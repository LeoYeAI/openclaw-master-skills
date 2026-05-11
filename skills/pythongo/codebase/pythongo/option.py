import bisect
import math
from collections import defaultdict
from typing import Any, Callable, Literal, Optional, TypedDict

import numpy as np

from pythongo import infini
from pythongo.classdef import InstrumentData


def calculate_once(method):
    """初始化"""

    def wrapper(self, *args, **kwargs):
        if not getattr(self, "_crr_calculated", False) and method.__name__.startswith(
            "crr_"
        ):
            self.crr_price()
            setattr(self, "_crr_calculated", True)
        elif not getattr(self, "_baw_calculated", False) and method.__name__.startswith(
            "baw_"
        ):
            self._baw_simulate(self.sigma)
            setattr(self, "_baw_calculated", True)
        return method(self, *args, **kwargs)

    return wrapper


class Option(object):
    """
    期权常见函数方法

    Args:
        option_type: 看涨期权 CALL；看跌期权 PUT
        underlying_price: 标的当前价格
        strike_price: 执行价
        time_to_expire: 距离到期日剩余时间，以年计算，例如，还剩下 32 天，即 32 / 365
        risk_free: 无风险利率
        market_price: 期权当前市场价格
        dividend_rate: 股息率
        sigma: 波动率，默认为 0 后续希腊值使用 BSM 计算的 IV 进行计算

    Note:
        内置 BSM、BAW、CRR 三种算法，可自行选择
        输入的市场价格会被贴现
    """

    def __init__(
        self,
        option_type: Literal["CALL", "PUT"],
        underlying_price: float,
        strike_price: float,
        time_to_expire: float,
        risk_free: float,
        market_price: float,
        dividend_rate: float,
        init_sigma: float = 0.0,
    ) -> None:
        self.underlying_price: float = underlying_price
        self.strike_price: float = strike_price
        self.time_to_expire: float = time_to_expire
        self.risk_free: float = risk_free
        self.dividend_rate: float = dividend_rate

        self._crr_value: list[float] = []
        self._crr_n: int = 1000
        self.sigma_default: float = 0.8

        self.market_price: float = market_price / self.disc
        self.option_type_sign: float = option_type
        self.sigma: float = init_sigma

    @property
    def option_type_sign(self) -> float:
        return self._option_type_sign

    @option_type_sign.setter
    def option_type_sign(self, option_type: Literal["CALL", "PUT"]) -> float:
        if option_type in ["CALL", "PUT"]:
            self._option_type_sign = 1.0 if option_type == "CALL" else -1.0
        else:
            raise ValueError("只能填入 CALL 或 PUT，大小写也要一致")

    @property
    def crr_n(self) -> int:
        """二叉树节点数量"""
        return self._crr_n

    @crr_n.setter
    def crr_n(self, notes: int) -> None:
        if notes <= 0:
            raise ValueError("节点数要大于 0")
        self._crr_n: int = notes

    @property
    def sigma(self) -> float:
        return self._sigma

    @sigma.setter
    def sigma(self, val: float) -> float:
        if val > 0:
            self._sigma = val
        else:
            self._sigma = self.bs_iv()

    @property
    def sigma_default(self) -> float:
        """无法计算出 sigma 时的默认值"""
        return self._sigma_default

    @sigma_default.setter
    def sigma_default(self, val: float) -> float:
        if val <= 0:
            raise ValueError("波动率要大于 0")
        self._sigma_default: float = val

    def equal_price(self, val_1: float, rel_tol: float) -> bool:
        return math.isclose(val_1, self.market_price, rel_tol=rel_tol)

    @property
    def d_1(self) -> float:
        return self._calculate_d_1(self.underlying_price, self.sigma)

    def _calculate_d_1(self, underlying_price: float, sigma: float) -> float:
        ln_p = math.log(underlying_price / self.strike_price)
        sigma_t = sigma * math.sqrt(self.time_to_expire)
        r_q = self.risk_free - self.dividend_rate
        return (ln_p + (r_q + 0.5 * sigma**2) * self.time_to_expire) / sigma_t

    @property
    def d_2(self) -> float:
        return self._calculate_d_2(self.d_1, self.sigma)

    def _calculate_d_2(self, d_1: float, sigma: float) -> float:
        return d_1 - sigma * math.sqrt(self.time_to_expire)

    def _calculate_d_i(self, d: float) -> float:
        return (1 / math.sqrt(2 * math.pi)) * math.exp((-(d**2)) / 2)

    def _calculate_n_d(self, d: float) -> float:
        """计算 N(d)"""
        return self.option_type_sign * self.cdf_normal(self.option_type_sign * d)

    @property
    def disc_q(self) -> float:
        return math.exp(-self.dividend_rate * self.time_to_expire)

    @property
    def s_t(self) -> float:
        return self._calculate_s_t(self.underlying_price)

    def _calculate_s_t(self, underlying_price: float) -> float:
        """计算 s_t"""
        return underlying_price * self.disc_q

    @property
    def disc(self) -> float:
        return math.exp(-self.risk_free * self.time_to_expire)

    @property
    def sigma_t(self) -> float:
        return self.sigma * math.sqrt(self.time_to_expire)

    def bs_iv(self) -> float:
        """二分法计算隐含波动率"""
        return self.binary_search(
            max_guess=2,
            min_guess=1e-5,
            min_precision=1e-7,
            price_func=self._calculate_bs_price
        )

    def baw_iv(self) -> float:
        """二分法计算美式期权隐含波动率"""
        return self.binary_search(
            max_guess=2,
            min_guess=1e-5,
            min_precision=1e-7,
            price_func=self._baw_price_pre
        )

    def bs_price(self) -> float:
        return self._calculate_bs_price(self.sigma, self.underlying_price)

    def _calculate_bs_price(self, sigma: float, underlying_price: float) -> float:
        """计算 BS 公式下期权理论价格"""
        s_t = self._calculate_s_t(underlying_price)
        d_1 = self._calculate_d_1(underlying_price, sigma)
        d_2 = self._calculate_d_2(d_1, sigma)

        n_d_1 = self._calculate_n_d(d_1)
        n_d_2 = self._calculate_n_d(d_2)

        bs_price = (
            s_t * n_d_1
            - self.strike_price
            * math.exp(-self.risk_free * self.time_to_expire)
            * n_d_2
        )
        return bs_price

    def cdf_normal(self, x: float) -> float:
        z = x / math.sqrt(2)
        return 0.5 * (1 + math.erf(z))

    def bs_delta(self) -> float:
        n_d_1 = self._calculate_n_d(self.d_1)
        return n_d_1 * self.disc_q

    def bs_gamma(self) -> float:
        d_1_1 = self._calculate_d_i(self.d_1)
        return self.disc_q * d_1_1 / (self.underlying_price * self.sigma_t)

    def bs_vega(self) -> float:
        d_1_1 = self._calculate_d_i(self.d_1)
        vega = self.s_t * math.sqrt(self.time_to_expire) * d_1_1
        return vega / 100

    def bs_theta(self) -> float:
        """折合为每天的时间损耗率"""
        d_1_1 = self._calculate_d_i(self.d_1)
        n_d_1 = self._calculate_n_d(self.d_1)
        n_d_2 = self._calculate_n_d(self.d_2)

        year_theta = (
            (-self.s_t * d_1_1 * self.sigma) / (2 * math.sqrt(self.time_to_expire))
            - self.risk_free * n_d_2 * self.strike_price * self.disc
            + self.dividend_rate * n_d_1 * self.s_t
        )

        return year_theta / 365

    def bs_rho(self) -> float:
        n_d_2 = self._calculate_n_d(self.d_2)
        rho = self.strike_price * self.time_to_expire * self.disc * n_d_2
        return rho / 100

    def bs_rho_q(self) -> float:
        n_d_1 = self._calculate_n_d(self.d_1)
        rho_q = self.s_t * self.time_to_expire * n_d_1
        return rho_q / 100

    def bs_vanna(self) -> float:
        d_1_1 = self._calculate_d_i(self.d_1)
        return -self.disc_q * d_1_1 * self.d_2 / self.sigma

    def _crr_m(self) -> list[float]:
        """无息标的的二叉树美式期权定价模型"""
        crr_n = self.crr_n
        dt = self.time_to_expire / crr_n
        u = math.exp(self.sigma * math.sqrt(dt))
        d = 1.0 / u
        a = math.exp(self.risk_free * dt)
        p = (a - d) / (u - d)
        q = 1.0 - p

        s_t = (
            self.underlying_price
            * d ** np.arange(crr_n, -1, -1)
            * u ** np.arange(0, crr_n + 1)
        )
        value = np.maximum(self.option_type_sign * (s_t - self.strike_price), 0)

        for _ in range(crr_n - 1, -1, -1):
            value[:-1] = math.exp(-self.risk_free * dt) * (
                p * value[1:] + q * value[:-1]
            )
            s_t = s_t * u
            value = np.maximum(self.option_type_sign * (s_t - self.strike_price), value)

        return value.tolist()

    def crr_price(self) -> float:
        """定价价格"""
        if not self._crr_value:
            self._crr_value = self._crr_m()
        return self._crr_value[0]

    @calculate_once
    def crr_delta(self) -> float:
        """delta"""
        delta = (self._crr_value[2] - self._crr_value[1]) / (
            self.underlying_price
            * (
                math.exp(self.sigma * math.sqrt(self.time_to_expire / self.crr_n))
                - 1 / math.exp(self.sigma * math.sqrt(self.time_to_expire / self.crr_n))
            )
        )
        return delta

    @calculate_once
    def crr_gamma(self) -> float:
        """gamma"""
        dt_sqrt = math.sqrt(self.time_to_expire / self.crr_n)
        exp_sigma = math.exp(self.sigma * dt_sqrt)

        temp1 = exp_sigma**2 - (1 / exp_sigma) ** 2
        temp2 = self.underlying_price * exp_sigma**2 - self.underlying_price
        temp3 = self.underlying_price - self.underlying_price * (1 / exp_sigma) ** 2
        h = 0.5 * self.underlying_price * temp1

        change = abs((self._crr_value[5] - self._crr_value[4]) / temp2) - abs(
            (self._crr_value[4] - self._crr_value[3]) / temp3
        )

        return self.option_type_sign * change / h

    @calculate_once
    def crr_vega(self) -> float:
        """vega"""
        f = self._crr_value[0]
        self.sigma += 0.01

        f_change = self._crr_m()[0]
        vega = (f_change - f) * 100

        self.sigma -= 0.01

        return vega / 100

    @calculate_once
    def crr_theta(self) -> float:
        """theta"""
        f = self._crr_value[0]
        self.time_to_expire -= 1 / 365

        f_change = self._crr_m()[0]
        theta = f_change - f
        self.time_to_expire += 1 / 365

        return theta

    @calculate_once
    def crr_rho(self) -> float:
        """rho"""
        f = self._crr_value[0]
        self.risk_free += 0.01

        f_change = self._crr_m()[0]
        rho = (f_change - f) * 100
        self.risk_free -= 0.01

        return rho / 100

    def _baw_func(self, underlying_price: float) -> float:
        """定价模型方程"""
        start_n_d_1 = self.cdf_normal(
            self.option_type_sign * self._calculate_d_1(underlying_price, self.sigma)
        )
        american_option_premium = self._american_option_premium(
            star=underlying_price, sigma=self.sigma
        )

        value_1 = (
            self._calculate_bs_price(self.sigma, underlying_price)
            + american_option_premium
        )
        value_2 = (1 - self.disc_q * start_n_d_1) * self.option_type_sign

        option_init = (underlying_price - self.strike_price) * self.option_type_sign

        return (value_1 + value_2 * underlying_price / self._q - option_init) ** 2

    def _baw_simulate(self, sigma: float):
        """定价模型方程求解"""
        self._q = self._calculate_q(sigma=sigma)
        self._star = self.find_minimum(self._baw_func, self.underlying_price)

    def _american_option_premium(self, star: float, sigma: float) -> float:
        """美式期权溢价"""
        cal_a = self._A(star, sigma)
        log_ratio = self._q * math.log(self.underlying_price / star)
        return cal_a * math.exp(log_ratio)

    def _baw_price_pre(self, sigma: float, underlying_price: float) -> float:
        self._baw_simulate(sigma)

        american_option_premium = self._american_option_premium(
            star=self._star, sigma=sigma
        )
        baw_price_pre = (
            self._calculate_bs_price(sigma, underlying_price) + american_option_premium
        )
        option_value = self.option_type_sign * (underlying_price - self.strike_price)

        check_sign = (
            underlying_price * self.option_type_sign
            < self._star * self.option_type_sign
        )

        return baw_price_pre if check_sign else option_value

    def baw_price(self) -> float:
        """美式期权定价模型"""
        return self._baw_price_pre(self.sigma, self.underlying_price)

    def _A(self, underlying_price: float, sigma: float) -> float:
        """计算美式期权溢价系数 A"""
        d_1 = self._calculate_d_1(underlying_price, sigma)
        start_n_d_1 = self.cdf_normal(self.option_type_sign * d_1)
        temp = 1 - self.disc_q * start_n_d_1

        return self.option_type_sign * temp * underlying_price / self._q

    def _calculate_q(self, sigma: float) -> float:
        "计算美式期权溢价系数 q"
        parm_m = 2 * self.risk_free / sigma**2
        parm_n = 2 * (self.risk_free - self.dividend_rate) / sigma**2
        parm_x = 1 - self.disc

        temp1 = 4 * parm_m / parm_x if self.risk_free > 0 else 0
        temp2 = parm_n - 1

        return 0.5 * self.option_type_sign * (-temp2 + math.sqrt(temp2**2 + temp1))

    @calculate_once
    def baw_delta(self) -> float:
        """baw 美式期权定价模型 delta"""
        return self.bs_delta() + self._A(self._star, self.sigma) / self._star

    @calculate_once
    def baw_gamma(self) -> float:
        """baw 美式期权定价模型 gamma"""
        return self.bs_gamma() + self._A(self._star, self.sigma) * (self._q - 1) / (
            self.underlying_price * self._star * self._q
        )

    def baw_vega(self) -> float:
        """baw 美式期权定价模型 vega"""
        f = self.baw_price()
        self.sigma += 0.01

        f_change = self.baw_price()
        vega = f_change - f
        self.sigma -= 0.01

        return vega

    def baw_theta(self) -> float:
        """baw 美式期权定价模型 theta, 日度"""
        f = self.baw_price()
        self.time_to_expire -= 1.0 / 365

        f_change = self.baw_price()
        theta = f_change - f
        self.time_to_expire += 1.0 / 365

        return theta

    def baw_rho(self) -> float:
        """baw 美式期权定价模型 rho"""
        f = self.baw_price()
        self.risk_free += 0.01

        f_change = self.baw_price()
        rho = f_change - f
        self.risk_free -= 0.01

        return rho

    def find_minimum(
        self,
        func: Any,
        initial_guess: float,
        max_iterations: int = 200,
        tolerance: float = 1e-7,
    ) -> float:
        """
        简化的 NelderMead 优化算法
        由于这里只需要用到一元的函数，所以这里直接写死算法中的 N = 1
        只返回最小值点，不返回最小值
        """

        def evaluate_function(x: float) -> float:
            try:
                return func(x)
            except Exception:
                return 1e10

        # 初始化 simplex 和函数值
        simplex = np.array(
            [initial_guess, 0.00025 if initial_guess == 0 else initial_guess * 1.05]
        )
        values = np.array(
            [evaluate_function(simplex[0]), evaluate_function(simplex[1])]
        )

        rho, chi, psi, sigma = 1, 2, 0.5, 0.5

        iterations = 0

        while iterations < max_iterations:
            if (
                np.max(np.abs(simplex[1] - simplex[0])) <= tolerance
                and np.max(np.abs(values[0] - values[1])) <= tolerance
            ):
                break

            xbar = np.mean(simplex[:-1])
            xr = (1 + rho) * xbar - rho * simplex[-1]
            fxr = evaluate_function(xr)
            doshrink = False

            if fxr < values[0]:
                xe = (1 + rho * chi) * xbar - rho * chi * simplex[-1]
                fxe = evaluate_function(xe)
                if fxe < fxr:
                    simplex[-1], values[-1] = xe, fxe
                else:
                    simplex[-1], values[-1] = xr, fxr
            else:
                if fxr < values[-2]:
                    simplex[-1], values[-1] = xr, fxr
                else:
                    if fxr < values[-1]:
                        xc = (1 + psi * rho) * xbar - psi * rho * simplex[-1]
                        fxc = evaluate_function(xc)
                        if fxc <= fxr:
                            simplex[-1], values[-1] = xc, fxc
                        else:
                            doshrink = True
                    else:
                        xcc = (1 - psi) * xbar + psi * simplex[-1]
                        fxcc = evaluate_function(xcc)
                        if fxcc < values[-1]:
                            simplex[-1], values[-1] = xcc, fxcc
                        else:
                            doshrink = True

                    if doshrink:
                        for j in range(1, len(simplex)):
                            simplex[j] = simplex[0] + sigma * (simplex[j] - simplex[0])
                            values[j] = evaluate_function(simplex[j])

            if values[0] > values[1]:
                simplex = simplex[::-1]
                values = values[::-1]

            iterations += 1

        return simplex[0] if values[0] < values[1] else simplex[1]

    def binary_search(
        self,
        max_guess: float,
        min_guess: float,
        price_func: Callable[[float, float], float],
        min_precision: float = 1e-7,
        max_count: int = 200,
    ) -> float:
        """
        二分法找值

        Args:
            max_guess: 最大初始猜测值。
            min_guess: 最小初始猜测值。
            price_func: 给定 sigma，计算期权价格的函数。
            min_precision: sigma 收敛的最小精度。默认为 1e-7。
            max_count: 最大迭代次数。默认为 200。
        """
        count = 0
        s_t = self.underlying_price * self.disc_q
        k_t = self.strike_price

        if self.option_type_sign * (s_t - k_t) >= self.market_price:
            return self.sigma_default

        o_sigma_top_price = price_func(max_guess, self.underlying_price)
        o_sigma_floor_price = price_func(min_guess, self.underlying_price)

        while count <= max_count:
            sigma = (min_guess + max_guess) / 2
            o_mid_price = price_func(sigma, self.underlying_price)

            if self.equal_price(o_mid_price, min_precision):
                return sigma
            elif (o_sigma_floor_price - self.market_price) * (
                o_mid_price - self.market_price
            ) < 0:
                max_guess = sigma
            else:
                min_guess = sigma

            count += 1

        if self.equal_price(o_sigma_floor_price, min_precision):
            return min_guess
        elif self.equal_price(o_sigma_top_price, min_precision):
            return max_guess

        return self.sigma_default


