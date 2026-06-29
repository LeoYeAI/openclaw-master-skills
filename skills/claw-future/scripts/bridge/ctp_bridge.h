/**
 * ctp_bridge.h
 *
 * C API bridge over CTP C++ SDK (ThostFtdcTraderApi / ThostFtdcMdApi).
 *
 * Design: 所有 CTP C++ 虚函数回调均通过内部事件队列异步化，
 *         Python 侧通过 md_poll / td_poll 轮询拿 JSON 事件，无需 GIL 处理。
 *
 * Build (Windows): Visual Studio 2019+，x64
 *   cl /LD /O2 /MD /std:c++17 ctp_bridge.cpp ...
 *
 * Build (macOS): Xcode Command Line Tools + clang++
 *   clang++ -shared -fPIC -std=c++17 -o libctp_bridge.dylib ctp_bridge.cpp ...
 */

#pragma once

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
#  ifdef CTPBRIDGE_EXPORTS
#    define CTPAPI __declspec(dllexport)
#  else
#    define CTPAPI __declspec(dllimport)
#  endif
#else
#  ifdef CTPBRIDGE_EXPORTS
#    define CTPAPI __attribute__((visibility("default")))
#  else
#    define CTPAPI
#  endif
#endif

/* ------------------------------------------------------------------ */
/*  Event type constants — returned by md_poll / td_poll               */
/* ------------------------------------------------------------------ */

/* Trader events */
#define EVT_FRONT_CONNECTED        1
#define EVT_FRONT_DISCONNECTED     2
#define EVT_RSP_AUTHENTICATE       3
#define EVT_RSP_LOGIN              4
#define EVT_RSP_LOGOUT             5
#define EVT_RSP_SETTLE_CONFIRM     6
#define EVT_RSP_ORDER_INSERT       7   /* order rejected by front */
#define EVT_RTN_ORDER              8   /* order state change */
#define EVT_RTN_TRADE              9   /* fill */
#define EVT_ERR_ORDER_INSERT      10
#define EVT_ERR_ORDER_ACTION      11
#define EVT_RSP_QRY_POSITION      12
#define EVT_RSP_QRY_ACCOUNT       13
#define EVT_RSP_QRY_ORDER         14
#define EVT_RSP_QRY_TRADE         15
#define EVT_RSP_ERROR             16

/* Market data events */
#define EVT_MD_FRONT_CONNECTED   101
#define EVT_MD_FRONT_DISCONNECTED 102
#define EVT_MD_RSP_LOGIN         103
#define EVT_MD_RSP_SUBSCRIBE     104
#define EVT_MD_TICK              105   /* depth market data */

/* ------------------------------------------------------------------ */
/*  Opaque handles                                                      */
/* ------------------------------------------------------------------ */
typedef void* CTP_MdHandle;
typedef void* CTP_TdHandle;

/* ------------------------------------------------------------------ */
/*  Market Data API                                                     */
/* ------------------------------------------------------------------ */

/** 创建行情实例。flow_path: 流文件目录（空串=当前目录） */
CTPAPI CTP_MdHandle md_create(const char* flow_path);
CTPAPI void         md_release(CTP_MdHandle h);
CTPAPI void         md_register_front(CTP_MdHandle h, const char* front_addr);
CTPAPI void         md_init(CTP_MdHandle h);

/** 登录行情服务器 */
CTPAPI int  md_login(CTP_MdHandle h,
                     const char* broker_id,
                     const char* user_id,
                     const char* password,
                     int req_id);

/** instruments: 逗号分隔的合约代码，如 "IF2505,rb2510" */
CTPAPI int  md_subscribe(CTP_MdHandle h, const char* instruments);
CTPAPI int  md_unsubscribe(CTP_MdHandle h, const char* instruments);

/**
 * 轮询一条事件。
 * @param buf       写入 JSON 字符串的缓冲区
 * @param buf_size  缓冲区大小（建议 8192）
 * @param timeout_ms 超时毫秒数（0=立即返回，-1=无限等待）
 * @return 事件类型常量，0 表示超时无事件，<0 表示错误
 */
