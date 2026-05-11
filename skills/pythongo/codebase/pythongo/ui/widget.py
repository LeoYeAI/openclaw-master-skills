import os
import sys
import time
from collections import defaultdict
from threading import Thread, current_thread, main_thread
from traceback import format_exc

import numpy as np
import pandas as pd
import qdarkstyle
from PyQt5 import QtCore
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QWidget

from pythongo.base import BaseStrategy as ParentStrategy
from pythongo.classdef import KLineData
from pythongo.infini import write_log
from pythongo.ui.drawer import KLineWidget


class BaseStrategy(ParentStrategy):
    """带 UI 的基础策略模版"""

    qt_thread: Thread = None
    qt_gui_support: "QtGuiSupport" = None

    def __init__(self) -> None:
        super().__init__()
        self.widget: KLWidget = None
        """K 线组件"""

        self._start_flag = False
        """内部启动标识"""

    @property
    def main_indicator_data(self) -> dict[str, float]:
        """主图指标数据"""
        return {}

    @property
    def main_indicator(self) -> list[str]:
        """主图显示指标名"""
        return list(self.main_indicator_data.keys())

    @property
    def sub_indicator_data(self) -> dict[str, float]:
        """副图指标数据"""
        return {}

    @property
    def sub_indicator(self) -> list[str]:
        """副图显示指标名"""
        return list(self.sub_indicator_data.keys())

    def on_init(self) -> None:
        super().on_init()
        self.init_widget()

    def on_start(self) -> None:
        self._start_flag = True

        super().on_start()

        if self.widget:
            self.widget.load_data_signal.emit()

    def on_stop(self) -> None:
        self._start_flag = False

        super().on_stop()

        self.close_gui()

    def close_gui(self) -> None:
        """关闭界面"""
        if self.qt_gui_support:
            self.qt_gui_support.hide_signal.emit(self)

    def init_widget(self) -> None:
        """实例化 Widget"""
        for _ in range(10):
            if not self.qt_gui_support:
                time.sleep(0.5)

        if self.qt_gui_support:
            self.qt_gui_support.init_widget_signal.emit(self)

    @classmethod
    def start_qt_gui_support(cls) -> None:
        """启动 QT 界面"""
        if cls.qt_thread is None:
            cls.qt_thread = Thread(target=cls.start_qt)
            cls.qt_thread.setDaemon(True)
            cls.qt_thread.start()

    @classmethod
    def start_qt(cls) -> None:
        # 启动 QT 循环
        try:
            app = QApplication([''])
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
            base_dir = os.path.split(os.path.realpath(__file__))[0]
            cfg_file = QtCore.QFile(os.path.join(base_dir, 'style.qss'))
            cfg_file.open(QtCore.QFile.ReadOnly)
            style_sheet = bytes(cfg_file.readAll()).decode('utf-8')
            app.setStyleSheet(style_sheet)
            cls.qt_gui_support = QtGuiSupport()
            sys.exit(app.exec_())
        except:
            cls.qt_thread = None
            write_log(format_exc())


if current_thread() is not main_thread():
    BaseStrategy.start_qt_gui_support() #: 启动 QT 界面


class QtGuiSupport(QtCore.QObject):
    """QT 辅助类"""
    init_widget_signal = QtCore.pyqtSignal(object)
    hide_signal = QtCore.pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self.widget_container: dict[str, KLWidget] = {}
        self.init_widget_signal.connect(self.init_strategy_widget)
        self.hide_signal.connect(self.hide_strategy_widget)

    def init_strategy_widget(self, s: BaseStrategy) -> None:
        """初始化 widget 或对策略类的 widget 重新赋值"""
        if self.widget_container.get(s.strategy_name) is None:
            s.widget = KLWidget(s)
            self.widget_container[s.strategy_name] = s.widget
        else:
            s.widget = self.widget_container[s.strategy_name]
            self.widget_container[s.strategy_name].strategy = s

        s.widget.kline_widget.set_title(s.params_map.instrument_id)

    def hide_strategy_widget(self, s: BaseStrategy) -> None:
        """隐藏 widget"""
        if self.widget_container.get(s.strategy_name):
            self.widget_container[s.strategy_name].hide()
            self.widget_container[s.strategy_name].kline_widget.cancel_xrange_event()


