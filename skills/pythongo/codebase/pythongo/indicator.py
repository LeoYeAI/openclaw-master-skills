import numpy as np
import talib


class Indicators(object):
    """技术指标"""

    def __init__(self) -> None:
        np.seterr(divide='ignore', invalid='ignore')
        np.errstate(divide="ignore", invalid="ignore")

    def sma(self, timeperiod: int = 9, array: bool = False) -> np.float64 | np.ndarray:
        """简单均线"""
        result: np.ndarray = talib.SMA(self.close, timeperiod)
        return result if array else result[-1]

    def ema(self, timeperiod: int = 12, array: bool = False) -> np.float64 | np.ndarray:
        """EXPMA 指标"""
        result: np.ndarray = talib.EMA(self.close, timeperiod)
        return result if array else result[-1]

    def std(self, timeperiod: int = 5, array: bool = False) -> np.float64 | np.ndarray:
        """标准差"""
        result: np.ndarray = talib.STDDEV(
            self.close,
            timeperiod=timeperiod,
            nbdev=np.sqrt(timeperiod / (timeperiod - 1)) 
        )
        return result if array else result[-1]

    def bbi(
        self,
        n1: int = 3,
        n2: int = 6,
        n3: int = 12,
        n4: int = 24,
        array: bool = False
    ) -> np.float64 | np.ndarray:
        """BBI 多空指标"""
        _sma = lambda n: self.sma(n, array=True)
        bbi = (_sma(n1) + _sma(n2) + _sma(n3) + _sma(n4)) / 4
        return bbi if array else bbi[-1]

    def cci(self, timeperiod: int = 14, array: bool = False) -> np.float64 | np.ndarray:
        """CCI 顺势指标"""
        result = talib.CCI(self.high, self.low, self.close, timeperiod)
        return result if array else result[-1]

    def rsi(self, timeperiod: int = 14, array: bool = False) -> np.float64 | np.ndarray:
        """RSI 相对强弱指数, 和无限易有细微差距, 可忽略"""
        result = talib.RSI(self.close, timeperiod)
        return result if array else result[-1]

    def adx(self, timeperiod: int = 14, array: bool = False):
        """ADX 指标"""
        result = talib.ADX(self.high, self.low, self.close, timeperiod)
        return result if array else result[-1]

    def sar(
        self,
        acceleration: float = 0.02,
        maximum: float = 0.2,
        array: bool = False
    ) -> np.float64 | np.ndarray:
        """抛物线 SAR, 和无限易有细微差距, 可忽略"""
        result: np.ndarray = talib.SAR(
            self.high,
            self.low,
            acceleration=acceleration,
            maximum=maximum
        )

        return result if array else result[-1]

    def kdj(
        self,
        fastk_period: int = 9,
        slowk_period: int = 3,
        slowd_period: int = 3,
        array: bool = False
    ) -> (
        tuple[np.float64, np.float64, np.float64] |
        tuple[np.ndarray, np.ndarray, np.ndarray]
    ):
        """KDJ 指标"""
        scl = self.close - (llv := talib.MIN(self.low, fastk_period))
        shl = talib.MAX(self.high, fastk_period) - llv
        rsv = np.zeros_like(scl, dtype=np.float64)
        np.divide(scl, shl, out=rsv, where=(shl != 0.0))
        rsv *= 100.0
        k = talib.EMA(rsv, slowk_period * 2 - 1)
        k[np.isnan(k)] = 0.0
        d = talib.EMA(k, slowd_period * 2 - 1)
        d[np.isnan(d)] = 0.0
        j = k * 3 - d * 2
        return (k, d, j) if array else (k[-1], d[-1], j[-1])

    def kd(
        self,
        fastk_period: int = 9,
        slowk_period: int = 3,
        slowd_period: int = 3,
        array: bool = False
    ) -> (
        tuple[np.float64, np.float64] |
        tuple[np.ndarray, np.ndarray]
    ):
        """KD 指标"""
        k, d, _ = self.kdj(
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowd_period=slowd_period,
            array=array
        )
        return k, d

    def macdext(
        self,
        fast_period: int = 12,
        fastmatype: int = 1,
        slow_period: int = 26,
        slowmatype: int = 1,
        signal_period: int = 9,
        signalmatype: int = 1,
        array: bool = False
    ) -> (
        tuple[np.float64, np.float64, np.float64] |
        tuple[np.ndarray, np.ndarray, np.ndarray]
    ):
        """
        MACD 指标加强版
        ----

        Args:
            fast_period: 快周期
            slow_period: 慢周期
            signal_period: 计算出的 MACD 在 signal_period 周期的简单平均(SMA)值
            *matype: 指标类型, 当前默认为 EMA
                0: SMA (simple)
                1: EMA (exponential)
                2: WMA (weighted)
                3: DEMA (double exponential)
                4: TEMA (triple exponential)
                5: TRIMA (triangular)
                6: KAMA (Kaufman adaptive)
                7: MAMA (Mesa adaptive)
                8: T3 (triple exponential T3)
        """
        macd, signal, hist = talib.MACDEXT(
            self.close,
            fastperiod=fast_period,
            fastmatype=fastmatype,
            slowperiod=slow_period,
            slowmatype=slowmatype,
            signalperiod=signal_period,
            signalmatype=signalmatype
        )

        return (macd, signal, hist * 2) if array else (macd[-1], signal[-1], hist[-1] * 2)

    def macd(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        array: bool = False
    ) -> (
        tuple[np.float64, np.float64, np.float64] |
        tuple[np.ndarray, np.ndarray, np.ndarray]
    ):
        """
        MACD 指标
        ----
        
        Args:
            fast_period: 快周期
            slow_period: 慢周期
            signal_period: 计算出的 MACD 在 signal_period 周期的移动平均(EMA)值
        """
        macd, signal, hist = talib.MACD(
            self.close,
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period
        )
        
        return (macd, signal, hist * 2) if array else (macd[-1], signal[-1], hist[-1] * 2)

    def atr(self, timeperiod: int = 14, array: bool = False) -> (
        tuple[np.float64, np.float64] |
        tuple[np.ndarray, np.ndarray]
    ):
        """真实波幅均值, ATR"""
        close = self.close[:-1]
        high = self.high[1:]
        low = self.low[1:]
        hl = high - low
        cl = abs(close - low)
        ch = abs(close - high)
        tr = self.arr_max(hl, cl, ch)
        atr = talib.SMA(tr, timeperiod)

        return (atr, tr) if array else (atr[-1], tr[-1])

    def boll(self, timeperiod: int = 20, deviation: int = 2) -> tuple[np.float64, np.float64]:
        """布林通道"""
        mid = self.sma(timeperiod)
        std = self.std(timeperiod)

        upper_band = mid + std * deviation
        lower_band = mid - std * deviation

        return upper_band, lower_band

    def keltner(self, timeperiod: int = 20, multiple: int = 2) -> tuple[np.float64, np.float64]:
        """肯特纳通道 (Keltner Channels, KC)"""
        mid = self.ema(timeperiod)
        atr, _ = self.atr(timeperiod)

        upper_envelope = mid + atr * multiple
        lower_envelope = mid - atr * multiple

        return upper_envelope, lower_envelope

    def donchian(self, timeperiod: int = 20) -> tuple[np.float64, np.float64]:
        """唐奇安通道 (Donchian Channels, DC)"""
        upper_channel = talib.MAX(self.high, timeperiod)
        lower_channel = talib.MIN(self.low, timeperiod)
        return upper_channel[-1], lower_channel[-1]

    def arr_max(self, *array: np.ndarray) -> np.ndarray:
        """多数组取最值构成新数组"""
        result = list(map(max, zip(*array)))
        return np.array(result)
