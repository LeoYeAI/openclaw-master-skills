from .common import ObjDataType


class AccountData(object):
    """账户数据类"""

    def __init__(self, data: ObjDataType = {}) -> None:
        self._investor = data.get("InvestorID", "")
        self._account = data.get("AccountID", "")
        self._balance = data.get("Balance", 0.0)
        self._pre_balance = data.get("PreBalance", 0.0)
        self._available = data.get("Available", 0.0)
        self._pre_available = data.get("PreAvailable", 0.0)
        self._close_profit = data.get("CloseProfit", 0.0)
        self._position_profit = data.get("PositionProfit", 0.0)
        self._dynamic_rights = data.get("DynamicRights", 0.0)
        self._commission = data.get("Fee", 0.0)
        self._margin = data.get("Margin", 0.0)
        self._frozen_margin = data.get("FrozenMargin", 0.0)
        self._deposit = data.get("Deposit", 0.0)
        self._withdraw = data.get("Withdraw", 0.0)

    def __repr__(self) -> str:
        return str(
            {
                "investor": self._investor,
                "account": self._account,
                "balance": self._balance,
                "pre_balance": self._pre_balance,
                "available": self._available,
                "pre_available": self._pre_available,
                "close_profit": self._close_profit,
                "position_profit": self._position_profit,
                "dynamic_rights": self._dynamic_rights,
                "commission": self._commission,
                "margin": self._margin,
                "frozen_margin": self._frozen_margin,
                "deposit": self._deposit,
                "withdraw": self._withdraw,
            }
        )

    @property
    def investor(self) -> str:
        """投资者账号"""
        return self._investor

    @property
    def account(self) -> str:
        """资金账号"""
        return self._account

    @property
    def balance(self) -> float:
        """结算准备金"""
        return self._balance

    @property
    def pre_balance(self) -> float:
        """上次结算准备金"""
        return self._pre_balance

    @property
    def available(self) -> float:
        """可用资金"""
        return self._available

    @property
    def pre_available(self) -> float:
        """上日可用资金"""
        return self._pre_available

    @property
    def close_profit(self) -> float:
        """平仓盈亏"""
        return self._close_profit

    @property
    def position_profit(self) -> float:
        """持仓盈亏"""
        return self._position_profit

    @property
    def dynamic_rights(self) -> float:
        """动态权益"""
        return self._dynamic_rights

    @property
    def commission(self) -> float:
        """手续费"""
        return self._commission

    @property
    def margin(self) -> float:
        """占用保证金"""
        return self._margin

    @property
    def frozen_margin(self) -> float:
        """冻结保证金"""
        return self._frozen_margin

    @property
    def risk(self) -> float:
        """风险度"""
        return self._margin / self._dynamic_rights

    @property
    def deposit(self) -> float:
        """入金金额"""
        return self._deposit

    @property
    def withdraw(self) -> float:
        """出金金额"""
        return self._withdraw
