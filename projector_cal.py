# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'projector_cal.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1730, 793)
        font = QtGui.QFont()
        font.setFamily("Arial")
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(0, 0, 281, 561))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.rootButton = QtWidgets.QPushButton(self.frame)
        self.rootButton.setObjectName("rootButton")
        self.verticalLayout.addWidget(self.rootButton)
        self.saveDataButton = QtWidgets.QPushButton(self.frame)
        self.saveDataButton.setObjectName("saveDataButton")
        self.verticalLayout.addWidget(self.saveDataButton)
        self.pullDataButton = QtWidgets.QPushButton(self.frame)
        self.pullDataButton.setObjectName("pullDataButton")
        self.verticalLayout.addWidget(self.pullDataButton)
        self.cleanButton = QtWidgets.QPushButton(self.frame)
        self.cleanButton.setObjectName("cleanButton")
        self.verticalLayout.addWidget(self.cleanButton)
        self.showCheckerPatternButton = QtWidgets.QPushButton(self.frame)
        self.showCheckerPatternButton.setObjectName("showCheckerPatternButton")
        self.verticalLayout.addWidget(self.showCheckerPatternButton)
        self.showWritePatternButton = QtWidgets.QPushButton(self.frame)
        self.showWritePatternButton.setObjectName("showWritePatternButton")
        self.verticalLayout.addWidget(self.showWritePatternButton)
        self.removePatternButton = QtWidgets.QPushButton(self.frame)
        self.removePatternButton.setObjectName("removePatternButton")
        self.verticalLayout.addWidget(self.removePatternButton)
        self.openCamButton = QtWidgets.QPushButton(self.frame)
        self.openCamButton.setObjectName("openCamButton")
        self.verticalLayout.addWidget(self.openCamButton)
        self.takePictureButton = QtWidgets.QPushButton(self.frame)
        self.takePictureButton.setObjectName("takePictureButton")
        self.verticalLayout.addWidget(self.takePictureButton)
        self.closeCamButton = QtWidgets.QPushButton(self.frame)
        self.closeCamButton.setObjectName("closeCamButton")
        self.verticalLayout.addWidget(self.closeCamButton)
        self.motorResetButton = QtWidgets.QPushButton(self.frame)
        self.motorResetButton.setObjectName("motorResetButton")
        self.verticalLayout.addWidget(self.motorResetButton)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setGeometry(QtCore.QRect(750, 0, 511, 271))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(10)
        self.frame_2.setFont(font)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
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
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setGeometry(QtCore.QRect(0, 560, 281, 51))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.motorForwardButton = QtWidgets.QPushButton(self.frame_3)
        self.motorForwardButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.motorForwardButton.setObjectName("motorForwardButton")
        self.horizontalLayout.addWidget(self.motorForwardButton)
        self.motorBackButton = QtWidgets.QPushButton(self.frame_3)
        self.motorBackButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.motorBackButton.setObjectName("motorBackButton")
        self.horizontalLayout.addWidget(self.motorBackButton)
        self.motorPositionEdit = QtWidgets.QLineEdit(self.frame_3)
        self.motorPositionEdit.setMaximumSize(QtCore.QSize(60, 16777215))
        self.motorPositionEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.motorPositionEdit.setObjectName("motorPositionEdit")
        self.horizontalLayout.addWidget(self.motorPositionEdit)
        self.frame_4 = QtWidgets.QFrame(self.centralwidget)
        self.frame_4.setGeometry(QtCore.QRect(10, 610, 271, 41))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.positionLabel = QtWidgets.QLabel(self.frame_4)
        self.positionLabel.setObjectName("positionLabel")
        self.horizontalLayout_2.addWidget(self.positionLabel)
        self.posValueLabel = QtWidgets.QLabel(self.frame_4)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.posValueLabel.setFont(font)
        self.posValueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.posValueLabel.setObjectName("posValueLabel")
        self.horizontalLayout_2.addWidget(self.posValueLabel)
        self.frame_5 = QtWidgets.QFrame(self.centralwidget)
        self.frame_5.setGeometry(QtCore.QRect(10, 650, 271, 41))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.stepsLabel = QtWidgets.QLabel(self.frame_5)
        self.stepsLabel.setObjectName("stepsLabel")
        self.horizontalLayout_3.addWidget(self.stepsLabel)
        self.stepsValueLabel = QtWidgets.QLabel(self.frame_5)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.stepsValueLabel.setFont(font)
        self.stepsValueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.stepsValueLabel.setObjectName("stepsValueLabel")
        self.horizontalLayout_3.addWidget(self.stepsValueLabel)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(822, 240, 91, 20))
        self.label_6.setMinimumSize(QtCore.QSize(0, 20))
        self.label_6.setObjectName("label_6")
        self.port_status = QtWidgets.QLabel(self.centralwidget)
        self.port_status.setGeometry(QtCore.QRect(900, 240, 131, 20))
        self.port_status.setMinimumSize(QtCore.QSize(0, 20))
        self.port_status.setText("")
        self.port_status.setObjectName("port_status")
        self.frame_6 = QtWidgets.QFrame(self.centralwidget)
        self.frame_6.setGeometry(QtCore.QRect(750, 280, 511, 141))
        self.frame_6.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.getSwVerButton = QtWidgets.QPushButton(self.frame_6)
        self.getSwVerButton.setGeometry(QtCore.QRect(20, 10, 93, 28))
        self.getSwVerButton.setObjectName("getSwVerButton")
        self.label_sw_version = QtWidgets.QLabel(self.frame_6)
        self.label_sw_version.setGeometry(QtCore.QRect(150, 20, 72, 15))
        self.label_sw_version.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_sw_version.setObjectName("label_sw_version")
        self.frame_left_up = QtWidgets.QFrame(self.centralwidget)
        self.frame_left_up.setGeometry(QtCore.QRect(290, 140, 451, 421))
        self.frame_left_up.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_left_up.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_left_up.setObjectName("frame_left_up")
        self.label_5 = QtWidgets.QLabel(self.frame_left_up)
        self.label_5.setGeometry(QtCore.QRect(10, 80, 61, 17))
        self.label_5.setObjectName("label_5")
        self.ksdLeftUpEdit_x = QtWidgets.QLineEdit(self.frame_left_up)
        self.ksdLeftUpEdit_x.setGeometry(QtCore.QRect(70, 70, 71, 24))
        self.ksdLeftUpEdit_x.setMaximumSize(QtCore.QSize(80, 16777215))
        self.ksdLeftUpEdit_x.setAlignment(QtCore.Qt.AlignCenter)
        self.ksdLeftUpEdit_x.setObjectName("ksdLeftUpEdit_x")
        self.label_X = QtWidgets.QLabel(self.frame_left_up)
        self.label_X.setGeometry(QtCore.QRect(80, 40, 61, 17))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_X.setFont(font)
        self.label_X.setAlignment(QtCore.Qt.AlignCenter)
        self.label_X.setObjectName("label_X")
        self.ksdLeftUpEdit_y = QtWidgets.QLineEdit(self.frame_left_up)
        self.ksdLeftUpEdit_y.setGeometry(QtCore.QRect(150, 70, 71, 24))
        self.ksdLeftUpEdit_y.setMaximumSize(QtCore.QSize(80, 16777215))
        self.ksdLeftUpEdit_y.setAlignment(QtCore.Qt.AlignCenter)
        self.ksdLeftUpEdit_y.setObjectName("ksdLeftUpEdit_y")
        self.label_X_2 = QtWidgets.QLabel(self.frame_left_up)
        self.label_X_2.setGeometry(QtCore.QRect(160, 40, 61, 17))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_X_2.setFont(font)
        self.label_X_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_X_2.setObjectName("label_X_2")
        self.ksdRightUpEdit_x = QtWidgets.QLineEdit(self.frame_left_up)
        self.ksdRightUpEdit_x.setGeometry(QtCore.QRect(290, 70, 71, 24))
        self.ksdRightUpEdit_x.setMaximumSize(QtCore.QSize(80, 16777215))
        self.ksdRightUpEdit_x.setAlignment(QtCore.Qt.AlignCenter)
        self.ksdRightUpEdit_x.setObjectName("ksdRightUpEdit_x")
        self.label_7 = QtWidgets.QLabel(self.frame_left_up)
        self.label_7.setGeometry(QtCore.QRect(230, 80, 61, 17))
        self.label_7.setObjectName("label_7")
        self.ksdRightUpEdit_y = QtWidgets.QLineEdit(self.frame_left_up)
        self.ksdRightUpEdit_y.setGeometry(QtCore.QRect(370, 70, 71, 24))
        self.ksdRightUpEdit_y.setMaximumSize(QtCore.QSize(80, 16777215))
        self.ksdRightUpEdit_y.setAlignment(QtCore.Qt.AlignCenter)
        self.ksdRightUpEdit_y.setObjectName("ksdRightUpEdit_y")
        self.label_X_3 = QtWidgets.QLabel(self.frame_left_up)
        self.label_X_3.setGeometry(QtCore.QRect(290, 40, 61, 17))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_X_3.setFont(font)
        self.label_X_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_X_3.setObjectName("label_X_3")
        self.label_X_4 = QtWidgets.QLabel(self.frame_left_up)
        self.label_X_4.setGeometry(QtCore.QRect(370, 40, 61, 17))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_X_4.setFont(font)
        self.label_X_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_X_4.setObjectName("label_X_4")
        self.ksdRightDownEdit_x = QtWidgets.QLineEdit(self.frame_left_up)
        self.ksdRightDownEdit_x.setGeometry(QtCore.QRect(290, 140, 71, 24))
        self.ksdRightDownEdit_x.setMaximumSize(QtCore.QSize(80, 16777215))
        self.ksdRightDownEdit_x.setAlignment(QtCore.Qt.AlignCenter)
        self.ksdRightDownEdit_x.setObjectName("ksdRightDownEdit_x")
        self.ksdRightDownEdit_y = QtWidgets.QLineEdit(self.frame_left_up)
        self.ksdRightDownEdit_y.setGeometry(QtCore.QRect(370, 140, 71, 24))
        self.ksdRightDownEdit_y.setMaximumSize(QtCore.QSize(80, 16777215))
        self.ksdRightDownEdit_y.setAlignment(QtCore.Qt.AlignCenter)
        self.ksdRightDownEdit_y.setObjectName("ksdRightDownEdit_y")
        self.ksdLeftDownEdit_x = QtWidgets.QLineEdit(self.frame_left_up)
        self.ksdLeftDownEdit_x.setGeometry(QtCore.QRect(70, 140, 71, 24))
        self.ksdLeftDownEdit_x.setMaximumSize(QtCore.QSize(80, 16777215))
        self.ksdLeftDownEdit_x.setAlignment(QtCore.Qt.AlignCenter)
        self.ksdLeftDownEdit_x.setObjectName("ksdLeftDownEdit_x")
        self.label_8 = QtWidgets.QLabel(self.frame_left_up)
        self.label_8.setGeometry(QtCore.QRect(10, 150, 61, 17))
        self.label_8.setObjectName("label_8")
        self.ksdLeftDownEdit_y = QtWidgets.QLineEdit(self.frame_left_up)
        self.ksdLeftDownEdit_y.setGeometry(QtCore.QRect(150, 140, 71, 24))
        self.ksdLeftDownEdit_y.setMaximumSize(QtCore.QSize(80, 16777215))
        self.ksdLeftDownEdit_y.setAlignment(QtCore.Qt.AlignCenter)
        self.ksdLeftDownEdit_y.setObjectName("ksdLeftDownEdit_y")
        self.label_9 = QtWidgets.QLabel(self.frame_left_up)
        self.label_9.setGeometry(QtCore.QRect(230, 150, 61, 17))
        self.label_9.setObjectName("label_9")
        self.refreshKsdButton = QtWidgets.QPushButton(self.frame_left_up)
        self.refreshKsdButton.setGeometry(QtCore.QRect(10, 190, 431, 28))
        self.refreshKsdButton.setObjectName("refreshKsdButton")
        self.autoKsdButton = QtWidgets.QPushButton(self.frame_left_up)
        self.autoKsdButton.setGeometry(QtCore.QRect(10, 230, 431, 28))
        self.autoKsdButton.setObjectName("autoKsdButton")
        self.tofAfButton = QtWidgets.QPushButton(self.frame_left_up)
        self.tofAfButton.setGeometry(QtCore.QRect(10, 310, 431, 28))
        self.tofAfButton.setObjectName("tofAfButton")
        self.visionAfButton = QtWidgets.QPushButton(self.frame_left_up)
        self.visionAfButton.setGeometry(QtCore.QRect(10, 350, 431, 28))
        self.visionAfButton.setObjectName("visionAfButton")
        self.ksdCalButton = QtWidgets.QPushButton(self.frame_left_up)
        self.ksdCalButton.setGeometry(QtCore.QRect(10, 270, 431, 28))
        self.ksdCalButton.setObjectName("ksdCalButton")
        self.kstResetButton = QtWidgets.QPushButton(self.frame_left_up)
        self.kstResetButton.setGeometry(QtCore.QRect(10, 10, 93, 28))
        self.kstResetButton.setObjectName("kstResetButton")
        self.frame_7 = QtWidgets.QFrame(self.centralwidget)
        self.frame_7.setGeometry(QtCore.QRect(10, 690, 271, 41))
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.sumStepsLabel = QtWidgets.QLabel(self.frame_7)
        self.sumStepsLabel.setObjectName("sumStepsLabel")
        self.horizontalLayout_4.addWidget(self.sumStepsLabel)
        self.stepsTotalValueLabel = QtWidgets.QLabel(self.frame_7)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.stepsTotalValueLabel.setFont(font)
        self.stepsTotalValueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.stepsTotalValueLabel.setObjectName("stepsTotalValueLabel")
        self.horizontalLayout_4.addWidget(self.stepsTotalValueLabel)
        self.frame_8 = QtWidgets.QFrame(self.centralwidget)
        self.frame_8.setGeometry(QtCore.QRect(289, -1, 451, 131))
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.label_14 = QtWidgets.QLabel(self.frame_8)
        self.label_14.setGeometry(QtCore.QRect(10, 10, 120, 17))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.eOpenCameraButton = QtWidgets.QPushButton(self.frame_8)
        self.eOpenCameraButton.setGeometry(QtCore.QRect(10, 50, 93, 28))
        self.eOpenCameraButton.setObjectName("eOpenCameraButton")
        self.eTakePictureButton = QtWidgets.QPushButton(self.frame_8)
        self.eTakePictureButton.setGeometry(QtCore.QRect(330, 50, 93, 28))
        self.eTakePictureButton.setObjectName("eTakePictureButton")
        self.label_10 = QtWidgets.QLabel(self.frame_8)
        self.label_10.setGeometry(QtCore.QRect(10, 90, 91, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.exTimesHorizontalSlider = QtWidgets.QSlider(self.frame_8)
        self.exTimesHorizontalSlider.setGeometry(QtCore.QRect(110, 100, 201, 21))
        self.exTimesHorizontalSlider.setMinimum(20)
        self.exTimesHorizontalSlider.setMaximum(30000)
        self.exTimesHorizontalSlider.setSingleStep(10)
        self.exTimesHorizontalSlider.setSliderPosition(30)
        self.exTimesHorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.exTimesHorizontalSlider.setInvertedAppearance(False)
        self.exTimesHorizontalSlider.setInvertedControls(False)
        self.exTimesHorizontalSlider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.exTimesHorizontalSlider.setTickInterval(10)
        self.exTimesHorizontalSlider.setObjectName("exTimesHorizontalSlider")
        self.exTimeSpinBox = QtWidgets.QSpinBox(self.frame_8)
        self.exTimeSpinBox.setGeometry(QtCore.QRect(330, 90, 91, 41))
        self.exTimeSpinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.exTimeSpinBox.setMinimum(20)
        self.exTimeSpinBox.setMaximum(30000)
        self.exTimeSpinBox.setProperty("value", 9000)
        self.exTimeSpinBox.setObjectName("exTimeSpinBox")
        self.eCloseCameraButton = QtWidgets.QPushButton(self.frame_8)
        self.eCloseCameraButton.setGeometry(QtCore.QRect(170, 50, 93, 28))
        self.eCloseCameraButton.setObjectName("eCloseCameraButton")
        self.previewCameraLabel = QtWidgets.QLabel(self.centralwidget)
        self.previewCameraLabel.setGeometry(QtCore.QRect(740, 0, 720, 540))
        self.previewCameraLabel.setMaximumSize(QtCore.QSize(720, 540))
        self.previewCameraLabel.setText("")
        self.previewCameraLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previewCameraLabel.setObjectName("previewCameraLabel")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(950, 620, 120, 80))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.stackedWidget.addWidget(self.page_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1730, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolBar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(1)
        self.exTimesHorizontalSlider.valueChanged['int'].connect(self.exTimeSpinBox.setValue)
        self.exTimeSpinBox.valueChanged['int'].connect(self.exTimesHorizontalSlider.setValue)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.rootButton.setText(_translate("MainWindow", "打开投影"))
        self.saveDataButton.setText(_translate("MainWindow", "保存数据"))
        self.pullDataButton.setText(_translate("MainWindow", "提取数据"))
        self.cleanButton.setText(_translate("MainWindow", "清除数据"))
        self.showCheckerPatternButton.setText(_translate("MainWindow", "显示棋盘图片"))
        self.showWritePatternButton.setText(_translate("MainWindow", "显示白色图片"))
        self.removePatternButton.setText(_translate("MainWindow", "清除显示图片"))
        self.openCamButton.setText(_translate("MainWindow", "打开相机"))
        self.takePictureButton.setText(_translate("MainWindow", "相机拍照"))
        self.closeCamButton.setText(_translate("MainWindow", "关闭相机"))
        self.motorResetButton.setText(_translate("MainWindow", "马达归零"))
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
        self.motorForwardButton.setText(_translate("MainWindow", "马达前进"))
        self.motorBackButton.setText(_translate("MainWindow", "马达后退"))
        self.motorPositionEdit.setText(_translate("MainWindow", "1000"))
        self.positionLabel.setText(_translate("MainWindow", "当前位置："))
        self.posValueLabel.setText(_translate("MainWindow", "1000"))
        self.stepsLabel.setText(_translate("MainWindow", "当前步数："))
        self.stepsValueLabel.setText(_translate("MainWindow", "1000"))
        self.label_6.setText(_translate("MainWindow", "串口状态:"))
        self.getSwVerButton.setText(_translate("MainWindow", "获取版本号"))
        self.label_sw_version.setText(_translate("MainWindow", "0.0.1"))
        self.label_5.setText(_translate("MainWindow", "左上角："))
        self.ksdLeftUpEdit_x.setText(_translate("MainWindow", "0"))
        self.label_X.setText(_translate("MainWindow", "X"))
        self.ksdLeftUpEdit_y.setText(_translate("MainWindow", "1080"))
        self.label_X_2.setText(_translate("MainWindow", "Y"))
        self.ksdRightUpEdit_x.setText(_translate("MainWindow", "1920"))
        self.label_7.setText(_translate("MainWindow", "右上角："))
        self.ksdRightUpEdit_y.setText(_translate("MainWindow", "1080"))
        self.label_X_3.setText(_translate("MainWindow", "X"))
        self.label_X_4.setText(_translate("MainWindow", "Y"))
        self.ksdRightDownEdit_x.setText(_translate("MainWindow", "1920"))
        self.ksdRightDownEdit_y.setText(_translate("MainWindow", "0"))
        self.ksdLeftDownEdit_x.setText(_translate("MainWindow", "0"))
        self.label_8.setText(_translate("MainWindow", "左下角："))
        self.ksdLeftDownEdit_y.setText(_translate("MainWindow", "0"))
        self.label_9.setText(_translate("MainWindow", "右下角："))
        self.refreshKsdButton.setText(_translate("MainWindow", "写入数据"))
        self.autoKsdButton.setText(_translate("MainWindow", "自动全向梯形校正"))
        self.tofAfButton.setText(_translate("MainWindow", "TOF自动对焦"))
        self.visionAfButton.setText(_translate("MainWindow", "视觉自动对焦"))
        self.ksdCalButton.setText(_translate("MainWindow", "自动全向梯形标定"))
        self.kstResetButton.setText(_translate("MainWindow", "梯形复位"))
        self.sumStepsLabel.setText(_translate("MainWindow", "累计步数："))
        self.stepsTotalValueLabel.setText(_translate("MainWindow", "0"))
        self.label_14.setText(_translate("MainWindow", "外部相机控制："))
        self.eOpenCameraButton.setText(_translate("MainWindow", "打开"))
        self.eTakePictureButton.setText(_translate("MainWindow", "拍照"))
        self.label_10.setText(_translate("MainWindow", "曝光时间:"))
        self.eCloseCameraButton.setText(_translate("MainWindow", "关闭"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
