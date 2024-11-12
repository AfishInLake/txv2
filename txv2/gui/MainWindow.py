#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/3 11:23
# @Author  : afish
# @File    : MainWindow.py
import functools
import inspect
import os
import tempfile
import zipfile
from importlib.machinery import SourceFileLoader
from typing import List

import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFileDialog, QMessageBox

from txv2.gui.MenuBar import MenuBar
from txv2.gui.Plug import PluginInterface
from settings import DIR


def exception_handler(method):
    """
    装饰器，用于捕获类方法中的异常并展示报错。
    """

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as e:
            args[0].show_message(str(e))

    return wrapper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和尺寸
        self.setWindowTitle("图像处理应用程序")
        self.setGeometry(100, 100, 800, 600)
        self.addCache()
        self.plugs: List[PluginInterface] = self.add_plugs()

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        # 设置主窗口的布局
        self.create_main_layout()

    def create_main_layout(self):
        # 主窗口的中心widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # 创建主布局
        self.main_layout = QHBoxLayout()

        # 左侧布局
        self.left_layout = QVBoxLayout()

        # 用于显示原始图像的 QLabel（占左侧的上半部分）
        self.image_label = QLabel("", self)  # 原始图像
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(250)  # 设置左侧上部分的高度

        # 添加左侧的上半部分用于显示图片
        self.left_layout.addWidget(self.image_label, 1)

        # 左侧的下半部分（占二分之一）
        self.left_widget_bottom = QVBoxLayout()  # 左侧下半部分区域
        self.left_layout.addLayout(self.left_widget_bottom, 1)

        # 右侧占空比为4
        self.right_widget = QLabel("", self)  # 右侧图像处理结果区域
        self.right_widget.setAlignment(Qt.AlignCenter)
        self.right_widget.setStyleSheet("background-color: white;")

        self.main_layout.addLayout(self.left_layout, 1)
        self.main_layout.addWidget(self.right_widget, 3)

        # 将布局设置为central_widget的布局
        central_widget.setLayout(self.main_layout)

    @exception_handler
    def add_plugs(self, *args, **kwargs) -> List[PluginInterface]:
        """
        添加插件并返回插件列表
        :return:
        """
        plugins = []
        plugin_dir = DIR / 'plugs'
        # 遍历插件目录下的所有.zip文件
        for filename in os.listdir(plugin_dir):
            if filename.endswith('.zip'):
                zip_path = plugin_dir / filename
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        zip_ref.extractall(tmpdirname)  # 解压到临时目录
                        from pathlib import Path
                        tmp_dir = Path(tmpdirname)

                        # 遍历解压目录下的所有 .py 文件
                        for py_file in tmp_dir.glob('*.py'):
                            module_name = py_file.stem  # 获取文件名作为模块名

                            # 使用 SourceFileLoader 加载模块
                            loader = SourceFileLoader(module_name, str(py_file))
                            module = loader.load_module()

                            # 查找符合 PluginInterface 的类
                            for name, obj in inspect.getmembers(module):
                                if inspect.isclass(obj) and issubclass(obj, PluginInterface) and obj is not PluginInterface:
                                    plugin_instance = obj()  # 实例化插件
                                    plugin_instance.window = self
                                    plugins.append(plugin_instance)
        return plugins

    @exception_handler
    def addCache(self, *args, **kwargs):
        # 定义文件路径
        tmp_file_path = DIR / 'tmp'
        # 检查文件是否存在，如果不存在则创建
        if not tmp_file_path.exists():
            try:
                os.makedirs(tmp_file_path, exist_ok=True)
            except OSError as e:
                self.show_message(f"创建缓存目录时出错：{e}")

    @exception_handler
    def open_file(self, *args, **kwargs):
        # 打开文件的功能
        file_name, _ = QFileDialog.getOpenFileName(self, "打开文件", "", "图像文件 (*.png *.jpg *.bmp);;所有文件 (*)")
        if file_name:
            self.name = file_name.split("/")[-1]
            with open(file_name, 'rb') as f:
                image_data = f.read()
            # 将二进制数据转换为 NumPy 数组
            image_array = np.asarray(bytearray(image_data), dtype=np.uint8)
            # 使用 cv2.imdecode 解码
            self.image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if self.image is None:
                self.show_message("图像加载失败，请检查文件路径是否存在或有中文。")
                return None
            self.display_image(self.image)

    @exception_handler
    def display_image(self, img, *args, **kwargs):
        """将OpenCV图像转换为QImage并显示在界面上"""
        if img.ndim == 2:  # 灰度图像
            height, width = img.shape
            q_image = QImage(img.data, width, height, width, QImage.Format_Grayscale8)
        else:  # 彩色图像
            height, width, channel = img.shape
            bytes_per_line = 3 * width
            q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        # 将QImage转换为QPixmap并显示
        self.image_label.setPixmap(QPixmap.fromImage(q_image).scaled(self.image_label.size(), Qt.KeepAspectRatio))

    @exception_handler
    def show_image(self, img, *args, **kwargs):
        """显示图像"""
        self.saveimg = img
        if img.ndim == 2:  # 灰度图像
            height, width = img.shape
            q_image = QImage(img.data, width, height, width, QImage.Format_Grayscale8)
        else:  # 彩色图像
            height, width, channel = img.shape
            bytes_per_line = 3 * width
            q_image = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        # 将QImage转换为QPixmap并显示
        self.right_widget.setPixmap(QPixmap.fromImage(q_image).scaled(self.right_widget.size(), Qt.KeepAspectRatio))

    def show_message(self, message, type='error', *args, **kwargs):
        """显示消息框"""
        msg_box = QMessageBox()
        if type == 'error':
            msg_box.setIcon(QMessageBox.Critical)
        else:
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(type)
        msg_box.setText(message)
        msg_box.exec_()

    def save(self):
        pass

    @exception_handler
    def clear_buttons(self, *args, **kwargs):
        """清除左侧下半部分的按钮"""
        while self.left_widget_bottom.count():
            item = self.left_widget_bottom.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