class KLWidget(QWidget):
    """K 线组件"""
    update_kline_signal = QtCore.pyqtSignal(dict)
    load_data_signal = QtCore.pyqtSignal()
    set_xrange_event_signal = QtCore.pyqtSignal()

    def __init__(self, strategy: BaseStrategy, parent=None):
        super().__init__(parent)
        self.strategy = strategy
        self.kline_widget = KLineWidget()
        self.init_ui()
        self.klines: list[dict] = []
        self.all_indicator_data = defaultdict(list)

        self.update_kline_signal.connect(self.update_kline)
        self.load_data_signal.connect(self.load_kline_data)
        self.set_xrange_event_signal.connect(self.kline_widget.set_xrange_event)

        self._first_add = True

    @property
    def main_indicator(self) -> list[str]:
        """主图指标"""
        return self.strategy.main_indicator

    @property
    def sub_indicator(self) -> list[str]:
        """副图指标"""
        return self.strategy.sub_indicator

    def init_ui(self) -> None:
        """初始化界面"""
        self.setWindowTitle(f"策略 - {self.strategy.strategy_name}")

        # 整合布局
        vbox = QVBoxLayout()
        vbox.addWidget(self.kline_widget)
        self.setLayout(vbox)
        self.resize(750, 850)

        _work_dir = os.path.dirname(os.path.dirname(__file__))
        self.setWindowIcon(QIcon(os.path.join(_work_dir, "ui", "infinitrader.png")))

    def recv_kline(self, data: dict[str, float | KLineData]) -> None:
        """
        收取 K 线

        Args:
            data: 数据容器，包含 K 线数据、价格信号、指标数据
                e.g. : `{"kline": kline_data, "signal_price": 0.0, "MA": 0.0}`
        """

        if self.strategy._start_flag:
            self.update_kline_signal.emit(data)
        else:
            if self._first_add:
                self.clear()
                self._first_add = False
            self.klines.append(data["kline"].to_json())
            for s in (self.main_indicator + self.sub_indicator):
                self.all_indicator_data[s].append(data[s])

        self.update_bs_signal(data.get("signal_price", 0))

    def update_kline(self, data: dict) -> None:
        """更新 K 线"""
        kline: KLineData = data["kline"]

        if (
            len(self.klines) >= 2
            and (self.klines[-2]["datetime"] < kline.datetime < self.klines[-1]["datetime"])
        ):
            """丢数据"""
            self.klines.insert(-1, kline.to_json())
            self.kline_widget.insert_kline(kline)

            for indicator_name in self.main_indicator:
                self.all_indicator_data[indicator_name].insert(-1, data[indicator_name])

            self.update_indicator_data(new_data=True)

            return

        is_new_kline = self.kline_widget.update_kline(kline)

        if is_new_kline:
            self.klines.append(kline.to_json())
        else:
            self.klines[-1] = kline.to_json()

        self.update_indicator_data(data, new_data=is_new_kline)

        self.kline_widget.update_candle_signal.emit()

        self.renew_main_indicator()
        self.renew_sub_indicator()

    def update_bs_signal(self, price: float) -> None:
        """设置买卖信号的坐标"""
        if price:
            index = len(self.klines) - 1
            self.kline_widget.buy_sell_signals[index] = price

            if self.strategy._start_flag:
                self.kline_widget.add_buy_sell_signal.emit(index)

    def load_kline_data(self) -> None:
        """载入历史 K 线数据"""
        if self._first_add is False:
            """只有调用了 recv_kline 才需要重新载入数据"""
            pdData = pd.DataFrame(self.klines).set_index("datetime")
            pdData["open_interest"] = pdData["open_interest"].astype(float)
            self.kline_widget.load_data(pdData)
            self.kline_widget.draw_marks_signal.emit()
            self.update_indicator_data()
            self.kline_widget.plot_all()
            self.set_main_indicator()
            self.set_sub_indicator()
        else:
            self.set_xrange_event_signal.emit()

        self.kline_widget.set_title(self.strategy.params_map.instrument_id)
        self._first_add = True
        self.show()

    def clear(self) -> None:
        """清空数据"""
        self.klines.clear()
        self.all_indicator_data.clear()
        self.kline_widget.clear_data()
        self.kline_widget.plot_all()

    def update_indicator_data(self, data: dict = None, new_data: bool = True) -> None:
        """更新指标数组中的数据"""
        if data:
            for s in self.main_indicator + self.sub_indicator:
                if new_data:
                    self.all_indicator_data[s].append(data[s])
                else:
                    self.all_indicator_data[s][-1] = data[s]

        for s in self.main_indicator:
            _indicator_data: np.ndarray = (
                np.array(self.all_indicator_data[s])
                if new_data
                else np.append(self.kline_widget.indicator_data[s][:-1], data[s])
            )
            self.kline_widget.indicator_data[s] = _indicator_data

        for s in self.sub_indicator:
            _indicator_data: np.ndarray = (
                np.array(self.all_indicator_data[s])
                if new_data
                else np.append(self.kline_widget.sub_indicator_data[s][:-1], data[s])
            )
            self.kline_widget.sub_indicator_data[s] = _indicator_data

    def renew_main_indicator(self) -> None:
        """更新主图指标"""
        for indicator_name in self.kline_widget.indicator_data:
            self.kline_widget.indicator_plot_items[indicator_name].setData(
                self.kline_widget.indicator_data[indicator_name],
                pen=self.kline_widget.indicator_color_map[indicator_name],
                name=indicator_name
            )

    def set_main_indicator(self) -> None:
        """设置主图指标"""
        self.kline_widget.set_indicator(
            indicator=self.main_indicator,
            datas=self.all_indicator_data
        )

    def renew_sub_indicator(self) -> None:
        """更新副图指标"""
        for indicator_name in self.kline_widget.sub_indicator_data:
            self.kline_widget.sub_indicator_plot_items[indicator_name].setData(
                self.kline_widget.sub_indicator_data[indicator_name],
                pen=self.kline_widget.sub_indicator_color_map[indicator_name],
                name=indicator_name
            )

    def set_sub_indicator(self) -> None:
        """设置副图指标"""
        self.kline_widget.set_indicator(
            indicator=self.sub_indicator,
            datas=self.all_indicator_data,
            main_plot=False
        )

    def closeEvent(self, evt: QCloseEvent) -> None:
        """继承关闭事件"""
        if self.strategy._start_flag:
            QMessageBox.warning(None, "警告", "策略启动时无法关闭，暂停时会自动关闭！")
        else:
            self.hide()
        evt.ignore()
