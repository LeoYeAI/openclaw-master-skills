/**
 * ctp_bridge.cpp
 *
 * CTP C++ SDK → 简洁 C API 桥接实现
 * 支持平台：Windows x64 / macOS / Linux x64
 *
 * 编码说明：
 *   CTP 内部字符串均为 GBK，JSON 输出前转 UTF-8。
 *   Windows: Win32 MultiByteToWideChar / WideCharToMultiByte
 *   macOS / Linux: POSIX iconv
 */

#include "ctp_bridge.h"

// CTP headers are GBK-encoded; suppress encoding warnings per compiler
#ifdef _MSC_VER
#  pragma warning(push)
#  pragma warning(disable: 4828)
#endif
#include "ThostFtdcMdApi.h"
#include "ThostFtdcTraderApi.h"
#ifdef _MSC_VER
#  pragma warning(pop)
#endif

#ifdef _WIN32
#  include <windows.h>
#else
#  include <iconv.h>
#endif

#include <queue>
#include <mutex>
#include <condition_variable>
#include <string>
#include <sstream>
#include <cstring>
#include <cstdio>
#include <chrono>
#include <atomic>
#include <algorithm>
#include <vector>

/* ================================================================== */
/*  跨平台工具                                                          */
/* ================================================================== */

/**
 * 跨平台安全字符串拷贝（dst 须为数组，sizeof(dst) 需可求）
 * 等价于 MSVC strncpy_s 的 3-arg 模板形式。
 */
static inline void ctp_strcpy(char* dst, size_t dst_size, const char* src)
{
    if (!dst || dst_size == 0) return;
    strncpy(dst, src ? src : "", dst_size - 1);
    dst[dst_size - 1] = '\0';
}

/** GBK → UTF-8 */
static std::string gbk_to_utf8(const char* gbk)
{
    if (!gbk || !gbk[0]) return "";

#ifdef _WIN32
    int wlen = MultiByteToWideChar(936, 0, gbk, -1, nullptr, 0);
    if (wlen <= 0) return gbk;
    std::wstring ws(wlen, 0);
    MultiByteToWideChar(936, 0, gbk, -1, &ws[0], wlen);
    int ulen = WideCharToMultiByte(CP_UTF8, 0, ws.c_str(), -1, nullptr, 0, nullptr, nullptr);
    if (ulen <= 0) return gbk;
    std::string utf8(ulen, 0);
    WideCharToMultiByte(CP_UTF8, 0, ws.c_str(), -1, &utf8[0], ulen, nullptr, nullptr);
    if (!utf8.empty() && utf8.back() == '\0') utf8.pop_back();
    return utf8;
#else
    iconv_t cd = iconv_open("UTF-8", "GBK");
    if (cd == (iconv_t)-1) return gbk;           // iconv 不支持 GBK 时原样返回

    size_t in_len  = strlen(gbk);
    size_t out_cap = in_len * 4 + 4;
    std::string result(out_cap, '\0');

    char* in_ptr   = const_cast<char*>(gbk);
    char* out_ptr  = &result[0];
    size_t out_left = out_cap;

    size_t ret = iconv(cd, &in_ptr, &in_len, &out_ptr, &out_left);
    iconv_close(cd);

    if (ret == (size_t)-1) return gbk;
    result.resize(out_cap - out_left);
    return result;
#endif
}

/** JSON 字符串转义（双引号、反斜杠、换行） */
static std::string json_esc(const char* s)
{
    if (!s) return "";
    std::string r;
    for (; *s; ++s) {
        if      (*s == '"')  r += "\\\"";
        else if (*s == '\\') r += "\\\\";
        else if (*s == '\n') r += "\\n";
        else if (*s == '\r') r += "\\r";
        else r += *s;
    }
    return r;
}

static inline double safe_price(double p)
{
    // CTP 用 1.7976931348623158e+308 表示无效价格
    return (p > 1e30 || p < -1e30) ? 0.0 : p;
}

