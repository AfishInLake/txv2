#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/11/3 11:22
# @Author  : afish
# @File    : main.py
import sys

from PyQt5.QtWidgets import QApplication

from txv2.gui.MainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show() 
    sys.exit(app.exec_())
