from .common import ObjDataType


class InvestorData(object):
    """投资者数据"""

    def __init__(self, data: ObjDataType = {}) -> None:
        self._broker_id = data.get("BrokerID", "")
        self._investor_id = data.get("InvestorID", "")
        self._user_id = data.get("UserID", "")

    def __repr__(self) -> str:
        return str(
            {
                "broker_id": self._broker_id,
                "investor_id": self._investor_id,
                "user_id": self._user_id,
            }
        )

    @property
    def broker_id(self) -> str:
        """经纪公司编号"""
        return self._broker_id

    @property
    def investor_id(self) -> str:
        """投资者账号"""
        return self._investor_id

    @property
    def user_id(self) -> str:
        """登录账号"""
        return self._user_id
