## 期货Tick行情数据
----

获取全市场期货合约的Tick高频行情，当前不提供API方式获取，只提供csv网盘交付，近10年历史数据，一次性网盘拷贝（支持按交易所按日期定制），每天增量更新。tick行情属于单独的数据服务内容，不在积分权限范畴，有需求的用户请微信联系：waditu_a ，联系时请注明期货tick数据。

<br>
<br>

**数据字段内容说明**


字段 | 类型  | 中文含义 | 样例
---- | ----- | ---- | ----
InstrumentID   |     string     |     合约ID      |        cu2310
BidPrice1     |      float      |     买一价     |         68190.000000
BidVolume1 |         int      |       买一量      |        4 
AskPrice1     |      float      |     卖一价      |        68212.000000
AskVolume1  |        int    |         卖一量    |          2
LastPrice     |      float       |    最新价        |      68210.000000
Volume      |        int        |     成交量         |       3223
Turnover      |      float      |     成交金额    |        382577245.000000
OpenInterest   |     int      |       持仓量        |      203332.000000
UpperLimitPrice  |   float   |        涨停价     |         68210.000000
LowerLimitPrice  |   float     |      跌停价      |        62210.000000
OpenPrice       |    float      |     今开盘         |     68010.000000
PreSettlementPrice  | float    |       昨结算价     |       68110.000000
PreClosePrice  |     float       |    昨收盘价       |     68113.000000
PreOpenInterest  |   int       |      昨持仓量     |       3232343.000000
TradingDay     |     string      |    交易日期      |      20230925
UpdateTime   |       string    |      更新时间    |        10:00:00.500

<br>
<br>

**文件样例**

<img src='https://tushare.pro/files/web/ft_tick.png'>