/* ================================================================== */
/*  逗号分隔字符串 → char* 数组                                         */
/* ================================================================== */
static std::vector<std::string> split_csv(const char* s)
{
    std::vector<std::string> v;
    if (!s || !s[0]) return v;
    std::istringstream ss(s);
    std::string tok;
    while (std::getline(ss, tok, ',')) {
        auto b = tok.find_first_not_of(" \t");
        auto e = tok.find_last_not_of(" \t");
        if (b != std::string::npos)
            v.push_back(tok.substr(b, e - b + 1));
    }
    return v;
}

/* ================================================================== */
/*  线程安全事件队列                                                     */
/* ================================================================== */
struct Event {
    int  type;
    char json[8192];
};

class EventQueue {
    std::queue<Event> q_;
    std::mutex        mu_;
    std::condition_variable cv_;
    static constexpr size_t MAXQ = 2000;
public:
    void push(int type, const std::string& json)
    {
        {
            std::lock_guard<std::mutex> lk(mu_);
            if (q_.size() >= MAXQ) q_.pop();   // overflow: drop oldest
            Event e;
            e.type = type;
            ctp_strcpy(e.json, sizeof(e.json), json.c_str());
            q_.push(e);
        }
        cv_.notify_one();
    }

    /** @return event type, 0=timeout */
    int poll(char* buf, int buf_size, int timeout_ms)
    {
        std::unique_lock<std::mutex> lk(mu_);
        if (q_.empty()) {
            if (timeout_ms == 0) return 0;
            auto dur = (timeout_ms < 0)
                ? std::chrono::milliseconds(24 * 3600 * 1000LL)
                : std::chrono::milliseconds(timeout_ms);
            cv_.wait_for(lk, dur, [this]{ return !q_.empty(); });
        }
        if (q_.empty()) return 0;
        Event e = q_.front(); q_.pop();
        ctp_strcpy(buf, buf_size, e.json);
        return e.type;
    }
};

/* ================================================================== */
/*  JSON 序列化辅助                                                     */
/* ================================================================== */

static std::string rsp_info_json(CThostFtdcRspInfoField* p)
{
    char buf[256];
    int eid = p ? p->ErrorID : 0;
    std::string emsg = p ? gbk_to_utf8(p->ErrorMsg) : "";
    snprintf(buf, sizeof(buf),
        R"("error_id":%d,"error_msg":"%s")",
        eid, json_esc(emsg.c_str()).c_str());
    return buf;
}

static std::string tick_json(CThostFtdcDepthMarketDataField* p)
{
    char buf[1024];
    snprintf(buf, sizeof(buf),
        R"({"instrument":"%s","trading_day":"%s","update_time":"%s",)"
        R"("update_ms":%d,"last":%.4f,"vol":%d,"turnover":%.2f,)"
        R"("open_interest":%.0f,"open":%.4f,"high":%.4f,"low":%.4f,)"
        R"("pre_close":%.4f,"upper_limit":%.4f,"lower_limit":%.4f,)"
        R"("bid1":%.4f,"bid1_vol":%d,"ask1":%.4f,"ask1_vol":%d})",
        p->InstrumentID,
        p->TradingDay,
        p->UpdateTime,
        p->UpdateMillisec,
        safe_price(p->LastPrice),
        p->Volume,
        p->Turnover,
        p->OpenInterest,
        safe_price(p->OpenPrice),
        safe_price(p->HighestPrice),
        safe_price(p->LowestPrice),
        safe_price(p->PreClosePrice),
        safe_price(p->UpperLimitPrice),
        safe_price(p->LowerLimitPrice),
        safe_price(p->BidPrice1),  p->BidVolume1,
        safe_price(p->AskPrice1),  p->AskVolume1);
    return buf;
}