class OptionChainData(TypedDict):
    """
    期权链数据结构
    """

    strike_prices: list[float]
    call_options: list[InstrumentData]
    put_options: list[InstrumentData]


class OptionChain(object):
    """
    获取期权链数据

    Note:
        包含标的月份合约列表、到期日、行权价列表、看涨期权列表、看跌期权列表、平值期权档位获取方法

    Args:
        exchange: 交易所代码
        product_id: 品种代码
    """

    def __init__(self, exchange: str, product_id: str) -> None:
        self.exchange = exchange
        self.product_id = product_id

        self.all_options: list[InstrumentData] = self.get_instruments(
            self.exchange,
            self.product_id,
        )

        self.option_chain: dict[str, dict[str, OptionChainData]] = {}
        self.option_type: Literal["期权", "股票期权", "现货期权"] = None

        self.process_data()

    @staticmethod
    def get_instruments(exchange: str, product_id: str) -> list[InstrumentData]:
        """
        查询指定品种的所有合约信息

        Args:
            exchange: 交易所代码
            product_id: 品种代码
        """

        instruments: list[dict] = infini.get_instruments_by_product(
            exchange=exchange,
            product_id=product_id,
        )

        result: list[InstrumentData] = []

        for instrument in instruments:
            instrument = InstrumentData(instrument)

            if instrument.product_type in ["期权", "股票期权", "现货期权"]:
                result.append(instrument)

        return result

    def process_data(self) -> None:
        """预处理期权数据"""
        if not self.all_options:
            return

        self.option_type = self.all_options[0].product_type

        temp_chain = defaultdict(
            lambda: defaultdict(
                lambda: {
                    "strike_prices": set(),
                    "call_options": [],
                    "put_options": [],
                }
            )
        )

        for item in self.all_options:
            chain_entry = temp_chain[item.underlying_symbol][item.expire_date]
            chain_entry["strike_prices"].add(item.strike_price)

            if item.options_type == "CALL":
                chain_entry["call_options"].append(item)
            elif item.options_type == "PUT":
                chain_entry["put_options"].append(item)

        final_chain = {}

        for symbol in sorted(temp_chain.keys()):
            final_chain[symbol] = {}

            for date in sorted(temp_chain[symbol].keys()):
                data = temp_chain[symbol][date]
                data["strike_prices"] = sorted(list(data["strike_prices"]))
                data["call_options"].sort(key=lambda x: x.strike_price)
                data["put_options"].sort(key=lambda x: x.strike_price)
                final_chain[symbol][date] = data

        self.option_chain = final_chain

    def get_month_contracts(self) -> list[str]:
        """
        获取标的月份合约列表，按到期时间排序
        """

        return list(self.option_chain.keys())

    def get_expire_dates(self, underlying_symbol: str = None) -> list[str]:
        """
        获取标的月份合约期权到期日

        Args:
            underlying_symbol: 标的合约代码，默认为 None，返回所有标的合约期权到期日，不为 None 时返回对应标的合约期权到期日
        """

        if not underlying_symbol:
            expire_dates = set(k for v in self.option_chain.values() for k in v.keys())
            return sorted(expire_dates)

        return list(self.option_chain.get(underlying_symbol).keys())

    def get_strike_prices(
        self, underlying_symbol: str, expire_date: str = None
    ) -> list[float]:
        """
        获取行权价列表，升序排列

        Args:
            underlying_symbol: 标的合约代码
            expire_date: 到期时间，默认为最近到期时间
        """

        symbol_chain = self.option_chain.get(underlying_symbol)
        if not symbol_chain:
            return []

        if not expire_date:
            dates = self.get_expire_dates(underlying_symbol)
            expire_date = dates[0]

        return symbol_chain[expire_date]["strike_prices"]

    def get_call_options(
        self, underlying_symbol: str, expire_date: str = None
    ) -> list[str]:
        """
        获取看涨期权合约列表，按行权价升序排列

        Args:
            underlying_symbol: 标的合约代码
            expire_date: 到期时间，默认为最近到期时间
        """

        symbol_chain = self.option_chain.get(underlying_symbol)
        if not symbol_chain:
            return []

        if not expire_date:
            dates = self.get_expire_dates(underlying_symbol)
            expire_date = dates[0]

        return [
            item.instrument_id for item in symbol_chain[expire_date]["call_options"]
        ]

    def get_put_options(
        self, underlying_symbol: str, expire_date: str = None
    ) -> list[str]:
        """
        获取看跌期权合约列表，按行权价升序排列

        Args:
            underlying_symbol: 标的合约代码
            expire_date: 到期时间，默认为最近到期时间
        """

        symbol_chain = self.option_chain.get(underlying_symbol)
        if not symbol_chain:
            return []

        if not expire_date:
            dates = self.get_expire_dates(underlying_symbol)
            expire_date = dates[0]

        return [item.instrument_id for item in symbol_chain[expire_date]["put_options"]]

    def get_atm_option(
        self,
        underlying_symbol: str,
        underlying_price: float,
        expire_date: str = None
    ) -> Optional[int]:
        """
        获取平值期权档位

        Args:
            underlying_symbol: 标的合约代码
            underlying_price: 标的物当前价格
            expire_date: 到期时间，获取 ETF 期权平值期权档位时填写，默认为最近到期时间

        Returns:
            获取最接近标的价格的行权价在行权价列表中的索引位置
        """

        strike_prices = self.get_strike_prices(underlying_symbol, expire_date)

        if not strike_prices:
            return None

        # 找到插入 underlying_price 的位置，即第一个大于等于 underlying_price 的元素索引
        idx = bisect.bisect_left(strike_prices, underlying_price)

        # 处理边界情况
        if idx == 0:
            return 0
        if idx == len(strike_prices):
            return len(strike_prices) - 1

        # 比较前一个和当前元素，哪个更接近
        if abs(strike_prices[idx - 1] - underlying_price) <= abs(
            strike_prices[idx] - underlying_price
        ):
            return idx - 1
        else:
            return idx
