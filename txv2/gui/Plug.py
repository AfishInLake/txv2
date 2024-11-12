#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/3 11:35
# @Author  : afish
# @File    : Plug.py
from abc import ABC, abstractmethod



class PluginInterface(ABC):
    window = None

    @abstractmethod
    def get_tool(self):
        """
        获取工具栏名称,没有将新建一个
        """
        pass

    @abstractmethod
    def get_menu(self):
        """
        获取插件名称将在tool栏下新建一个此名称的插件
        """
        pass

    @abstractmethod
    def start(self):
        """
        插件启动
        """
        pass