static std::string order_json(CThostFtdcOrderField* p)
{
    char buf[1024];
    snprintf(buf, sizeof(buf),
        R"({"instrument":"%s","exchange":"%s","order_ref":"%s",)"
        R"("order_sys_id":"%s","front_id":%d,"session_id":%d,)"
        R"("direction":"%c","offset":"%c","price_type":"%c",)"
        R"("limit_price":%.4f,"volume_total":%d,"volume_traded":%d,)"
        R"("order_status":"%c","status_msg":"%s","insert_time":"%s",)"
        R"("trading_day":"%s"})",
        p->InstrumentID,
        p->ExchangeID,
        p->OrderRef,
        p->OrderSysID,
        p->FrontID,
        p->SessionID,
        p->Direction,
        p->CombOffsetFlag[0],
        p->OrderPriceType,
        safe_price(p->LimitPrice),
        p->VolumeTotalOriginal,
        p->VolumeTraded,
        p->OrderStatus,
        json_esc(gbk_to_utf8(p->StatusMsg).c_str()).c_str(),
        p->InsertTime,
        p->TradingDay);
    return buf;
}

static std::string trade_json(CThostFtdcTradeField* p)
{
    char buf[512];
    snprintf(buf, sizeof(buf),
        R"({"instrument":"%s","exchange":"%s","trade_id":"%s",)"
        R"("order_ref":"%s","order_sys_id":"%s",)"
        R"("direction":"%c","offset":"%c",)"
        R"("price":%.4f,"volume":%d,"trade_time":"%s","trading_day":"%s"})",
        p->InstrumentID,
        p->ExchangeID,
        p->TradeID,
        p->OrderRef,
        p->OrderSysID,
        p->Direction,
        p->OffsetFlag,
        p->Price,
        p->Volume,
        p->TradeTime,
        p->TradingDay);
    return buf;
}

static std::string position_json(CThostFtdcInvestorPositionField* p, bool is_last)
{
    char buf[512];
    snprintf(buf, sizeof(buf),
        R"({"instrument":"%s","direction":"%c","position":%d,)"
        R"("yd_position":%d,"open_volume":%d,"close_volume":%d,)"
        R"("position_profit":%.2f,"close_profit":%.2f,)"
        R"("open_cost":%.2f,"use_margin":%.2f,"is_last":%s})",
        p->InstrumentID,
        p->PosiDirection,
        p->Position,
        p->YdPosition,
        p->OpenVolume,
        p->CloseVolume,
        p->PositionProfit,
        p->CloseProfit,
        p->OpenCost,
        p->UseMargin,
        is_last ? "true" : "false");
    return buf;
}

static std::string account_json(CThostFtdcTradingAccountField* p)
{
    char buf[512];
    snprintf(buf, sizeof(buf),
        R"({"account_id":"%s","balance":%.2f,"available":%.2f,)"
        R"("margin":%.2f,"frozen_margin":%.2f,"commission":%.2f,)"
        R"("position_profit":%.2f,"close_profit":%.2f})",
        p->AccountID,
        p->Balance,
        p->Available,
        p->CurrMargin,
        p->FrozenMargin,
        p->Commission,
        p->PositionProfit,
        p->CloseProfit);
    return buf;
}

/* ================================================================== */
/*  Market Data SPI                                                     */
/* ================================================================== */

class MdSpi : public CThostFtdcMdSpi
{
public:
    EventQueue* q = nullptr;

    void OnFrontConnected() override {
        q->push(EVT_MD_FRONT_CONNECTED, R"({"event":"md_connected"})");
    }
    void OnFrontDisconnected(int reason) override {
        char buf[64];
        snprintf(buf, sizeof(buf), R"({"event":"md_disconnected","reason":%d})", reason);
        q->push(EVT_MD_FRONT_DISCONNECTED, buf);
    }
    void OnRspUserLogin(CThostFtdcRspUserLoginField* p,
                        CThostFtdcRspInfoField* info, int, bool) override {
        char buf[256];
        snprintf(buf, sizeof(buf),
            R"({"event":"md_login","trading_day":"%s",%s})",
            p ? p->TradingDay : "",
            rsp_info_json(info).c_str());
        q->push(EVT_MD_RSP_LOGIN, buf);
    }
    void OnRspSubMarketData(CThostFtdcSpecificInstrumentField* p,
                            CThostFtdcRspInfoField* info, int, bool) override {
        char buf[256];
        snprintf(buf, sizeof(buf),
            R"({"event":"md_subscribe","instrument":"%s",%s})",
            p ? p->InstrumentID : "",
            rsp_info_json(info).c_str());
        q->push(EVT_MD_RSP_SUBSCRIBE, buf);
    }
    void OnRtnDepthMarketData(CThostFtdcDepthMarketDataField* p) override {
        if (p) q->push(EVT_MD_TICK, tick_json(p));
    }
    void OnRspError(CThostFtdcRspInfoField* info, int, bool) override {
        char buf[256];
        snprintf(buf, sizeof(buf), R"({"event":"md_error",%s})", rsp_info_json(info).c_str());
        q->push(EVT_RSP_ERROR, buf);
    }
};

