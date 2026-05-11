import datetime as dt

import numpy as np
import pyqtgraph as pg
from pandas import DataFrame
from PyQt5 import QtCore
from PyQt5.QtWidgets import QGraphicsItem


class TextItemType(pg.TextItem, QGraphicsItem): ...
class InfiniteLineType(pg.InfiniteLine, QGraphicsItem): ...
class PlotItemType(pg.PlotItem, QGraphicsItem):...


class Crosshair(QtCore.QObject):
    update_signal = QtCore.pyqtSignal(tuple)

    def __init__(self, parent: pg.PlotWidget, master):
        self.master = master
        super().__init__(parent)

        self.up_color = "#FF7171"
        self.down_color = "#00B01A"

        self.x_axis = 0
        self.y_axis = 0

        self.datas: DataFrame = np.rec.array(np.zeros(0))

        self.y_axises: list[int] = [0] * 3

        self.text_prices: list[TextItemType] = [
            pg.TextItem("", anchor=(1, 1)) for _ in range(3)
        ]

        self.views: list[PlotItemType] = [
            parent.centralWidget.getItem(i + 1, 0)
            for i in range(3)
        ]

        self.rects: list[QtCore.QRectF] = self.get_rects()

        self.vertical_lines: list[InfiniteLineType] = [
            pg.InfiniteLine(angle=90, movable=False) for _ in range(3)
        ]

        self.horizontal_lines: list[InfiniteLineType] = [
            pg.InfiniteLine(angle=0,  movable=False) for _ in range(3)
        ]
        self.h_line_visible = [False] * 3
        
        # mid 在 y 轴动态跟随最新价显示最新价和最新时间
        self.__text_info: TextItemType = pg.TextItem("kline_info")
        self.__text_sig: TextItemType = pg.TextItem("lastSigInfo", anchor=(1, 0))
        self.__text_sub_sig: TextItemType = pg.TextItem("lastSubSigInfo", anchor=(1, 0))
        self.__text_volume: TextItemType = pg.TextItem("kline_volume", anchor=(1, 0))

        self.init_ui()
        self.init_mouse_move_event()

        self.update_signal.connect(self.update_info)

    def init_mouse_move_event(self) -> None:
        self.proxy = pg.SignalProxy(
            signal=self.parent().scene().sigMouseMoved,
            rateLimit=60,
            slot=self.__mouse_moved
        )

    def init_ui(self) -> None:
        """初始化 UI"""
        self.__text_info.setZValue(2)
        self.__text_sig.setZValue(2)
        self.__text_sub_sig.setZValue(2)
        self.__text_volume.setZValue(2)

        for i in range(3):
            self.text_prices[i].setZValue(2)
            self.vertical_lines[i].setPos(0)
            self.horizontal_lines[i].setPos(0)
            self.vertical_lines[i].setZValue(0)
            self.horizontal_lines[i].setZValue(0)
            self.views[i].addItem(self.vertical_lines[i])
            self.views[i].addItem(self.horizontal_lines[i])
            self.views[i].addItem(self.text_prices[i])
        
        self.views[0].addItem(self.__text_info, ignoreBounds=True)
        self.views[0].addItem(self.__text_sig, ignoreBounds=True)
        self.views[1].addItem(self.__text_volume, ignoreBounds=True)
        self.views[2].addItem(self.__text_sub_sig, ignoreBounds=True)

    def get_rects(self) -> list[QtCore.QRectF]:
        return [self.views[i].sceneBoundingRect() for i in range(3)]

    def update_info(self, pos: tuple[float, float]):
        """刷新界面显示"""
        x_axis, y_axis = pos if all(pos) else (self.x_axis, self.y_axis)
        self.move_to(x_axis, y_axis)
        
    def __mouse_moved(self, event: tuple[QtCore.QPointF]):
        """鼠标移动回调"""
        pos = event[0]
        self.rects: list[QtCore.QRectF] = self.get_rects()
        for i in range(3):
            self.h_line_visible[i] = False
            if self.rects[i].contains(pos):
                mouse_point: QtCore.QPointF = self.views[i].getViewBox().mapSceneToView(pos)
                x_axis = mouse_point.x()
                y_axis = mouse_point.y()
                self.y_axises[i] = y_axis
                self.h_line_visible[i] = True
                self.move_to(int(x_axis), y_axis)

    def move_to(self, x_axis: int, y_axis: float):
        if all([x_axis, y_axis]) is False:
            return

        self.rects: list[QtCore.QRectF] = self.get_rects()

        self.x_axis, self.y_axis = x_axis, y_axis

        self.set_vhline_pos(x_axis, y_axis)
        self.show_kline_info(x_axis, y_axis)

    def set_vhline_pos(self, x_axis: int, y_axis: float):
        """水平和竖线位置设置"""
        for i in range(3):
            self.vertical_lines[i].setPos(x_axis)
            if self.h_line_visible[i]:
                self.horizontal_lines[i].setPos(y_axis if i == 0 else self.y_axises[i])
                self.horizontal_lines[i].show()
            else:
                self.horizontal_lines[i].hide()

    def _ind_str(self, color: str, name: str, value: str) -> str:
        return f'<span style="color: {color};">&nbsp;&nbsp;{name}: {value:.2f}</span>'

    def get_color(self, value: float, close: float) -> str:
        """和上一个收盘价比较，决定 K 线信息的字符颜色"""
        return self.up_color if value > close else self.down_color

    def show_kline_info(self, x_axis: int, y_axis: float):
        """显示 K 线信息"""
        if (_size := len(self.datas)) == 0:
            return

        if x_axis >= _size:
            x_axis = _size - 1

        kline = self.datas[x_axis]
        pre_kline = self.datas[x_axis - 1]

        open_text_color = self.get_color(kline.open, pre_kline.close)
        high_text_color = self.get_color(kline.high, pre_kline.close)
        low_text_color = self.get_color(kline.low, pre_kline.close)
        close_text_color = self.get_color(kline.close, pre_kline.close)

        tick_time: dt.datetime = kline["datetime"].astype(dt.datetime)
        date_text = tick_time.strftime("%F")
        time_text = tick_time.strftime("%X")

        final_price_text = (
            f"<span>成交价</span><br>"
            f"<span>{price}</span><br>"
            if (price := abs(self.master.buy_sell_signals.get(x_axis, 0)))
            else ""
        )

        self.__text_info.setHtml(
            f'<div style="background-color:#3F424D; font-size: 16px; color: white"> \
                <span>日期</span><br> \
                <span>{date_text}</span><br> \
                <span>时间</span><br> \
                <span>{time_text}</span><br> \
                <span style="color: {open_text_color};">开盘价</span><br> \
                <span style="color: {open_text_color};">{kline.open}</span><br> \
                <span style="color: {high_text_color};">最高价</span><br> \
                <span style="color: {high_text_color};">{kline.high}</span><br> \
                <span style="color: {low_text_color};">最低价</span><br> \
                <span style="color: {low_text_color};">{kline.low}</span><br> \
                <span style="color: {close_text_color};">收盘价</span><br> \
                <span style="color: {close_text_color};">{kline.close}</span><br> \
                <span>成交量</span><br> \
                <span>{kline.volume}</span><br> \
                <span>持仓量</span><br> \
                <span>{int(kline.open_interest)}</span><br> \
                {final_price_text} \
            </div>'
        )

        # 显示所有的主图技术指标
        html = '<div style="text-align: right; font-size: 18px;">'
        for indicator_name in self.master.indicator_data:
            value: float = self.master.indicator_data[indicator_name][x_axis]
            color_value: str = self.master.indicator_color_map[indicator_name]
            html += self._ind_str(color_value, indicator_name, value)
        html += "</div>"
        self.__text_sig.setHtml(html)

        # 显示所有的主图技术指标
        html = '<div style="text-align: right; font-size: 18px;">'
        for indicator_name in self.master.sub_indicator_data:
            value: float = self.master.sub_indicator_data[indicator_name][x_axis]
            color_value: str = self.master.sub_indicator_color_map[indicator_name]
            html += self._ind_str(color_value, indicator_name, value)
        html += "</div>"
        self.__text_sub_sig.setHtml(html)

        self.__text_volume.setHtml(
            f'<div style="text-align: right"> \
                <span style="color: white; font-size: 18px;">VOL: {kline.volume}</span> \
            </div>'
        )

        # 坐标轴宽度
        right_axis: pg.AxisItem = self.views[0].getAxis('right')
        bottom_axis: pg.AxisItem = self.views[2].getAxis('bottom')
        offset = QtCore.QPointF(right_axis.width(), bottom_axis.height())

        # 各个顶点
        top_left: list[QtCore.QPointF] = [
            self.views[i].getViewBox().mapSceneToView(
                self.rects[i].topLeft()
            )
            for i in range(3)
        ]

        bottom_right: list[QtCore.QPointF] = [
            self.views[i].getViewBox().mapSceneToView(
                self.rects[i].bottomRight() - offset
            )
            for i in range(3)
        ]

        # 显示价格
        for i in range(3):
            if self.h_line_visible[i]:
                pos_y = y_axis if i == 0 else self.y_axises[i]
                self.text_prices[i].setHtml(
                    f'<div style="text-align: right"> \
                        <span style="color: white; font-size: 18px;">{pos_y:.3f}</span> \
                    </div>'
                )
                self.text_prices[i].setPos(bottom_right[i].x(), pos_y)
                self.text_prices[i].show()
            else:
                self.text_prices[i].hide()

        # 设置坐标
        self.__text_info.setPos(top_left[0])
        self.__text_sig.setPos(bottom_right[0].x(), top_left[0].y())
        self.__text_sub_sig.setPos(bottom_right[2].x(), top_left[2].y())
        self.__text_volume.setPos(bottom_right[1].x(), top_left[1].y())