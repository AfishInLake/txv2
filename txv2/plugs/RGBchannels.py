#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/11 11:25
# @Author  : afish
# @File    : RGBchannels.py
import cv2
from PyQt5.QtWidgets import QPushButton

from txv2.gui.Plug import PluginInterface


class Plugin(PluginInterface):

    def get_tool(self):
        return "工具"

    def get_menu(self):
        return "RGB图像单通道提取"

    def start(self):
        self.window.clear_buttons()
        # 创建R、G、B按钮
        r_button = QPushButton('R 通道', self.window)
        g_button = QPushButton('G 通道', self.window)
        b_button = QPushButton('B 通道', self.window)

        # 绑定事件
        r_button.clicked.connect(lambda: self.extract_rgb_channel('R'))
        g_button.clicked.connect(lambda: self.extract_rgb_channel('G'))
        b_button.clicked.connect(lambda: self.extract_rgb_channel('B'))

        # 添加按钮到右侧布局
        self.window.left_widget_bottom.addWidget(r_button)
        self.window.left_widget_bottom.addWidget(g_button)
        self.window.left_widget_bottom.addWidget(b_button)

    def extract_rgb_channel(self, channel):
        """提取RGB图像的单通道"""
        if self.window.image is None:
            self.window.show_message("未加载图像。")
            return
        if channel not in ['R', 'G', 'B']:
            self.window.show_message("通道选择错误，请选择 'R', 'G', 或 'B'。")
            return

        channels = cv2.split(self.window.image)
        if channel == 'R':
            self.window.show_image(channels[2])  # 红色通道
        elif channel == 'G':
            self.window.show_image(channels[1])  # 绿色通道
        elif channel == 'B':
            self.window.show_image(channels[0])  # 蓝色通道
