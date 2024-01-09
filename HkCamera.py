from PyQt5.QtWidgets import QMainWindow, QMessageBox

from BasicDemo import ToHexStr, decoding_char
from CamOperation_class import CameraOperation
from MvImport.CameraParams_const import MV_GIGE_DEVICE, MV_USB_DEVICE
from MvImport.CameraParams_header import MV_CC_DEVICE_INFO_LIST, MV_CC_DEVICE_INFO
from MvImport.MvCameraControl_class import MvCamera
from MvImport.MvErrorDefine_const import MV_E_CALLORDER, MV_OK
from PyUICBasicDemo import UiHk_MainWindow
import ctypes


class UiHkWindow(QMainWindow, UiHk_MainWindow):

    def __init__(self):
        super().__init__()
        # mainWindow = QMainWindow()

        global deviceList
        deviceList = MV_CC_DEVICE_INFO_LIST()
        global cam
        cam = MvCamera()
        global nSelCamIndex
        nSelCamIndex = 0
        global obj_cam_operation
        obj_cam_operation = 0
        global isOpen
        isOpen = False
        global isGrabbing
        isGrabbing = False
        global isCalibMode  # 是否是标定模式（获取原始图像）
        isCalibMode = True

        self.ui = UiHk_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('海康摄像头调试')

        self.ui.bnEnum.clicked.connect(self.enum_devices)
        self.ui.bnOpen.clicked.connect(self.open_device)
        self.ui.bnClose.clicked.connect(self.close_device)
        self.ui.bnStart.clicked.connect(self.start_grabbing)
        self.ui.bnStop.clicked.connect(self.stop_grabbing)

        self.ui.bnSoftwareTrigger.clicked.connect(self.trigger_once)
        self.ui.radioTriggerMode.clicked.connect(self.set_software_trigger_mode)
        self.ui.radioContinueMode.clicked.connect(self.set_continue_mode)

        self.ui.bnGetParam.clicked.connect(self.get_param)
        self.ui.bnSetParam.clicked.connect(self.set_param)

        self.ui.bnSaveImage.clicked.connect(self.save_bmp)

    # ch:枚举相机 | en:enum devices
    def enum_devices(self):
        global deviceList
        global obj_cam_operation

        deviceList = MV_CC_DEVICE_INFO_LIST()
        ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, deviceList)
        if ret != 0:
            strError = "Enum devices fail! ret = :" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
            return -1

        if deviceList.nDeviceNum == 0:
            QMessageBox.warning(self, "Info", "Find no device", QMessageBox.Ok)
            return -2
        print("Find %d devices!" % deviceList.nDeviceNum)

        devList = []
        for i in range(0, deviceList.nDeviceNum):
            mvcc_dev_info = ctypes.cast(deviceList.pDeviceInfo[i], ctypes.POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                print("\ngige device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print("current ip: %d.%d.%d.%d " % (nip1, nip2, nip3, nip4))
                devList.append(
                    "[" + str(i) + "]GigE: " + user_defined_name + " " + model_name + "(" + str(nip1) + "." + str(
                        nip2) + "." + str(nip3) + "." + str(nip4) + ")")
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print("\nu3v device: [%d]" % i)
                user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
                model_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName)
                print("device user define name: " + user_defined_name)
                print("device model name: " + model_name)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print("user serial number: " + strSerialNumber)
                devList.append("[" + str(i) + "]USB: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")

        self.ui.ComboDevices.clear()
        self.ui.ComboDevices.addItems(devList)
        self.ui.ComboDevices.setCurrentIndex(0)
        return deviceList.nDeviceNum

    # ch:打开相机 | en:open device
    def open_device(self):
        global deviceList
        global nSelCamIndex
        global obj_cam_operation
        global isOpen
        if deviceList.nDeviceNum > 0:
            if isOpen:
                QMessageBox.warning(self, "Error", 'Camera is Running!', QMessageBox.Ok)
                return MV_E_CALLORDER

            nSelCamIndex = self.ui.ComboDevices.currentIndex()
            print('>>>>>>>>>>>>', nSelCamIndex)
            if nSelCamIndex < 0:
                QMessageBox.warning(self, "Error", 'Please select a camera!', QMessageBox.Ok)
                return MV_E_CALLORDER

            obj_cam_operation = CameraOperation(cam, deviceList, nSelCamIndex)
            ret = obj_cam_operation.Open_device()
            if 0 != ret:
                strError = "Open device failed ret:" + ToHexStr(ret)
                QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
                isOpen = False
            else:
                self.set_continue_mode()

                self.get_param()

                isOpen = True
                self.enable_controls()
        else:
            QMessageBox.warning(self, "Info", "Find no device, open fail", QMessageBox.Ok)

    # ch:开始取流 | en:Start grab image
    def start_grabbing(self):
        global obj_cam_operation
        global isGrabbing
        print('start_grabbing', isOpen)
        if isOpen:
            ret = obj_cam_operation.Start_grabbing(self.ui.widgetDisplay.winId())
            if ret != 0:
                strError = "Start grabbing failed ret:" + ToHexStr(ret)
                print('Start grabbing failed ret')
                QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
            else:
                isGrabbing = True
                self.enable_controls()
        else:
            print('请先打开HK CAM')

    # ch:停止取流 | en:Stop grab image   768
    def stop_grabbing(self):
        global obj_cam_operation
        global isGrabbing
        ret = obj_cam_operation.Stop_grabbing()
        if ret != 0:
            strError = "Stop grabbing failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
        else:
            isGrabbing = False
            self.enable_controls()

    # ch:关闭设备 | Close device
    def close_device(self):
        global isOpen
        global isGrabbing
        global obj_cam_operation

        if isOpen:
            obj_cam_operation.Close_device()
            isOpen = False

        isGrabbing = False

        self.enable_controls()

    # ch:设置触发模式 | en:set trigger mode
    def set_continue_mode(self):
        strError = None

        ret = obj_cam_operation.Set_trigger_mode(False)
        if ret != 0:
            strError = "Set continue mode failed ret:" + ToHexStr(ret) + " mode is " + str(is_trigger_mode)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
        else:
            self.ui.radioContinueMode.setChecked(True)
            self.ui.radioTriggerMode.setChecked(False)
            self.ui.bnSoftwareTrigger.setEnabled(False)

    # ch:设置软触发模式 | en:set software trigger mode
    def set_software_trigger_mode(self):

        ret = obj_cam_operation.Set_trigger_mode(True)
        if ret != 0:
            strError = "Set trigger mode failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
        else:
            self.ui.radioContinueMode.setChecked(False)
            self.ui.radioTriggerMode.setChecked(True)
            self.ui.bnSoftwareTrigger.setEnabled(isGrabbing)

    # ch:设置触发命令 | en:set trigger software
    def trigger_once(self):
        ret = obj_cam_operation.Trigger_once()
        if ret != 0:
            strError = "TriggerSoftware failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)

    # ch:存图 | en:save image
    def save_bmp(self):
        ret = obj_cam_operation.Save_Bmp()
        if ret != MV_OK:
            strError = "Save BMP failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
        else:
            print("Save image success")

    def get_raw_numpy(self):
        if obj_cam_operation != 0:
            return obj_cam_operation.Get_Raw_Numpy()

    def save_cal_bmp(self, name):
        ret = obj_cam_operation.Save_Cal_Bmp(name)
        if ret != MV_OK:
            strError = "Save BMP failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
        else:
            print("Save image success")

    # ch: 获取参数 | en:get param
    def get_param(self):
        ret = obj_cam_operation.Get_parameter()
        if ret != MV_OK:
            strError = "Get param failed ret:" + ToHexStr(ret)
            QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)
        else:
            self.ui.edtExposureTime.setText("{0:.2f}".format(obj_cam_operation.exposure_time))
            self.ui.edtGain.setText("{0:.2f}".format(obj_cam_operation.gain))
            self.ui.edtFrameRate.setText("{0:.2f}".format(obj_cam_operation.frame_rate))

    # ch: 设置参数 | en:set param
    def set_param(self):
        if obj_cam_operation != 0:
            frame_rate = self.ui.edtFrameRate.text()
            exposure = self.ui.edtExposureTime.text()
            gain = self.ui.edtGain.text()
            ret = obj_cam_operation.Set_parameter(frame_rate, exposure, gain)
            if ret != MV_OK:
                strError = "Set param failed ret:" + ToHexStr(ret)
                QMessageBox.warning(self, "Error", strError, QMessageBox.Ok)

            return MV_OK

        # ch: 设置控件状态 | en:set enable status

    def enable_controls(self):
        global isGrabbing
        global isOpen

        # 先设置group的状态，再单独设置各控件状态
        self.ui.groupGrab.setEnabled(isOpen)
        self.ui.groupParam.setEnabled(isOpen)

        self.ui.bnOpen.setEnabled(not isOpen)
        self.ui.bnClose.setEnabled(isOpen)

        self.ui.bnStart.setEnabled(isOpen and (not isGrabbing))
        self.ui.bnStop.setEnabled(isOpen and isGrabbing)
        self.ui.bnSoftwareTrigger.setEnabled(isGrabbing and self.ui.radioTriggerMode.isChecked())

        self.ui.bnSaveImage.setEnabled(isOpen and isGrabbing)
