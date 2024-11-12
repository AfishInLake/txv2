#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/3 11:23
# @Author  : afish
# @File    : MenuBar.py
from typing import List

from PyQt5.QtWidgets import QMenuBar, QAction, QMenu

from txv2.gui.Plug import PluginInterface


class MenuBar(QMenuBar):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.plugs: List[PluginInterface] = self.main_window.plugs
        # 文件菜单
        file_menu = self.addMenu("文件")
        # 文件子级菜单项
        open_action = QAction("打开文件", self)
        open_action.triggered.connect(self.main_window.open_file)
        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.main_window.save)
        scan_menu = QAction("扫描插件", self)
        scan_menu.triggered.connect(self.create_menu_bar)
        # 添加分隔线
        separator = QAction(self)
        separator.setSeparator(True)
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(scan_menu)
        file_menu.addAction(separator)  # 添加分隔线
        file_menu.addAction(exit_action)

        self.create_menu_bar()

    def add_plugin_to_menu(self, plugin_name:str, menu: QMenu, plugin_instance):
        # 这里可以根据插件名称决定挂载到哪个菜单
        # 如果有同名就不需要添加
        for action in menu.actions():
            if action.text() == plugin_name:
                return
        plugin_action = QAction(plugin_name, self)
        plugin_action.triggered.connect(plugin_instance.start)  # 连接插件的 start 方法
        menu.addAction(plugin_action)

    def create_menu_bar(self):
        for plugin in self.plugs:
            tool_name = plugin.get_tool()
            tool = self.find_menu_by_name(tool_name)
            menu = plugin.get_menu()
            if tool:  # 如果找到上级菜单，则添加插件
                self.add_plugin_to_menu(menu, tool, plugin)
            else:  # 如果未找到，则创建新的上级菜单
                new_menu = self.addMenu(tool_name)
                self.add_plugin_to_menu(menu, new_menu, plugin)

    def find_menu_by_name(self, name):
        for action in self.actions():
            menu = action.menu()
            if menu and menu.title() == name:
                return menu
        return None
