# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'projector_pdu.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1548, 793)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Arial")
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(860, 40, 511, 271))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.frame_2.setFont(font)
        self.frame_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(20, 10, 51, 21))
        self.label_2.setObjectName("label_2")
        self.serial_selection = QtWidgets.QComboBox(self.frame_2)
        self.serial_selection.setGeometry(QtCore.QRect(90, 10, 87, 21))
        self.serial_selection.setObjectName("serial_selection")
        self.baud_rate = QtWidgets.QComboBox(self.frame_2)
        self.baud_rate.setGeometry(QtCore.QRect(90, 40, 87, 21))
        self.baud_rate.setObjectName("baud_rate")
        self.baud_rate.addItem("")
        self.baud_rate.addItem("")
        self.baud_rate.addItem("")
        self.baud_rate.addItem("")
        self.baud_rate.addItem("")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setGeometry(QtCore.QRect(20, 40, 51, 21))
        self.label_4.setObjectName("label_4")
        self.refresh_port = QtWidgets.QPushButton(self.frame_2)
        self.refresh_port.setGeometry(QtCore.QRect(20, 72, 161, 28))
        self.refresh_port.setObjectName("refresh_port")
        self.open_port = QtWidgets.QPushButton(self.frame_2)
        self.open_port.setGeometry(QtCore.QRect(20, 116, 161, 28))
        self.open_port.setObjectName("open_port")
        self.close_port = QtWidgets.QPushButton(self.frame_2)
        self.close_port.setGeometry(QtCore.QRect(20, 160, 161, 28))
        self.close_port.setObjectName("close_port")
        self.label_11 = QtWidgets.QLabel(self.frame_2)
        self.label_11.setGeometry(QtCore.QRect(190, 10, 441, 21))
        self.label_11.setObjectName("label_11")
        self.receive_data_area = QtWidgets.QPlainTextEdit(self.frame_2)
        self.receive_data_area.setGeometry(QtCore.QRect(190, 40, 301, 61))
        self.receive_data_area.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.receive_data_area.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.receive_data_area.setUndoRedoEnabled(False)
        self.receive_data_area.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
        self.receive_data_area.setReadOnly(True)
        self.receive_data_area.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.receive_data_area.setObjectName("receive_data_area")
        self.label_13 = QtWidgets.QLabel(self.frame_2)
        self.label_13.setGeometry(QtCore.QRect(398, 287, 341, 221))
        self.label_13.setObjectName("label_13")
        self.input_data = QtWidgets.QTextEdit(self.frame_2)
        self.input_data.setGeometry(QtCore.QRect(190, 160, 301, 61))
        self.input_data.setMaximumSize(QtCore.QSize(1677721, 1677721))
        self.input_data.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.input_data.setObjectName("input_data")
        self.label_12 = QtWidgets.QLabel(self.frame_2)
        self.label_12.setGeometry(QtCore.QRect(190, 120, 301, 21))
        self.label_12.setObjectName("label_12")
        self.send_data = QtWidgets.QPushButton(self.frame_2)
        self.send_data.setGeometry(QtCore.QRect(20, 200, 161, 28))
        self.send_data.setAutoDefault(False)
        self.send_data.setObjectName("send_data")
        self.label_6 = QtWidgets.QLabel(self.frame_2)
        self.label_6.setGeometry(QtCore.QRect(60, 240, 91, 20))
        self.label_6.setMinimumSize(QtCore.QSize(0, 20))
        self.label_6.setObjectName("label_6")
        self.port_status = QtWidgets.QLabel(self.frame_2)
        self.port_status.setGeometry(QtCore.QRect(200, 240, 131, 20))
        self.port_status.setMinimumSize(QtCore.QSize(0, 20))
        self.port_status.setText("")
        self.port_status.setObjectName("port_status")
        self.frame1 = QtWidgets.QFrame(self.centralwidget)
        self.frame1.setGeometry(QtCore.QRect(30, 40, 821, 681))
        self.frame1.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.frame1.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame1.setLineWidth(1)
        self.frame1.setObjectName("frame1")
        self.frame_8 = QtWidgets.QFrame(self.frame1)
        self.frame_8.setGeometry(QtCore.QRect(380, 190, 421, 161))
        self.frame_8.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.frame_8.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setLineWidth(2)
        self.frame_8.setMidLineWidth(1)
        self.frame_8.setObjectName("frame_8")
        self.label_31 = QtWidgets.QLabel(self.frame_8)
        self.label_31.setGeometry(QtCore.QRect(20, 60, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_31.setFont(font)
        self.label_31.setObjectName("label_31")
        self.temp1Label = QtWidgets.QLabel(self.frame_8)
        self.temp1Label.setGeometry(QtCore.QRect(110, 60, 41, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.temp1Label.setFont(font)
        self.temp1Label.setObjectName("temp1Label")
        self.label_33 = QtWidgets.QLabel(self.frame_8)
        self.label_33.setGeometry(QtCore.QRect(160, 60, 21, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_33.setFont(font)
        self.label_33.setObjectName("label_33")
        self.label_32 = QtWidgets.QLabel(self.frame_8)
        self.label_32.setGeometry(QtCore.QRect(20, 90, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_32.setFont(font)
        self.label_32.setObjectName("label_32")
        self.temp2Label = QtWidgets.QLabel(self.frame_8)
        self.temp2Label.setGeometry(QtCore.QRect(110, 90, 41, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.temp2Label.setFont(font)
        self.temp2Label.setObjectName("temp2Label")
        self.label_35 = QtWidgets.QLabel(self.frame_8)
        self.label_35.setGeometry(QtCore.QRect(160, 90, 21, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_35.setFont(font)
        self.label_35.setObjectName("label_35")
        self.label_36 = QtWidgets.QLabel(self.frame_8)
        self.label_36.setGeometry(QtCore.QRect(140, 20, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_36.setFont(font)
        self.label_36.setObjectName("label_36")
        self.label_37 = QtWidgets.QLabel(self.frame_8)
        self.label_37.setGeometry(QtCore.QRect(340, 20, 41, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_37.setFont(font)
        self.label_37.setObjectName("label_37")
        self.tempFlagLabel = QtWidgets.QLabel(self.frame_8)
        self.tempFlagLabel.setGeometry(QtCore.QRect(380, 20, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.tempFlagLabel.setFont(font)
        self.tempFlagLabel.setObjectName("tempFlagLabel")
        self.updateTempButton = QtWidgets.QPushButton(self.frame_8)
        self.updateTempButton.setGeometry(QtCore.QRect(10, 20, 121, 31))
        self.updateTempButton.setMaximumSize(QtCore.QSize(121, 16777215))
        self.updateTempButton.setObjectName("updateTempButton")
        self.label_34 = QtWidgets.QLabel(self.frame_8)
        self.label_34.setGeometry(QtCore.QRect(20, 120, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_34.setFont(font)
        self.label_34.setObjectName("label_34")
        self.temp3Label = QtWidgets.QLabel(self.frame_8)
        self.temp3Label.setGeometry(QtCore.QRect(110, 120, 41, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.temp3Label.setFont(font)
        self.temp3Label.setObjectName("temp3Label")
        self.label_38 = QtWidgets.QLabel(self.frame_8)
        self.label_38.setGeometry(QtCore.QRect(160, 120, 21, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_38.setFont(font)
        self.label_38.setObjectName("label_38")
        self.label_39 = QtWidgets.QLabel(self.frame_8)
        self.label_39.setGeometry(QtCore.QRect(200, 60, 51, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_39.setFont(font)
        self.label_39.setObjectName("label_39")
        self.label_40 = QtWidgets.QLabel(self.frame_8)
        self.label_40.setGeometry(QtCore.QRect(200, 90, 51, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_40.setFont(font)
        self.label_40.setObjectName("label_40")
        self.label_41 = QtWidgets.QLabel(self.frame_8)
        self.label_41.setGeometry(QtCore.QRect(200, 120, 51, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_41.setFont(font)
        self.label_41.setObjectName("label_41")
        self.temp1VoltageLabel = QtWidgets.QLabel(self.frame_8)
        self.temp1VoltageLabel.setGeometry(QtCore.QRect(250, 60, 61, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.temp1VoltageLabel.setFont(font)
        self.temp1VoltageLabel.setObjectName("temp1VoltageLabel")
        self.temp2VoltageLabel = QtWidgets.QLabel(self.frame_8)
        self.temp2VoltageLabel.setGeometry(QtCore.QRect(250, 90, 61, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.temp2VoltageLabel.setFont(font)
        self.temp2VoltageLabel.setObjectName("temp2VoltageLabel")
        self.temp3VoltageLabel = QtWidgets.QLabel(self.frame_8)
        self.temp3VoltageLabel.setGeometry(QtCore.QRect(250, 120, 61, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.temp3VoltageLabel.setFont(font)
        self.temp3VoltageLabel.setObjectName("temp3VoltageLabel")
        self.label_42 = QtWidgets.QLabel(self.frame_8)
        self.label_42.setGeometry(QtCore.QRect(320, 60, 21, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_42.setFont(font)
        self.label_42.setObjectName("label_42")
        self.label_43 = QtWidgets.QLabel(self.frame_8)
        self.label_43.setGeometry(QtCore.QRect(320, 90, 21, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_43.setFont(font)
        self.label_43.setObjectName("label_43")
        self.label_44 = QtWidgets.QLabel(self.frame_8)
        self.label_44.setGeometry(QtCore.QRect(320, 120, 21, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_44.setFont(font)
        self.label_44.setObjectName("label_44")
        self.updateTempEdit = QtWidgets.QLineEdit(self.frame1)
        self.updateTempEdit.setGeometry(QtCore.QRect(590, 210, 121, 31))
        self.updateTempEdit.setMaximumSize(QtCore.QSize(121, 16777215))
        self.updateTempEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.updateTempEdit.setObjectName("updateTempEdit")
        self.frame_6 = QtWidgets.QFrame(self.frame1)
        self.frame_6.setGeometry(QtCore.QRect(10, 560, 791, 51))
        self.frame_6.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.frame_6.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setLineWidth(2)
        self.frame_6.setMidLineWidth(3)
        self.frame_6.setObjectName("frame_6")
        self.getSwVerButton = QtWidgets.QPushButton(self.frame_6)
        self.getSwVerButton.setGeometry(QtCore.QRect(10, 10, 121, 31))
        self.getSwVerButton.setObjectName("getSwVerButton")
        self.label_sw_version = QtWidgets.QLabel(self.frame_6)
        self.label_sw_version.setGeometry(QtCore.QRect(160, 9, 72, 31))
        self.label_sw_version.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_sw_version.setAlignment(QtCore.Qt.AlignCenter)
        self.label_sw_version.setObjectName("label_sw_version")
        self.savePduDataButton = QtWidgets.QPushButton(self.frame_6)
        self.savePduDataButton.setGeometry(QtCore.QRect(260, 10, 121, 31))
        self.savePduDataButton.setObjectName("savePduDataButton")
        self.frame = QtWidgets.QFrame(self.frame1)
        self.frame.setGeometry(QtCore.QRect(380, 10, 421, 161))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(2)
        self.frame.setMidLineWidth(1)
        self.frame.setObjectName("frame")
        self.label_30 = QtWidgets.QLabel(self.frame)
        self.label_30.setGeometry(QtCore.QRect(20, 110, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.label_30.setFont(font)
        self.label_30.setObjectName("label_30")
        self.motorBackButton = QtWidgets.QPushButton(self.frame)
        self.motorBackButton.setGeometry(QtCore.QRect(150, 20, 121, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.motorBackButton.sizePolicy().hasHeightForWidth())
        self.motorBackButton.setSizePolicy(sizePolicy)
        self.motorBackButton.setMaximumSize(QtCore.QSize(121, 16777215))
        self.motorBackButton.setObjectName("motorBackButton")
        self.motorStatuslabel = QtWidgets.QLabel(self.frame)
        self.motorStatuslabel.setGeometry(QtCore.QRect(150, 110, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.motorStatuslabel.setFont(font)
        self.motorStatuslabel.setObjectName("motorStatuslabel")
        self.motorStepsEdit = QtWidgets.QLineEdit(self.frame)
        self.motorStepsEdit.setGeometry(QtCore.QRect(290, 20, 121, 31))
        self.motorStepsEdit.setMaximumSize(QtCore.QSize(121, 16777215))
        self.motorStepsEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.motorStepsEdit.setObjectName("motorStepsEdit")
        self.motorForwardButton = QtWidgets.QPushButton(self.frame)
        self.motorForwardButton.setGeometry(QtCore.QRect(10, 20, 121, 31))
        self.motorForwardButton.setMaximumSize(QtCore.QSize(121, 16777215))
        self.motorForwardButton.setObjectName("motorForwardButton")
        self.autoTestMotorOpenButton = QtWidgets.QPushButton(self.frame)
        self.autoTestMotorOpenButton.setGeometry(QtCore.QRect(10, 70, 121, 31))
        self.autoTestMotorOpenButton.setMaximumSize(QtCore.QSize(121, 16777215))
        self.autoTestMotorOpenButton.setObjectName("autoTestMotorOpenButton")
        self.autoTestMotorCloseButton = QtWidgets.QPushButton(self.frame)
        self.autoTestMotorCloseButton.setGeometry(QtCore.QRect(150, 70, 121, 31))
        self.autoTestMotorCloseButton.setMaximumSize(QtCore.QSize(121, 16777215))
        self.autoTestMotorCloseButton.setObjectName("autoTestMotorCloseButton")
        self.motorStepsRoundEdit = QtWidgets.QLineEdit(self.frame)
        self.motorStepsRoundEdit.setGeometry(QtCore.QRect(290, 70, 121, 31))
        self.motorStepsRoundEdit.setMaximumSize(QtCore.QSize(121, 16777215))
        self.motorStepsRoundEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.motorStepsRoundEdit.setObjectName("motorStepsRoundEdit")
        self.totalRoundLabel = QtWidgets.QLabel(self.frame)
        self.totalRoundLabel.setGeometry(QtCore.QRect(330, 110, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.totalRoundLabel.setFont(font)
        self.totalRoundLabel.setObjectName("totalRoundLabel")
        self.frame_4 = QtWidgets.QFrame(self.frame1)
        self.frame_4.setGeometry(QtCore.QRect(10, 10, 351, 161))
        self.frame_4.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setLineWidth(2)
        self.frame_4.setMidLineWidth(1)
        self.frame_4.setObjectName("frame_4")
        self.fan3SpinBox = QtWidgets.QSpinBox(self.frame_4)
        self.fan3SpinBox.setGeometry(QtCore.QRect(220, 110, 71, 41))
        self.fan3SpinBox.setMaximum(100)
        self.fan3SpinBox.setProperty("value", 30)
        self.fan3SpinBox.setObjectName("fan3SpinBox")
        self.fan1HorizontalSlider = QtWidgets.QSlider(self.frame_4)
        self.fan1HorizontalSlider.setGeometry(QtCore.QRect(70, 20, 141, 21))
        self.fan1HorizontalSlider.setMaximum(100)
        self.fan1HorizontalSlider.setSingleStep(10)
        self.fan1HorizontalSlider.setSliderPosition(30)
        self.fan1HorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.fan1HorizontalSlider.setInvertedAppearance(False)
        self.fan1HorizontalSlider.setInvertedControls(False)
        self.fan1HorizontalSlider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.fan1HorizontalSlider.setTickInterval(10)
        self.fan1HorizontalSlider.setObjectName("fan1HorizontalSlider")
        self.fan2SpinBox = QtWidgets.QSpinBox(self.frame_4)
        self.fan2SpinBox.setGeometry(QtCore.QRect(220, 60, 71, 41))
        self.fan2SpinBox.setMaximum(100)
        self.fan2SpinBox.setProperty("value", 30)
        self.fan2SpinBox.setObjectName("fan2SpinBox")
        self.label_29 = QtWidgets.QLabel(self.frame_4)
        self.label_29.setGeometry(QtCore.QRect(10, 110, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_29.setFont(font)
        self.label_29.setObjectName("label_29")
        self.label_20 = QtWidgets.QLabel(self.frame_4)
        self.label_20.setGeometry(QtCore.QRect(10, 60, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")
        self.fan2HorizontalSlider = QtWidgets.QSlider(self.frame_4)
        self.fan2HorizontalSlider.setGeometry(QtCore.QRect(70, 70, 141, 21))
        self.fan2HorizontalSlider.setMaximum(100)
        self.fan2HorizontalSlider.setSliderPosition(30)
        self.fan2HorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.fan2HorizontalSlider.setObjectName("fan2HorizontalSlider")
        self.label_19 = QtWidgets.QLabel(self.frame_4)
        self.label_19.setGeometry(QtCore.QRect(10, 10, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.fan3HorizontalSlider = QtWidgets.QSlider(self.frame_4)
        self.fan3HorizontalSlider.setGeometry(QtCore.QRect(70, 120, 141, 21))
        self.fan3HorizontalSlider.setMaximum(100)
        self.fan3HorizontalSlider.setSliderPosition(30)
        self.fan3HorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.fan3HorizontalSlider.setObjectName("fan3HorizontalSlider")
        self.fan1SpinBox = QtWidgets.QSpinBox(self.frame_4)
        self.fan1SpinBox.setGeometry(QtCore.QRect(220, 10, 71, 41))
        self.fan1SpinBox.setMaximum(100)
        self.fan1SpinBox.setProperty("value", 30)
        self.fan1SpinBox.setObjectName("fan1SpinBox")
        self.fan1Detectlabel_2 = QtWidgets.QLabel(self.frame_4)
        self.fan1Detectlabel_2.setGeometry(QtCore.QRect(300, 20, 41, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.fan1Detectlabel_2.setFont(font)
        self.fan1Detectlabel_2.setObjectName("fan1Detectlabel_2")
        self.fan2Detectlabel = QtWidgets.QLabel(self.frame_4)
        self.fan2Detectlabel.setGeometry(QtCore.QRect(300, 70, 41, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.fan2Detectlabel.setFont(font)
        self.fan2Detectlabel.setObjectName("fan2Detectlabel")
        self.fan3Detectlabel = QtWidgets.QLabel(self.frame_4)
        self.fan3Detectlabel.setGeometry(QtCore.QRect(300, 120, 41, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.fan3Detectlabel.setFont(font)
        self.fan3Detectlabel.setObjectName("fan3Detectlabel")
        self.frame_5 = QtWidgets.QFrame(self.frame1)
        self.frame_5.setGeometry(QtCore.QRect(10, 190, 351, 161))
        self.frame_5.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setLineWidth(2)
        self.frame_5.setMidLineWidth(1)
        self.frame_5.setObjectName("frame_5")
        self.redSpinBox = QtWidgets.QSpinBox(self.frame_5)
        self.redSpinBox.setGeometry(QtCore.QRect(220, 10, 71, 41))
        self.redSpinBox.setMaximum(100)
        self.redSpinBox.setProperty("value", 30)
        self.redSpinBox.setObjectName("redSpinBox")
        self.label_14 = QtWidgets.QLabel(self.frame_5)
        self.label_14.setGeometry(QtCore.QRect(10, 60, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.blueHorizontalSlider = QtWidgets.QSlider(self.frame_5)
        self.blueHorizontalSlider.setGeometry(QtCore.QRect(70, 120, 141, 21))
        self.blueHorizontalSlider.setMaximum(100)
        self.blueHorizontalSlider.setSingleStep(10)
        self.blueHorizontalSlider.setSliderPosition(30)
        self.blueHorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.blueHorizontalSlider.setObjectName("blueHorizontalSlider")
        self.blueSpinBox = QtWidgets.QSpinBox(self.frame_5)
        self.blueSpinBox.setGeometry(QtCore.QRect(220, 110, 71, 41))
        self.blueSpinBox.setMaximum(100)
        self.blueSpinBox.setProperty("value", 30)
        self.blueSpinBox.setObjectName("blueSpinBox")
        self.label_10 = QtWidgets.QLabel(self.frame_5)
        self.label_10.setGeometry(QtCore.QRect(10, 10, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.greenHorizontalSlider = QtWidgets.QSlider(self.frame_5)
        self.greenHorizontalSlider.setGeometry(QtCore.QRect(70, 70, 141, 21))
        self.greenHorizontalSlider.setMaximum(100)
        self.greenHorizontalSlider.setSliderPosition(30)
        self.greenHorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.greenHorizontalSlider.setObjectName("greenHorizontalSlider")
        self.redHorizontalSlider = QtWidgets.QSlider(self.frame_5)
        self.redHorizontalSlider.setGeometry(QtCore.QRect(70, 20, 141, 21))
        self.redHorizontalSlider.setMaximum(100)
        self.redHorizontalSlider.setSingleStep(10)
        self.redHorizontalSlider.setSliderPosition(30)
        self.redHorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.redHorizontalSlider.setInvertedAppearance(False)
        self.redHorizontalSlider.setInvertedControls(False)
        self.redHorizontalSlider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.redHorizontalSlider.setTickInterval(10)
        self.redHorizontalSlider.setObjectName("redHorizontalSlider")
        self.label_15 = QtWidgets.QLabel(self.frame_5)
        self.label_15.setGeometry(QtCore.QRect(10, 110, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.greenSpinBox = QtWidgets.QSpinBox(self.frame_5)
        self.greenSpinBox.setGeometry(QtCore.QRect(220, 60, 71, 41))
        self.greenSpinBox.setMaximum(100)
        self.greenSpinBox.setProperty("value", 30)
        self.greenSpinBox.setObjectName("greenSpinBox")
        self.frame_9 = QtWidgets.QFrame(self.frame1)
        self.frame_9.setGeometry(QtCore.QRect(10, 370, 351, 161))
        self.frame_9.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setLineWidth(2)
        self.frame_9.setMidLineWidth(1)
        self.frame_9.setObjectName("frame_9")
        self.blueMaxSpinBox = QtWidgets.QSpinBox(self.frame_9)
        self.blueMaxSpinBox.setGeometry(QtCore.QRect(220, 110, 71, 41))
        self.blueMaxSpinBox.setMaximum(255)
        self.blueMaxSpinBox.setProperty("value", 30)
        self.blueMaxSpinBox.setObjectName("blueMaxSpinBox")
        self.greenMaxHorizontalSlider = QtWidgets.QSlider(self.frame_9)
        self.greenMaxHorizontalSlider.setGeometry(QtCore.QRect(70, 70, 141, 21))
        self.greenMaxHorizontalSlider.setMaximum(255)
        self.greenMaxHorizontalSlider.setSliderPosition(30)
        self.greenMaxHorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.greenMaxHorizontalSlider.setObjectName("greenMaxHorizontalSlider")
        self.redMaxSpinBox = QtWidgets.QSpinBox(self.frame_9)
        self.redMaxSpinBox.setGeometry(QtCore.QRect(220, 10, 71, 41))
        self.redMaxSpinBox.setMaximum(255)
        self.redMaxSpinBox.setProperty("value", 30)
        self.redMaxSpinBox.setObjectName("redMaxSpinBox")
        self.greenMaxSpinBox = QtWidgets.QSpinBox(self.frame_9)
        self.greenMaxSpinBox.setGeometry(QtCore.QRect(220, 60, 71, 41))
        self.greenMaxSpinBox.setMaximum(255)
        self.greenMaxSpinBox.setProperty("value", 30)
        self.greenMaxSpinBox.setObjectName("greenMaxSpinBox")
        self.label_18 = QtWidgets.QLabel(self.frame_9)
        self.label_18.setGeometry(QtCore.QRect(10, 60, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.label_17 = QtWidgets.QLabel(self.frame_9)
        self.label_17.setGeometry(QtCore.QRect(10, 110, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.redMaxHorizontalSlider = QtWidgets.QSlider(self.frame_9)
        self.redMaxHorizontalSlider.setGeometry(QtCore.QRect(70, 20, 141, 21))
        self.redMaxHorizontalSlider.setMaximum(255)
        self.redMaxHorizontalSlider.setSingleStep(10)
        self.redMaxHorizontalSlider.setSliderPosition(30)
        self.redMaxHorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.redMaxHorizontalSlider.setInvertedAppearance(False)
        self.redMaxHorizontalSlider.setInvertedControls(False)
        self.redMaxHorizontalSlider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.redMaxHorizontalSlider.setTickInterval(10)
        self.redMaxHorizontalSlider.setObjectName("redMaxHorizontalSlider")
        self.blueMaxHorizontalSlider = QtWidgets.QSlider(self.frame_9)
        self.blueMaxHorizontalSlider.setGeometry(QtCore.QRect(70, 120, 141, 21))
        self.blueMaxHorizontalSlider.setMaximum(255)
        self.blueMaxHorizontalSlider.setSingleStep(10)
        self.blueMaxHorizontalSlider.setSliderPosition(30)
        self.blueMaxHorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.blueMaxHorizontalSlider.setObjectName("blueMaxHorizontalSlider")
        self.label_16 = QtWidgets.QLabel(self.frame_9)
        self.label_16.setGeometry(QtCore.QRect(10, 10, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.frame_7 = QtWidgets.QFrame(self.frame1)
        self.frame_7.setGeometry(QtCore.QRect(380, 370, 421, 161))
        self.frame_7.setFrameShape(QtWidgets.QFrame.Box)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setLineWidth(2)
        self.frame_7.setMidLineWidth(1)
        self.frame_7.setObjectName("frame_7")
        self.panelPwmSpinBox = QtWidgets.QSpinBox(self.frame_7)
        self.panelPwmSpinBox.setGeometry(QtCore.QRect(260, 10, 71, 41))
        self.panelPwmSpinBox.setMaximum(100)
        self.panelPwmSpinBox.setProperty("value", 30)
        self.panelPwmSpinBox.setObjectName("panelPwmSpinBox")
        self.label_22 = QtWidgets.QLabel(self.frame_7)
        self.label_22.setGeometry(QtCore.QRect(10, 10, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")
        self.panelPwmHorizontalSlider = QtWidgets.QSlider(self.frame_7)
        self.panelPwmHorizontalSlider.setGeometry(QtCore.QRect(90, 20, 161, 21))
        self.panelPwmHorizontalSlider.setMaximum(100)
        self.panelPwmHorizontalSlider.setSingleStep(10)
        self.panelPwmHorizontalSlider.setSliderPosition(30)
        self.panelPwmHorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.panelPwmHorizontalSlider.setInvertedAppearance(False)
        self.panelPwmHorizontalSlider.setInvertedControls(False)
        self.panelPwmHorizontalSlider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.panelPwmHorizontalSlider.setTickInterval(10)
        self.panelPwmHorizontalSlider.setObjectName("panelPwmHorizontalSlider")
        self.openLedButton = QtWidgets.QPushButton(self.frame_7)
        self.openLedButton.setGeometry(QtCore.QRect(10, 60, 121, 31))
        self.openLedButton.setMaximumSize(QtCore.QSize(121, 16777215))
        self.openLedButton.setObjectName("openLedButton")
        self.label_sw_version_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_sw_version_2.setGeometry(QtCore.QRect(50, 20, 151, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_sw_version_2.setFont(font)
        self.label_sw_version_2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_sw_version_2.setObjectName("label_sw_version_2")
        self.fan1Detectlabel = QtWidgets.QLabel(self.centralwidget)
        self.fan1Detectlabel.setGeometry(QtCore.QRect(1150, 480, 81, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.fan1Detectlabel.setFont(font)
        self.fan1Detectlabel.setText("")
        self.fan1Detectlabel.setObjectName("fan1Detectlabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1548, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.blueMaxSpinBox.valueChanged['int'].connect(self.blueMaxHorizontalSlider.setValue)
        self.redMaxSpinBox.valueChanged['int'].connect(self.redMaxHorizontalSlider.setValue)
        self.greenMaxSpinBox.valueChanged['int'].connect(self.greenMaxHorizontalSlider.setValue)
        self.redMaxHorizontalSlider.valueChanged['int'].connect(self.redMaxSpinBox.setValue)
        self.greenMaxHorizontalSlider.valueChanged['int'].connect(self.greenMaxSpinBox.setValue)
        self.blueMaxHorizontalSlider.valueChanged['int'].connect(self.blueMaxSpinBox.setValue)
        self.redSpinBox.valueChanged['int'].connect(self.redHorizontalSlider.setValue)
        self.redHorizontalSlider.valueChanged['int'].connect(self.redSpinBox.setValue)
        self.greenHorizontalSlider.valueChanged['int'].connect(self.greenSpinBox.setValue)
        self.greenSpinBox.valueChanged['int'].connect(self.greenHorizontalSlider.setValue)
        self.blueHorizontalSlider.valueChanged['int'].connect(self.blueSpinBox.setValue)
        self.blueSpinBox.valueChanged['int'].connect(self.blueHorizontalSlider.setValue)
        self.fan1HorizontalSlider.valueChanged['int'].connect(self.fan1SpinBox.setValue)
        self.fan1SpinBox.valueChanged['int'].connect(self.fan1HorizontalSlider.setValue)
        self.fan2HorizontalSlider.valueChanged['int'].connect(self.fan2SpinBox.setValue)
        self.fan2SpinBox.valueChanged['int'].connect(self.fan2HorizontalSlider.setValue)
        self.fan3HorizontalSlider.valueChanged['int'].connect(self.fan3SpinBox.setValue)
        self.fan3SpinBox.valueChanged['int'].connect(self.fan3HorizontalSlider.setValue)
        self.panelPwmSpinBox.valueChanged['int'].connect(self.panelPwmHorizontalSlider.setValue)
        self.panelPwmHorizontalSlider.valueChanged['int'].connect(self.panelPwmSpinBox.setValue)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_2.setText(_translate("MainWindow", "串口号"))
        self.baud_rate.setCurrentText(_translate("MainWindow", "9600"))
        self.baud_rate.setItemText(0, _translate("MainWindow", "9600"))
        self.baud_rate.setItemText(1, _translate("MainWindow", "19200"))
        self.baud_rate.setItemText(2, _translate("MainWindow", "38400"))
        self.baud_rate.setItemText(3, _translate("MainWindow", "115200"))
        self.baud_rate.setItemText(4, _translate("MainWindow", "921600"))
        self.label_4.setText(_translate("MainWindow", "波特率"))
        self.refresh_port.setText(_translate("MainWindow", "刷新串口"))
        self.open_port.setText(_translate("MainWindow", "打开串口"))
        self.close_port.setText(_translate("MainWindow", "关闭串口"))
        self.label_11.setText(_translate("MainWindow", "数据接收"))
        self.label_13.setText(_translate("MainWindow", "数据发送"))
        self.label_12.setText(_translate("MainWindow", "数据发送"))
        self.send_data.setText(_translate("MainWindow", "发送数据"))
        self.label_6.setText(_translate("MainWindow", "串口状态:"))
        self.label_31.setText(_translate("MainWindow", "LED温度："))
        self.temp1Label.setText(_translate("MainWindow", "100"))
        self.label_33.setText(_translate("MainWindow", "度"))
        self.label_32.setText(_translate("MainWindow", "LCD温度："))
        self.temp2Label.setText(_translate("MainWindow", "100"))
        self.label_35.setText(_translate("MainWindow", "度"))
        self.label_36.setText(_translate("MainWindow", "采集频率："))
        self.label_37.setText(_translate("MainWindow", "状态："))
        self.tempFlagLabel.setText(_translate("MainWindow", "关闭"))
        self.updateTempButton.setText(_translate("MainWindow", "启动定时"))
        self.label_34.setText(_translate("MainWindow", "环境温度："))
        self.temp3Label.setText(_translate("MainWindow", "100"))
        self.label_38.setText(_translate("MainWindow", "度"))
        self.label_39.setText(_translate("MainWindow", "电压："))
        self.label_40.setText(_translate("MainWindow", "电压："))
        self.label_41.setText(_translate("MainWindow", "电压："))
        self.temp1VoltageLabel.setText(_translate("MainWindow", "3.3"))
        self.temp2VoltageLabel.setText(_translate("MainWindow", "3.3"))
        self.temp3VoltageLabel.setText(_translate("MainWindow", "3.3"))
        self.label_42.setText(_translate("MainWindow", "V"))
        self.label_43.setText(_translate("MainWindow", "V"))
        self.label_44.setText(_translate("MainWindow", "V"))
        self.updateTempEdit.setText(_translate("MainWindow", "1000"))
        self.getSwVerButton.setText(_translate("MainWindow", "获取软件版本："))
        self.label_sw_version.setText(_translate("MainWindow", "0.0.1"))
        self.savePduDataButton.setText(_translate("MainWindow", "保存数据"))
        self.label_30.setText(_translate("MainWindow", "马达状态："))
        self.motorBackButton.setText(_translate("MainWindow", "马达后退"))
        self.motorStatuslabel.setText(_translate("MainWindow", "未限位"))
        self.motorStepsEdit.setText(_translate("MainWindow", "1000"))
        self.motorForwardButton.setText(_translate("MainWindow", "马达前进"))
        self.autoTestMotorOpenButton.setText(_translate("MainWindow", "开始自动测试"))
        self.autoTestMotorCloseButton.setText(_translate("MainWindow", "关闭自动测试"))
        self.motorStepsRoundEdit.setText(_translate("MainWindow", "2800"))
        self.totalRoundLabel.setText(_translate("MainWindow", "0"))
        self.label_29.setText(_translate("MainWindow", "风扇3"))
        self.label_20.setText(_translate("MainWindow", "风扇2"))
        self.label_19.setText(_translate("MainWindow", "风扇1"))
        self.fan1Detectlabel_2.setText(_translate("MainWindow", "正常"))
        self.fan2Detectlabel.setText(_translate("MainWindow", "正常"))
        self.fan3Detectlabel.setText(_translate("MainWindow", "正常"))
        self.label_14.setText(_translate("MainWindow", "电流G"))
        self.label_10.setText(_translate("MainWindow", "电流R"))
        self.label_15.setText(_translate("MainWindow", "电流B"))
        self.label_18.setText(_translate("MainWindow", "MaxG"))
        self.label_17.setText(_translate("MainWindow", "MaxB"))
        self.label_16.setText(_translate("MainWindow", "MaxR"))
        self.label_22.setText(_translate("MainWindow", "屏PWM"))
        self.openLedButton.setText(_translate("MainWindow", "打开光机"))
        self.label_sw_version_2.setText(_translate("MainWindow", "光机外设控制："))
