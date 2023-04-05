#from ui_test.testV3_1 import Ui_Form
import sys
import random
from PyQt5.QtChart import QDateTimeAxis, QValueAxis, QSplineSeries, QChart, QChartView
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QDateTime, Qt, QTimer

def setupPrarmeters(self):
    # 设置数据显示时间 1min
    self.showTime = 60 * 1
    # 设置数据刷新时间 1s
    self.flushTime = 1000 * 1
    # 设置显示数据量
    self.totalNum = self.showTime / self.flushTime * 1000

def chart_init(self):
    # self.chart = QChart()
    self.chart = self.graphicsView.chart()
    self.chart.setTitle('测试样例')
    self.series = QSplineSeries()
    # 设置曲线名称
    self.series.setName("实时数据")
    # 把曲线添加到QChart的实例中
    self.chart.addSeries(self.series)
    # 声明并初始化X轴，Y轴
    self.dtaxisX = QDateTimeAxis()
    self.vlaxisY = QValueAxis()
    # 设置坐标轴显示范围
    self.dtaxisX.setMin(QDateTime.currentDateTime().addSecs(-self.showTime*1))
    self.dtaxisX.setMax(QDateTime.currentDateTime().addSecs(0))
    self.vlaxisY.setMin(-300)
    self.vlaxisY.setMax(300)
    # 设置X轴时间样式
    self.dtaxisX.setFormat("hh:mm:ss")
    # 设置坐标轴上的格点
    self.dtaxisX.setTickCount(6)
    self.vlaxisY.setTickCount(11)
    # 设置坐标轴名称
    self.dtaxisX.setTitleText("时间")
    self.vlaxisY.setTitleText("幅值")
    # 设置网格不显示
    self.vlaxisY.setGridLineVisible(False)
    # 把坐标轴添加到chart中
    self.chart.addAxis(self.dtaxisX, Qt.AlignBottom)
    self.chart.addAxis(self.vlaxisY, Qt.AlignLeft)
    # 把曲线关联到坐标轴
    self.series.attachAxis(self.dtaxisX)
    self.series.attachAxis(self.vlaxisY)

def timer_init(self):
    # 使用QTimer，1秒触发一次，更新数据
    self.timer = QTimer(self)
    self.timer.timeout.connect(self.drawLine)
    self.timer.start(self.flushTime)

def drawLine(self):
    # 获取当前时间
    bjtime = QDateTime.currentDateTime()
    # 更新X轴坐标
    self.dtaxisX.setMin(QDateTime.currentDateTime().addSecs(-self.showTime*1))
    self.dtaxisX.setMax(QDateTime.currentDateTime().addSecs(0))
    # 当曲线上的点超出X轴的范围时，移除最早的点
    if self.series.count() > self.totalNum:
        self.series.removePoints(0, self.series.count()-self.totalNum)
    # 产生随机数
    yint = random.randint(-250, 250)
    # 添加数据到曲线末端
    self.series.append(bjtime.toMSecsSinceEpoch(), yint)


class mainWindow(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)

        self.setupUi(self)
        self.setupPrarmeters()
        self.chart_init()
        self.timer_init()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = mainWindow()
    view.show()
    sys.exit(app.exec_())
