#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os,sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import  Qt


class FrameDemo(QWidget):
    def __init__(self):
        super(FrameDemo, self).__init__()
        self.setFixedSize(500,450)
        self.setWindowTitle("QFrame Demo演示")
        self.layout = QVBoxLayout(self)
        self.demoframe = QFrame()
        self.demoframe.setFrameStyle(QFrame.NoFrame|QFrame.Plain)
        self.demoframe.setLineWidth(1)
        self.demoframe.setMidLineWidth(1)
        self.demoframe.setFixedSize(480,200)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.demoframe)
        self.layout.addSpacing(20)
        self.layout.addStretch()
        # 设置 lineWidth
        childlayout01 = QHBoxLayout()
        childlayout01.addWidget(QLabel("线宽: "))
        self.combox01 = QComboBox()
        self.combox01.addItems(["1","2","3"])
        childlayout01.addWidget(self.combox01)
        self.btn01 = QPushButton("设置线宽")
        childlayout01.addWidget(self.btn01)
        self.layout.addLayout(childlayout01)
        # 设置MidLineWidth
        childlayout02 = QHBoxLayout()
        childlayout02.addWidget(QLabel("MidLineWidth: "))
        self.combox02 = QComboBox()
        self.combox02.addItems(["1","2","3"])
        childlayout02.addWidget(self.combox02)
        self.btn02 = QPushButton("设置midline线宽")
        childlayout02.addWidget(self.btn02)
        self.layout.addLayout(childlayout02)
        # 设置FrameShape
        childlayout03 = QHBoxLayout()
        childlayout03.addWidget(QLabel("FrameShape: "))
        self.combox03 = QComboBox()
        self.combox03.addItems(["NoFrame","Box","Panel","StyledPanel"])
        childlayout03.addWidget(self.combox03)
        self.btn03 = QPushButton("设置FrameShape")
        childlayout03.addWidget(self.btn03)
        self.layout.addLayout(childlayout03)
        # 设置FrameShadow
        childlayout04 = QHBoxLayout()
        childlayout04.addWidget(QLabel("FrameShadow: "))
        self.combox04 = QComboBox()
        self.combox04.addItems(["Plain","Raised","Sunken"])
        childlayout04.addWidget(self.combox04)
        self.btn04 = QPushButton("设置FrameShadow")
        childlayout04.addWidget(self.btn04)
        self.layout.addLayout(childlayout04)
        self.setall_btn = QPushButton("一键设置")
        self.layout.addWidget(self.setall_btn)
        #信号槽
        self.btn01.clicked.connect(self.btn_setLineWidth)
        self.btn02.clicked.connect(self.btn_setMidLineWidth)
        self.btn03.clicked.connect(self.btn_setFrameShape)
        self.btn04.clicked.connect(self.btn_setFrameShadow)
        self.setall_btn.clicked.connect(self.btn_set_all)

    def btn_set_all(self):
        self.btn_setLineWidth()
        self.btn_setMidLineWidth()
        self.btn_setFrameShape()
        self.btn_setFrameShadow()

    def btn_setLineWidth(self):
        value = int(self.combox01.currentText())
        self.demoframe.setLineWidth(value)

    def btn_setMidLineWidth(self):
        value = int(self.combox02.currentText())
        self.demoframe.setMidLineWidth(value)

    def btn_setFrameShape(self):
        if "NoFrame" == self.combox03.currentText():
            self.demoframe.setFrameShape(QFrame.NoFrame)
        elif "Box" == self.combox03.currentText():
            self.demoframe.setFrameShape(QFrame.Box)
        elif "Panel" == self.combox03.currentText():
            self.demoframe.setFrameShape(QFrame.Panel)
        elif "StyledPanel" == self.combox03.currentText():
            self.demoframe.setFrameShape(QFrame.StyledPanel)
        else:
            pass

    def btn_setFrameShadow(self):
        if "Plain" == self.combox04.currentText():
            self.demoframe.setFrameShadow(QFrame.Plain)
        elif "Raised" == self.combox04.currentText():
            print("=2=")
            self.demoframe.setFrameShadow(QFrame.Raised)
        elif "Sunken" == self.combox04.currentText():
            self.demoframe.setFrameShadow(QFrame.Sunken)
        else:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = FrameDemo()
    test.show()
    sys.exit(app.exec_())