/* ================================================================== */
/*  Trader SPI                                                          */
/* ================================================================== */

class TdSpi : public CThostFtdcTraderSpi
{
public:
    EventQueue* q      = nullptr;
    int  front_id      = 0;
    int  session_id    = 0;

    void OnFrontConnected() override {
        q->push(EVT_FRONT_CONNECTED, R"({"event":"td_connected"})");
    }
    void OnFrontDisconnected(int reason) override {
        char buf[64];
        snprintf(buf, sizeof(buf), R"({"event":"td_disconnected","reason":%d})", reason);
        q->push(EVT_FRONT_DISCONNECTED, buf);
    }
    void OnRspAuthenticate(CThostFtdcRspAuthenticateField*,
                           CThostFtdcRspInfoField* info, int, bool) override {
        char buf[256];
        snprintf(buf, sizeof(buf), R"({"event":"authenticate",%s})", rsp_info_json(info).c_str());
        q->push(EVT_RSP_AUTHENTICATE, buf);
    }
    void OnRspUserLogin(CThostFtdcRspUserLoginField* p,
                        CThostFtdcRspInfoField* info, int, bool) override {
        if (p && (!info || info->ErrorID == 0)) {
            front_id   = p->FrontID;
            session_id = p->SessionID;
        }
        char buf[512];
        snprintf(buf, sizeof(buf),
            R"({"event":"td_login","trading_day":"%s","front_id":%d,"session_id":%d,"max_order_ref":"%s",%s})",
            p ? p->TradingDay : "",
            p ? p->FrontID : 0,
            p ? p->SessionID : 0,
            p ? p->MaxOrderRef : "",
            rsp_info_json(info).c_str());
        q->push(EVT_RSP_LOGIN, buf);
    }
    void OnRspUserLogout(CThostFtdcUserLogoutField*,
                         CThostFtdcRspInfoField* info, int, bool) override {
        char buf[128];
        snprintf(buf, sizeof(buf), R"({"event":"logout",%s})", rsp_info_json(info).c_str());
        q->push(EVT_RSP_LOGOUT, buf);
    }
    void OnRspSettlementInfoConfirm(CThostFtdcSettlementInfoConfirmField*,
                                    CThostFtdcRspInfoField* info, int, bool) override {
        char buf[128];
        snprintf(buf, sizeof(buf), R"({"event":"settle_confirm",%s})", rsp_info_json(info).c_str());
        q->push(EVT_RSP_SETTLE_CONFIRM, buf);
    }
    void OnRspOrderInsert(CThostFtdcInputOrderField* p,
                          CThostFtdcRspInfoField* info, int, bool) override {
        char buf[512];
        snprintf(buf, sizeof(buf),
            R"({"event":"order_insert_rsp","order_ref":"%s",%s})",
            p ? p->OrderRef : "",
            rsp_info_json(info).c_str());
        q->push(EVT_RSP_ORDER_INSERT, buf);
    }
    void OnRtnOrder(CThostFtdcOrderField* p) override {
        if (p) q->push(EVT_RTN_ORDER, order_json(p));
    }
    void OnRtnTrade(CThostFtdcTradeField* p) override {
        if (p) q->push(EVT_RTN_TRADE, trade_json(p));
    }
    void OnErrRtnOrderInsert(CThostFtdcInputOrderField* p,
                             CThostFtdcRspInfoField* info) override {
        char buf[512];
        snprintf(buf, sizeof(buf),
            R"({"event":"order_insert_err","order_ref":"%s",%s})",
            p ? p->OrderRef : "",
            rsp_info_json(info).c_str());
        q->push(EVT_ERR_ORDER_INSERT, buf);
    }
    void OnErrRtnOrderAction(CThostFtdcOrderActionField*,
                             CThostFtdcRspInfoField* info) override {
        char buf[256];
        snprintf(buf, sizeof(buf), R"({"event":"order_action_err",%s})", rsp_info_json(info).c_str());
        q->push(EVT_ERR_ORDER_ACTION, buf);
    }
    void OnRspQryInvestorPosition(CThostFtdcInvestorPositionField* p,
                                  CThostFtdcRspInfoField* info,
                                  int, bool is_last) override {
        if (!info || info->ErrorID == 0) {
            if (p) q->push(EVT_RSP_QRY_POSITION, position_json(p, is_last));
            else {
                // 空仓时 p==nullptr 且 is_last==true
                q->push(EVT_RSP_QRY_POSITION,
                    R"({"instrument":"","is_last":true,"position":0})");
            }
        } else {
            char buf[256];
            snprintf(buf, sizeof(buf), R"({"event":"qry_position_err",%s})",
                rsp_info_json(info).c_str());
            q->push(EVT_RSP_ERROR, buf);
        }
    }
    void OnRspQryTradingAccount(CThostFtdcTradingAccountField* p,
                                CThostFtdcRspInfoField* info,
                                int, bool) override {
        if (p && (!info || info->ErrorID == 0))
            q->push(EVT_RSP_QRY_ACCOUNT, account_json(p));
        else {
            char buf[256];
            snprintf(buf, sizeof(buf), R"({"event":"qry_account_err",%s})",
                rsp_info_json(info).c_str());
            q->push(EVT_RSP_ERROR, buf);
        }
    }
    void OnRspQryOrder(CThostFtdcOrderField* p,
                       CThostFtdcRspInfoField*, int, bool is_last) override {
        if (p) {
            auto js = order_json(p);
            js.pop_back();
            js += (is_last ? R"(,"is_last":true})" : R"(,"is_last":false})");
            q->push(EVT_RSP_QRY_ORDER, js);
        } else if (is_last) {
            q->push(EVT_RSP_QRY_ORDER, R"({"is_last":true})");
        }
    }
    void OnRspQryTrade(CThostFtdcTradeField* p,
                       CThostFtdcRspInfoField*, int, bool is_last) override {
        if (p) {
            auto js = trade_json(p);
            js.pop_back();
            js += (is_last ? R"(,"is_last":true})" : R"(,"is_last":false})");
            q->push(EVT_RSP_QRY_TRADE, js);
        } else if (is_last) {
            q->push(EVT_RSP_QRY_TRADE, R"({"is_last":true})");
        }
    }
    void OnRspError(CThostFtdcRspInfoField* info, int, bool) override {
        char buf[256];
        snprintf(buf, sizeof(buf), R"({"event":"error",%s})", rsp_info_json(info).c_str());
        q->push(EVT_RSP_ERROR, buf);
    }
};

