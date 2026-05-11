import datetime
from collections import deque
from functools import partial
from typing import Optional

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtGui import QBrush, QFont, QPainter, QPen, QPicture
from PyQt5.QtWidgets import (QGraphicsItem, QStyleOptionGraphicsItem,
                             QVBoxLayout, QWidget)

from pythongo.classdef import KLineData
from pythongo.ui.crosshair import Crosshair


class PlotItemType(pg.ViewBox, pg.PlotItem):
    ...


class KeyWraper(QWidget):
    """键盘鼠标功能支持的元类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CustomViewBox(pg.ViewBox):
    """选择缩放功能支持"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MyStringAxis(pg.AxisItem):
    """时间序列横坐标支持"""

    def __init__(self, xdict: dict = {}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minVal = 0
        self.maxVal = 0
        self.xdict: dict = xdict
        self.x_values = np.asarray(xdict.keys())
        self.x_strings = xdict.values()
        self.setPen(color=(255, 255, 255, 255), width=0.8)
        self.setStyle(
            tickFont=QFont("Roman times", 10, QFont.Bold),
            autoExpandTextSpace=True
        )

    def update_xdict(self, xdict: dict):
        """更新坐标映射表"""
        self.xdict.update(xdict)
        self.x_values = np.asarray(self.xdict.keys())
        self.x_strings = self.xdict.values()


class CandlestickItem(QGraphicsItem):
    """K线图形对象"""

    def __init__(self, data: pd.DataFrame):
        """初始化"""
        super().__init__()

        # 只重画部分图形，大大提高界面更新速度
        self.rect: QtCore.QRect = None
        self.setFlag(self.ItemUsesExtendedStyleOption)

        # 画笔和画刷
        self.w = 0.4
        self.offset = 0
        self.low = 0
        self.high = 1

        self.picture: QPicture = QPicture()
        self.pictures: list[QPicture] = []
        self.green_pen: QPen = pg.mkPen(color=(0, 176, 26), width=self.w * 2)
        self.green_brush: QBrush = pg.mkBrush((0, 176, 26))
        self.red_pen: QPen = pg.mkPen(color=(255, 113, 113), width=self.w * 2)
        self.red_brush: QBrush = pg.mkBrush((255, 113, 113))

        self.generate_picture(data)

    def generate_picture(self, data: pd.DataFrame, redraw: bool = False):
        """重新生成图形对象"""
        if len(data) == 0:
            return

        if redraw:  #: 重画或者只更新最后一个K线
            self.pictures = []
        elif self.pictures:
            self.pictures.pop()

        self.low, self.high = (
            np.min(data["low"]),
            np.max(data["high"])
        )

        for (index, open0, close0, low0, high0) in data[len(self.pictures):]:
            picture = QPicture()
            p = QPainter()
            p.begin(picture)
            # 下跌蓝色（实心）, 上涨红色（空心）
            pen, brush, pmin, pmax = (
                (self.green_pen, self.green_brush, close0, open0)
                if open0 > close0
                else (self.red_pen, self.red_brush, open0, close0)
            )

            p.setPen(pen)  
            p.setBrush(brush)

            # 画K线方块和上下影线
            if open0 == close0:
                p.drawLine(
                    QtCore.QPointF(index - self.w, open0),
                    QtCore.QPointF(index + self.w, close0)
                )
            else:
                p.drawRect(QtCore.QRectF(index - self.w, open0, self.w * 2, close0 - open0))

            if pmin > low0:
                p.drawLine(
                    QtCore.QPointF(index, low0),
                    QtCore.QPointF(index, pmin)
                )

            if high0 > pmax:
                p.drawLine(
                    QtCore.QPointF(index, pmax),
                    QtCore.QPointF(index, high0)
                )

            p.end()
            self.pictures.append(picture)

    def paint(self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None
    ):
        """继承 paint 事件, 自动重画"""
        rect = option.exposedRect
        xmin = max(0, int(rect.left()))
        xmax = min(len(self.pictures), int(rect.right()))

        if (
            self.rect != (_rect := (rect.left(), rect.right()))
            or self.picture is None
        ):
            self.rect = _rect
            self.picture = self.create_picture(xmin, xmax)
            self.picture.play(painter)
        elif self.picture:
            self.picture.play(painter)

    def create_picture(self, xmin: int, xmax: int) -> QPicture:
        """创建 QPicture 对象"""
        picture = QPicture()
        p = QPainter(picture)
        [pic.play(p) for pic in self.pictures[xmin:xmax]]
        p.end()
        return picture

    def boundingRect(self) -> QtCore.QRectF:
        """继承 boundingRect 事件, 定义边界"""
        return QtCore.QRectF(0, self.low, len(self.pictures), (self.high - self.low))


class KLineWidget(KeyWraper):
    """用于显示价格走势图"""

    cls_id = 0
    update_candle_signal = QtCore.pyqtSignal()
    add_buy_sell_signal = QtCore.pyqtSignal(int)
    draw_marks_signal = QtCore.pyqtSignal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.index: int = 0
        self.view_kline_range: list[int] = [0, 0]
        self.kline_count: int = 60  # 显示的 K 线范围

        KLineWidget.cls_id += 1
        self.window_id: str = str(KLineWidget.cls_id)

        self.init_data_container()

        self.colors = [
            "#FFFFFF", "#FFF100", "#FF37E5",
            "#C18AFF", "#B6FF1A", "#368FFF"
        ]

        # 所有K线上信号图
        self.indicator_color = deque(self.colors)
        self.indicator_data: dict[str, np.ndarray] = {}
        self.indicator_color_map: dict[str, str] = {}
        self.indicator_plot_items: dict[str, pg.PlotDataItem] = {}

        # 所副图上信号图
        self.sub_indicator_color = deque(self.colors)
        self.sub_indicator_data: dict[str, np.ndarray] = {}
        self.sub_indicator_color_map: dict[str, str] = {}
        self.sub_indicator_plot_items: dict[str, pg.PlotDataItem] = {}

        self.init_completed = False
        self.update_candle_signal.connect(self.update_candle)
        self.add_buy_sell_signal.connect(self.add_new_bs_signal)
        self.draw_marks_signal.connect(self.draw_marks)

        self.init_ui()
        self.init_xrange_event()

    def init_data_container(self) -> None:
        """初始化数据容器"""
        base = ["open", "close", "low", "high"]

        self.datas: np.recarray = pd.DataFrame(
            columns=["datetime", *base, "volume", "open_interest"]
        ).set_index("datetime").to_records(index_dtypes="<M8[s]")

        self.list_kline: np.recarray = pd.DataFrame(
            columns=["array_index", *base]
        ).to_records(False)

        self.list_volume: np.recarray = pd.DataFrame(
            columns=["array_index", *base[:2], "high", "low"]
        ).to_records(False)

        self.list_high: list[float] = []
        self.list_low: list[float] = []
        self.buy_sell_signals: dict[int, float] = {}
        self.list_open_interest: list[int] = []
        self.arrows: list[pg.ArrowItem] = []

    def init_ui(self):
        """初始化界面"""

        # 界面布局
        self.kline_layout = pg.GraphicsLayout(border=(100, 100, 100))
        self.kline_layout.setContentsMargins(10, 10, 10, 10)
        self.kline_layout.setSpacing(0)
        self.kline_layout.setBorder(color=(255, 255, 255, 255), width=0.8)
        self.kline_layout.setZValue(0)
        self.layout_title = self.kline_layout.addLabel("PythonGo")
        
        # 设置横坐标
        self.time_axis = MyStringAxis(orientation="bottom")

        # 初始化子图
        self.init_kline_plot_item()
        self.init_vol_plot_item()  
        self.init_bottom_plot_item()

        plot_widget = pg.PlotWidget()
        plot_widget.setCentralItem(self.kline_layout)

        # 注册十字光标
        self.crosshair = Crosshair(plot_widget, self)

        # 设置界面
        view_box = QVBoxLayout()
        view_box.addWidget(plot_widget)
        self.setLayout(view_box)

        self.init_completed = True    

    def set_title(self, title: str) -> None:
        """设置窗口标题, 一般为合约代码"""
        self.layout_title.setText(title, bold=True, color="w")

    def get_window_name(self, name: str) -> str:
        return f"{self.window_id}_{name}"

    def make_plot_item(self, name: str) -> PlotItemType:
        """生成绘图对象"""
        view_box = CustomViewBox()
        view_box.setMouseEnabled(x=True, y=False)
        view_box.setRange(xRange=(0, 1), yRange=(0, 1))

        plot_item: PlotItemType = pg.PlotItem(viewBox=view_box, name=name)
        plot_item.setMenuEnabled(False)
        plot_item.setClipToView(True)
        plot_item.hideAxis("left")
        plot_item.showAxis("right")
        plot_item.setDownsampling(mode="peak")
        plot_item.showGrid(x=True, y=True)
        plot_item.hideButtons()

        axis_item: pg.AxisItem = plot_item.getAxis("right")
        axis_item.setWidth(60)
        axis_item.setStyle(
            tickFont=QFont("Roman times", 10, QFont.Bold)
        )
        axis_item.setPen(color=(255, 255, 255, 255), width=0.8)
        return plot_item

    def init_vol_plot_item(self):
        """初始化成交量子图"""
        self.volume = CandlestickItem(self.list_volume)

        self.vol_plot_item = self.make_plot_item(self.get_window_name("PlotVOL"))
        self.vol_plot_item.addItem(self.volume)
        self.vol_plot_item.setMaximumHeight(150)
        self.vol_plot_item.setXLink(self.get_window_name("PlotOI"))
        self.vol_plot_item.hideAxis("bottom")

        self.kline_layout.nextRow()
        self.kline_layout.addItem(self.vol_plot_item)

    def init_kline_plot_item(self):
        """初始化K线子图"""
        self.candle = CandlestickItem(self.list_kline)

        self.kline_plot_item = self.make_plot_item(self.get_window_name("PlotKL"))        
        self.kline_plot_item.addItem(self.candle)
        self.kline_plot_item.setMinimumHeight(350)
        self.kline_plot_item.setXLink(self.get_window_name("PlotOI"))
        self.kline_plot_item.hideAxis("bottom")

        self.kline_layout.nextRow()
        self.kline_layout.addItem(self.kline_plot_item)

    def init_bottom_plot_item(self):
        """初始化底部子图, 一般为持仓量"""
        self.bottom_chart = self.make_plot_item(self.get_window_name("PlotOI"))
        self.bottom_chart_plot = self.bottom_chart.plot()

        self.kline_layout.nextRow()
        self.kline_layout.addItem(self.bottom_chart)

    def plot_volume(self, redraw: bool = False, xmin: int = 0, xmax: int = -1):
        """重画成交量子图"""
        if self.init_completed:
            self.volume.generate_picture(
                data=self.list_volume[xmin:xmax],
                redraw=redraw
            )

    def plot_kline(self, redraw: bool = False, xmin: int = 0, xmax: int = -1):
        """重画K线子图"""
        if self.init_completed:
            self.candle.generate_picture(
                data=self.list_kline[xmin:xmax],
                redraw=redraw
            )

    def plot_open_interest(self, xmin: int = 0, xmax: int = -1):
        """重画持仓量子图"""
        if self.init_completed:
            self.bottom_chart_plot.setData(
                self.list_open_interest[xmin:xmax],
                pen="w",
                name="OpenInterest"
            )

    def add_indicator(self, indicator_name: str, main: bool = True):
        """添加指标图"""
        if main:
            if indicator_name in self.indicator_plot_items:
                self.kline_plot_item.removeItem(self.indicator_plot_items[indicator_name])
            self.indicator_plot_items[indicator_name] = self.kline_plot_item.plot()
            self.indicator_color_map[indicator_name] = self.indicator_color[0]
            self.indicator_color.append(self.indicator_color.popleft())
        else:
            if indicator_name in self.sub_indicator_plot_items:
                self.bottom_chart.removeItem(self.sub_indicator_plot_items[indicator_name])
            self.sub_indicator_plot_items[indicator_name] = self.bottom_chart.plot()
            self.sub_indicator_color_map[indicator_name] = self.sub_indicator_color[0]
            self.sub_indicator_color.append(self.sub_indicator_color.popleft())

    def set_indicator(
        self,
        indicator: list[str],
        datas: dict[str, list[float]],
        main_plot: bool = True
    ):
        """设置指标图"""
        for indicator_name in indicator:
            _indicator_data = np.array(datas[indicator_name])
            self.add_indicator(indicator_name, main_plot)

            if main_plot:
                self.indicator_data[indicator_name] = _indicator_data
                self.indicator_plot_items[indicator_name].setData(
                    _indicator_data,
                    pen=self.indicator_color_map[indicator_name],
                    name=indicator_name
                )
            else:
                self.sub_indicator_data[indicator_name] = _indicator_data
                self.sub_indicator_plot_items[indicator_name].setData(
                    _indicator_data,
                    pen=self.sub_indicator_color_map[indicator_name],
                    name=indicator_name
                )

    def draw_marks(self):
        """显示开平仓信号"""
        if len(self.datas) == 0:
            return

        for arrow in self.arrows:
            self.kline_plot_item.removeItem(arrow)

        # 画买卖信号
        for index, price in self.buy_sell_signals.items():
            arrow = pg.ArrowItem(
                pos=(index, self.datas[index]["low" if price > 0 else "high"]),
                angle=90 if price > 0 else -90,
                brush=(168, 101, 243) if price > 0 else (255, 234, 90)
            )

            self.kline_plot_item.addItem(arrow)
            self.arrows.append(arrow)

    def refresh(self):
        """刷新三个子图的显示范围"""   
        minutes = int(self.kline_count / 2)
        xmin = max(0, self.index - minutes)
        xmax = xmin + 2 * minutes
        self.bottom_chart.setXRange(xmin, xmax)
        self.kline_plot_item.setXRange(xmin, xmax)
        self.vol_plot_item.setXRange(xmin, xmax)
        self.set_sub_indicator_y_range(xmin, xmax)

    def onPaint(self):
        """界面刷新回调"""
        view = self.kline_plot_item.getViewBox()
        view_range = view.viewRange()
        xmin = max(0, int(view_range[0][0]))
        xmax = max(0, int(view_range[0][1]))
        self.index = int((xmin + xmax) / 2) + 1

    def init_xrange_event(self):
        def viewXRangeChanged(low: str, high: str, *args) -> None:
            if len(self.datas) == 0:
                return

            view: pg.ViewBox = args[0]
            view_range = view.viewRange()

            xmin = max(0, int(view_range[0][0]))
            xmax = max(0, int(view_range[0][1]))
            xmax = min(xmax, len(self.datas))

            ymin = min(self.datas[xmin:xmax][low])
            ymax = max(self.datas[xmin:xmax][high])
            ymin, ymax = (-1, 1) if ymin == ymax else (ymin, ymax)

            if view.name.endswith("PlotOI") and self.sub_indicator_data:
                self.set_sub_indicator_y_range(xmin, xmax)
            else:
                view.setYRange(ymin, ymax)

        self.xrange_events = {
            "kline": partial(viewXRangeChanged, "low", "high"),
            "volume": partial(viewXRangeChanged, "volume", "volume"),
            "bottom": partial(viewXRangeChanged, "open_interest", "open_interest")
        }        

    def set_xrange_event(self):
        """更新十字光标数据，并设置 XRange 事件用于 Y 坐标自适应"""
        self.crosshair.datas = self.datas

        self.kline_plot_item.getViewBox().sigXRangeChanged.connect(
            self.xrange_events["kline"]
        )

        self.vol_plot_item.getViewBox().sigXRangeChanged.connect(
            self.xrange_events["volume"]
        )

        self.bottom_chart.getViewBox().sigXRangeChanged.connect(
            self.xrange_events["bottom"]
        )

    def cancel_xrange_event(self):
        """取消 XRange 事件"""
        self.kline_plot_item.getViewBox().sigXRangeChanged.disconnect(
            self.xrange_events["kline"]
        )
        self.vol_plot_item.getViewBox().sigXRangeChanged.disconnect(
            self.xrange_events["volume"]
        )
        self.bottom_chart.getViewBox().sigXRangeChanged.disconnect(
            self.xrange_events["bottom"]
        )

    def set_sub_indicator_y_range(self, xmin: int, xmax: int) -> None:
        """设置指标副图的 YRange"""
        if self.sub_indicator_data:
            array_data = self.sub_indicator_data.values()
            all_data = np.array(list(map(lambda x: x[xmin:xmax], array_data)))
            self.bottom_chart.setYRange(all_data.min(), all_data.max())

    def clear_data(self):
        """清空数据"""
        self.list_low.clear()
        self.list_high.clear()
        self.list_open_interest.clear()
        self.buy_sell_signals.clear()
        self.indicator_data.clear()

        for arrow in self.arrows:
            """清除箭头前先从图表上移除箭头"""
            self.kline_plot_item.removeItem(arrow)

        self.arrows.clear()

        self.list_kline.resize(0, refcheck=0)
        self.list_volume.resize(0, refcheck=0)
        self.datas.resize(0, refcheck=0)
        # self.cancel_xrange_event()
        self.clear_buy_sell_signals()
        self.clear_buy_sell_signals(False)

    def clear_buy_sell_signals(self, main_plot: bool = True):
        """清空信号图形"""
        if main_plot:
            for item in self.indicator_plot_items.values():
                self.kline_plot_item.removeItem(item)
            self.indicator_data = {}
            self.indicator_plot_items = {}
        else:
            for item in self.sub_indicator_plot_items.values():
                self.bottom_chart.removeItem(item)
            self.sub_indicator_data = {}
            self.sub_indicator_plot_items = {}

    def add_new_bs_signal(self, index: int) -> None:
        """画买卖信号"""
        price = self.buy_sell_signals[index]
        arrow = pg.ArrowItem(
            pos=(index, self.datas[index]["low" if price > 0 else "high"]),
            angle=90 if price > 0 else -90,
            brush=(168, 101, 243) if price > 0 else (255, 234, 90)
        )

        self.kline_plot_item.addItem(arrow)
        self.arrows.append(arrow)

    def insert_kline(self, kline: KLineData) -> None:
        """插入 K 线, 不能使用 np.insert"""
        array_size = len(self.datas)

        self.datas.resize(array_size + 1, refcheck=0)
        self.list_kline.resize(array_size + 1, refcheck=0)
        self.list_volume.resize(array_size + 1, refcheck=0)

        self.datas[-1] = self.datas[-2]
        self.datas[-2] = (
            kline.datetime,
            kline.open,
            kline.close,
            kline.low,
            kline.high,
            kline.volume,
            kline.open_interest
        )

        self.list_kline[-1] = self.list_kline[-2]
        self.list_kline[-1].array_index += 1
        self.list_kline[-2] = (array_size - 1, kline.open, kline.close, kline.low, kline.high)

        self.list_volume[-1] = self.list_volume[-2]
        self.list_volume[-1].array_index += 1
        self.list_volume[-2] = (
            (array_size - 1, abs(kline.volume), 0, abs(kline.volume), 0)
            if kline.close < kline.open
            else (array_size - 1, 0, abs(kline.volume), abs(kline.volume), 0)
        )


        self.list_low.insert(-1, kline.low)
        self.list_high.insert(-1, kline.high)
        self.list_open_interest.insert(-1, kline.open_interest)

        self.time_axis.update_xdict(dict(enumerate(self.datas["datetime"])))

    def update_kline(self, kline: KLineData):
        """新增 K 线数据, K 线播放模式"""
        is_new_kline = not (
            len(self.datas) > 0
            and kline.datetime == self.datas[-1].datetime.astype(datetime.datetime)
        )

        if is_new_kline:
            array_index = len(self.datas)
            self.datas.resize(array_index + 1, refcheck=0)
            self.list_kline.resize(array_index + 1, refcheck=0)
            self.list_volume.resize(array_index + 1, refcheck=0)
        else:
            array_index = len(self.datas) - 1
            self.list_low.pop()
            self.list_high.pop()
            self.list_open_interest.pop()

        self.datas[-1] = (
            kline.datetime,
            kline.open,
            kline.close,
            kline.low,
            kline.high,
            kline.volume,
            kline.open_interest
        )
        self.list_kline[-1] = (array_index, kline.open, kline.close, kline.low, kline.high)
        self.list_volume[-1] = (  #: O C H L
            (array_index, abs(kline.volume), 0, abs(kline.volume), 0)
            if kline.close < kline.open
            else (array_index, 0, abs(kline.volume), abs(kline.volume), 0)
        )

        self.list_low.append(kline.low)
        self.list_high.append(kline.high)
        self.list_open_interest.append(kline.open_interest)

        self.time_axis.update_xdict({array_index: kline.datetime})

        return is_new_kline


    def load_data(self, datas: pd.DataFrame):
        """
        载入 pandas.DataFrame K 线数据
        
        Args:
            datas: K 线数组转换成 DataFrame 后的数据
        """
        datas["array_index"] = np.array(range(len(datas.index)))

        self.datas = datas[
            ["open", "close", "low", "high", "volume", "open_interest"]
        ].to_records(index_dtypes="<M8[s]")

        self.time_axis.xdict = {}
        self.time_axis.update_xdict(dict(enumerate(self.datas["datetime"])))
        self.set_xrange_event()

        # 更新画图用到的数据
        self.list_kline = datas[["array_index", "open", "close", "low", "high"]].to_records(False)
        self.list_high = datas["high"].values.tolist()
        self.list_low = datas["low"].values.tolist()
        self.list_open_interest = datas["open_interest"].values.tolist()

        # 成交量颜色和涨跌同步，K 线方向由涨跌决定
        df = pd.DataFrame()
        df["array_index"] = datas["array_index"].values
        df["open"] = df["close"] = df["high"] = datas["volume"].values
        df.loc[datas["open"].values <= datas["close"].values, "open"] = 0
        df.loc[datas["open"].values > datas["close"].values, "close"] = 0
        df["low"] = 0

        self.list_volume = df.to_records(False)

    def plot_all(self):
        """重画所有界面"""
        self.index = len(self.datas)
        xmin, xmax = 0, len(self.datas)

        self.bottom_chart.setLimits(xMin=xmin, xMax=xmax)
        self.kline_plot_item.setLimits(xMin=xmin, xMax=xmax)
        self.vol_plot_item.setLimits(xMin=xmin, xMax=xmax)
        self.plot_kline(redraw=True, xmin=xmin, xmax=xmax)
        self.plot_volume(redraw=True, xmin=xmin, xmax=xmax)
        self.plot_open_interest(xmin=xmin, xmax=xmax)
        self.refresh()

        self.crosshair.update_signal.emit((None, None))

    def update_candle(self) -> None:
        """更新线图"""
        self.index = len(self.datas)

        for plot_item in (self.bottom_chart, self.kline_plot_item, self.vol_plot_item):
            plot_item.setLimits(xMin=0, xMax=len(self.datas))

        x_range = int(self.kline_plot_item.getViewBox().viewRange()[0][-1])

        if x_range < len(self.datas) - 1:
            """如果在浏览前面的 K 线, 则不更新线图"""
            return

        self.plot_kline(False, 0, len(self.datas))
        self.plot_volume(False, 0, len(self.datas))
        self.plot_open_interest(0, len(self.datas))

        minutes = int(self.kline_count / 2)
        xmin = max(0, len(self.datas) - minutes)
        xmax = xmin + 2 * minutes

        self.candle.picture = None
        self.volume.picture = None

        self.update()

        for plot_item in (self.bottom_chart, self.kline_plot_item, self.vol_plot_item):
            plot_item.setXRange(xmin, xmax)

        self.crosshair.update_signal.emit((None, None))        