CTPAPI int  md_poll(CTP_MdHandle h, char* buf, int buf_size, int timeout_ms);

CTPAPI const char* md_get_trading_day(CTP_MdHandle h);
CTPAPI const char* md_get_api_version();

/* ------------------------------------------------------------------ */
/*  Trader API                                                          */
/* ------------------------------------------------------------------ */

CTPAPI CTP_TdHandle td_create(const char* flow_path);
CTPAPI void         td_release(CTP_TdHandle h);
CTPAPI void         td_register_front(CTP_TdHandle h, const char* front_addr);
CTPAPI void         td_init(CTP_TdHandle h);

/** 客户端认证（SimNow 也需要） */
CTPAPI int  td_authenticate(CTP_TdHandle h,
                             const char* broker_id,
                             const char* user_id,
                             const char* app_id,
                             const char* auth_code,
                             int req_id);

/** 登录 */
CTPAPI int  td_login(CTP_TdHandle h,
                     const char* broker_id,
                     const char* user_id,
                     const char* password,
                     int req_id);

/** 确认结算单（每日第一次必须调用） */
CTPAPI int  td_settle_confirm(CTP_TdHandle h,
                               const char* broker_id,
                               const char* investor_id,
                               int req_id);

/**
 * 报单
 * @param direction    '0'=买  '1'=卖
 * @param offset       '0'=开  '1'=平  '3'=平今  '4'=平昨
 * @param price_type   '1'=限价  '2'=市价(任意价)
 * @param limit_price  市价时传 0
 * @param time_cond    '3'=GFD(当日有效)  '1'=IOC
 * @param vol_cond     '1'=任何数量  '2'=全部成交
 */
CTPAPI int  td_order_insert(CTP_TdHandle h,
                             const char* broker_id,
                             const char* investor_id,
                             const char* exchange_id,
                             const char* instrument_id,
                             const char* order_ref,    /* 客户端自编报单引用 */
                             char direction,
                             char offset,
                             char price_type,
                             double limit_price,
                             int volume,
                             char time_cond,
                             char vol_cond,
                             int req_id);

/**
 * 撤单（通过 OrderSysID 撤）
 * order_sys_id: OnRtnOrder 中的 OrderSysID
 */
CTPAPI int  td_order_cancel_by_sysid(CTP_TdHandle h,
                                      const char* broker_id,
                                      const char* investor_id,
                                      const char* exchange_id,
                                      const char* instrument_id,
                                      const char* order_sys_id,
                                      int req_id);

/**
 * 撤单（通过 FrontID+SessionID+OrderRef 撤）
 */
CTPAPI int  td_order_cancel_by_ref(CTP_TdHandle h,
                                    const char* broker_id,
                                    const char* investor_id,
                                    const char* exchange_id,
                                    const char* instrument_id,
                                    const char* order_ref,
                                    int front_id,
                                    int session_id,
                                    int req_id);

/** 查持仓（instrument_id 为空串查全部） */
CTPAPI int  td_qry_position(CTP_TdHandle h,
                              const char* broker_id,
                              const char* investor_id,
                              const char* instrument_id,
                              int req_id);

/** 查资金账户 */
CTPAPI int  td_qry_account(CTP_TdHandle h,
                             const char* broker_id,
                             const char* investor_id,
                             int req_id);

/** 查当日委托 */
CTPAPI int  td_qry_order(CTP_TdHandle h,
                          const char* broker_id,
                          const char* investor_id,
                          const char* instrument_id,
                          int req_id);

/** 查当日成交 */
CTPAPI int  td_qry_trade(CTP_TdHandle h,
                          const char* broker_id,
                          const char* investor_id,
                          const char* instrument_id,
                          int req_id);

CTPAPI int  td_poll(CTP_TdHandle h, char* buf, int buf_size, int timeout_ms);

CTPAPI int         td_get_front_id(CTP_TdHandle h);
CTPAPI int         td_get_session_id(CTP_TdHandle h);
CTPAPI const char* td_get_trading_day(CTP_TdHandle h);

#ifdef __cplusplus
}
#endif