/* ================================================================== */
/*  内部句柄结构                                                         */
/* ================================================================== */

struct MdContext {
    CThostFtdcMdApi* api = nullptr;
    MdSpi*           spi = nullptr;
    EventQueue       evq;
};

struct TdContext {
    CThostFtdcTraderApi* api = nullptr;
    TdSpi*               spi = nullptr;
    EventQueue           evq;
};

/* ================================================================== */
/*  Market Data API 实现                                                */
/* ================================================================== */

extern "C" {

CTPAPI CTP_MdHandle md_create(const char* flow_path)
{
    auto* ctx = new MdContext();
    ctx->spi = new MdSpi();
    ctx->spi->q = &ctx->evq;
    ctx->api = CThostFtdcMdApi::CreateFtdcMdApi(flow_path ? flow_path : "");
    return ctx;
}

CTPAPI void md_release(CTP_MdHandle h)
{
    auto* ctx = static_cast<MdContext*>(h);
    if (!ctx) return;
    if (ctx->api) { ctx->api->RegisterSpi(nullptr); ctx->api->Release(); }
    delete ctx->spi;
    delete ctx;
}

CTPAPI void md_register_front(CTP_MdHandle h, const char* front_addr)
{
    static_cast<MdContext*>(h)->api->RegisterFront(const_cast<char*>(front_addr));
}

CTPAPI void md_init(CTP_MdHandle h)
{
    auto* ctx = static_cast<MdContext*>(h);
    ctx->api->RegisterSpi(ctx->spi);
    ctx->api->Init();
}

CTPAPI int md_login(CTP_MdHandle h, const char* broker, const char* user,
                    const char* password, int req_id)
{
    auto* ctx = static_cast<MdContext*>(h);
    CThostFtdcReqUserLoginField req{};
    ctp_strcpy(req.BrokerID, sizeof(req.BrokerID), broker);
    ctp_strcpy(req.UserID,   sizeof(req.UserID),   user);
    ctp_strcpy(req.Password, sizeof(req.Password), password);
    return ctx->api->ReqUserLogin(&req, req_id);
}

CTPAPI int md_subscribe(CTP_MdHandle h, const char* instruments)
{
    auto* ctx = static_cast<MdContext*>(h);
    auto parts = split_csv(instruments);
    if (parts.empty()) return -1;
    std::vector<char*> ptrs;
    for (auto& s : parts) ptrs.push_back(const_cast<char*>(s.c_str()));
    return ctx->api->SubscribeMarketData(ptrs.data(), (int)ptrs.size());
}

CTPAPI int md_unsubscribe(CTP_MdHandle h, const char* instruments)
{
    auto* ctx = static_cast<MdContext*>(h);
    auto parts = split_csv(instruments);
    if (parts.empty()) return -1;
    std::vector<char*> ptrs;
    for (auto& s : parts) ptrs.push_back(const_cast<char*>(s.c_str()));
    return ctx->api->UnSubscribeMarketData(ptrs.data(), (int)ptrs.size());
}

CTPAPI int md_poll(CTP_MdHandle h, char* buf, int buf_size, int timeout_ms)
{
    return static_cast<MdContext*>(h)->evq.poll(buf, buf_size, timeout_ms);
}

CTPAPI const char* md_get_trading_day(CTP_MdHandle h)
{
    return static_cast<MdContext*>(h)->api->GetTradingDay();
}

CTPAPI const char* md_get_api_version()
{
    return CThostFtdcMdApi::GetApiVersion();
}

/* ================================================================== */
/*  Trader API 实现                                                     */
/* ================================================================== */

CTPAPI CTP_TdHandle td_create(const char* flow_path)
{
    auto* ctx = new TdContext();
    ctx->spi = new TdSpi();
    ctx->spi->q = &ctx->evq;
    ctx->api = CThostFtdcTraderApi::CreateFtdcTraderApi(flow_path ? flow_path : "");
    return ctx;
}

CTPAPI void td_release(CTP_TdHandle h)
{
    auto* ctx = static_cast<TdContext*>(h);
    if (!ctx) return;
    if (ctx->api) { ctx->api->RegisterSpi(nullptr); ctx->api->Release(); }
    delete ctx->spi;
    delete ctx;
}

CTPAPI void td_register_front(CTP_TdHandle h, const char* front_addr)
{
    static_cast<TdContext*>(h)->api->RegisterFront(const_cast<char*>(front_addr));
}

CTPAPI void td_init(CTP_TdHandle h)
{
    auto* ctx = static_cast<TdContext*>(h);
    ctx->api->SubscribePublicTopic(THOST_TERT_QUICK);
    ctx->api->SubscribePrivateTopic(THOST_TERT_QUICK);
    ctx->api->RegisterSpi(ctx->spi);
    ctx->api->Init();
}

CTPAPI int td_authenticate(CTP_TdHandle h, const char* broker, const char* user,
                            const char* app_id, const char* auth_code, int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcReqAuthenticateField req{};
    ctp_strcpy(req.BrokerID, sizeof(req.BrokerID), broker);
    ctp_strcpy(req.UserID,   sizeof(req.UserID),   user);
    ctp_strcpy(req.AppID,    sizeof(req.AppID),    app_id);
    ctp_strcpy(req.AuthCode, sizeof(req.AuthCode), auth_code);
    return ctx->api->ReqAuthenticate(&req, req_id);
}

CTPAPI int td_login(CTP_TdHandle h, const char* broker, const char* user,
                    const char* password, int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcReqUserLoginField req{};
    ctp_strcpy(req.BrokerID, sizeof(req.BrokerID), broker);
    ctp_strcpy(req.UserID,   sizeof(req.UserID),   user);
    ctp_strcpy(req.Password, sizeof(req.Password), password);
#ifdef __APPLE__
    // macOS SDK 6.7.7 adds length + systemInfo parameters; pass empty values
    TThostFtdcClientSystemInfoType sysinfo{};
    return ctx->api->ReqUserLogin(&req, req_id, 0, sysinfo);
#else
    return ctx->api->ReqUserLogin(&req, req_id);
#endif
}

CTPAPI int td_settle_confirm(CTP_TdHandle h, const char* broker,
                              const char* investor, int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcSettlementInfoConfirmField req{};
    ctp_strcpy(req.BrokerID,   sizeof(req.BrokerID),   broker);
    ctp_strcpy(req.InvestorID, sizeof(req.InvestorID), investor);
    return ctx->api->ReqSettlementInfoConfirm(&req, req_id);
}

CTPAPI int td_order_insert(CTP_TdHandle h,
                            const char* broker, const char* investor,
                            const char* exchange, const char* instrument,
                            const char* order_ref,
                            char direction, char offset,
                            char price_type, double limit_price, int volume,
                            char time_cond, char vol_cond,
                            int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcInputOrderField req{};

    ctp_strcpy(req.BrokerID,     sizeof(req.BrokerID),     broker);
    ctp_strcpy(req.InvestorID,   sizeof(req.InvestorID),   investor);
    ctp_strcpy(req.ExchangeID,   sizeof(req.ExchangeID),   exchange);
    ctp_strcpy(req.InstrumentID, sizeof(req.InstrumentID), instrument);
    ctp_strcpy(req.OrderRef,     sizeof(req.OrderRef),     order_ref);

    req.Direction            = direction;
    req.CombOffsetFlag[0]    = offset;
    req.CombHedgeFlag[0]     = THOST_FTDC_HF_Speculation;
    req.OrderPriceType       = price_type;
    req.LimitPrice           = limit_price;
    req.VolumeTotalOriginal  = volume;
    req.TimeCondition        = time_cond;
    req.VolumeCondition      = vol_cond;
    req.MinVolume            = 1;
    req.ContingentCondition  = THOST_FTDC_CC_Immediately;
    req.ForceCloseReason     = THOST_FTDC_FCC_NotForceClose;
    req.IsAutoSuspend        = 0;
    req.UserForceClose       = 0;
    req.RequestID            = req_id;

    return ctx->api->ReqOrderInsert(&req, req_id);
}

CTPAPI int td_order_cancel_by_sysid(CTP_TdHandle h,
                                     const char* broker, const char* investor,
                                     const char* exchange, const char* instrument,
                                     const char* order_sys_id, int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcInputOrderActionField req{};
    ctp_strcpy(req.BrokerID,     sizeof(req.BrokerID),     broker);
    ctp_strcpy(req.InvestorID,   sizeof(req.InvestorID),   investor);
    ctp_strcpy(req.ExchangeID,   sizeof(req.ExchangeID),   exchange);
    ctp_strcpy(req.InstrumentID, sizeof(req.InstrumentID), instrument);
    ctp_strcpy(req.OrderSysID,   sizeof(req.OrderSysID),   order_sys_id);
    req.ActionFlag = THOST_FTDC_AF_Delete;
    req.RequestID  = req_id;
    return ctx->api->ReqOrderAction(&req, req_id);
}

CTPAPI int td_order_cancel_by_ref(CTP_TdHandle h,
                                   const char* broker, const char* investor,
                                   const char* exchange, const char* instrument,
                                   const char* order_ref, int front_id,
                                   int session_id, int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcInputOrderActionField req{};
    ctp_strcpy(req.BrokerID,     sizeof(req.BrokerID),     broker);
    ctp_strcpy(req.InvestorID,   sizeof(req.InvestorID),   investor);
    ctp_strcpy(req.ExchangeID,   sizeof(req.ExchangeID),   exchange);
    ctp_strcpy(req.InstrumentID, sizeof(req.InstrumentID), instrument);
    ctp_strcpy(req.OrderRef,     sizeof(req.OrderRef),     order_ref);
    req.FrontID    = front_id;
    req.SessionID  = session_id;
    req.ActionFlag = THOST_FTDC_AF_Delete;
    req.RequestID  = req_id;
    return ctx->api->ReqOrderAction(&req, req_id);
}

CTPAPI int td_qry_position(CTP_TdHandle h, const char* broker,
                            const char* investor, const char* instrument, int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcQryInvestorPositionField req{};
    ctp_strcpy(req.BrokerID,   sizeof(req.BrokerID),   broker);
    ctp_strcpy(req.InvestorID, sizeof(req.InvestorID), investor);
    if (instrument && instrument[0])
        ctp_strcpy(req.InstrumentID, sizeof(req.InstrumentID), instrument);
    return ctx->api->ReqQryInvestorPosition(&req, req_id);
}

CTPAPI int td_qry_account(CTP_TdHandle h, const char* broker,
                           const char* investor, int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcQryTradingAccountField req{};
    ctp_strcpy(req.BrokerID,  sizeof(req.BrokerID),  broker);
    ctp_strcpy(req.AccountID, sizeof(req.AccountID), investor);
    return ctx->api->ReqQryTradingAccount(&req, req_id);
}

CTPAPI int td_qry_order(CTP_TdHandle h, const char* broker,
                         const char* investor, const char* instrument, int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcQryOrderField req{};
    ctp_strcpy(req.BrokerID,   sizeof(req.BrokerID),   broker);
    ctp_strcpy(req.InvestorID, sizeof(req.InvestorID), investor);
    if (instrument && instrument[0])
        ctp_strcpy(req.InstrumentID, sizeof(req.InstrumentID), instrument);
    return ctx->api->ReqQryOrder(&req, req_id);
}

CTPAPI int td_qry_trade(CTP_TdHandle h, const char* broker,
                         const char* investor, const char* instrument, int req_id)
{
    auto* ctx = static_cast<TdContext*>(h);
    CThostFtdcQryTradeField req{};
    ctp_strcpy(req.BrokerID,   sizeof(req.BrokerID),   broker);
    ctp_strcpy(req.InvestorID, sizeof(req.InvestorID), investor);
    if (instrument && instrument[0])
        ctp_strcpy(req.InstrumentID, sizeof(req.InstrumentID), instrument);
    return ctx->api->ReqQryTrade(&req, req_id);
}

CTPAPI int td_poll(CTP_TdHandle h, char* buf, int buf_size, int timeout_ms)
{
    return static_cast<TdContext*>(h)->evq.poll(buf, buf_size, timeout_ms);
}

CTPAPI int td_get_front_id(CTP_TdHandle h)
{
    return static_cast<TdContext*>(h)->spi->front_id;
}

CTPAPI int td_get_session_id(CTP_TdHandle h)
{
    return static_cast<TdContext*>(h)->spi->session_id;
}

CTPAPI const char* td_get_trading_day(CTP_TdHandle h)
{
    return static_cast<TdContext*>(h)->api->GetTradingDay();
}

} // extern "C"
