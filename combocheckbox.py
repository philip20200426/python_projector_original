# 下拉复选框测试/combocheckbox.py
from PyQt5.QtWidgets import QComboBox, QLineEdit, QListWidget, QCheckBox, QListWidgetItem
from PyQt5 import QtCore


class ComboCheckBox(QComboBox):
    def __init__(self, parent):
        """
        initial function
        """
        super(ComboCheckBox, self).__init__(parent)

        self.box_list = []  # selected items
        self.text = QLineEdit()  # use to selected items
        self.state = 0  # use to record state
        #self.text.setStyleSheet("QLineEdit { qproperty-frame: false }")
        self.setStyleSheet("width: 160px; height: 22px; font-size: 12px; font-weight: bold")
        self.text.setReadOnly(True)
        self.setLineEdit(self.text)

    def myadditems(self, items):
        """

        :param items: 传入下拉选项
        :return:
        """
        self.items = ["全选"] + items  # items list
        q = QListWidget()
        for i in range(len(self.items)):
            self.box_list.append(QCheckBox())
            self.box_list[i].setText(self.items[i])
            item = QListWidgetItem(q)
            q.setItemWidget(item, self.box_list[i])
            if i == 0:
                self.box_list[i].stateChanged.connect(self.all_selected)
            else:
                self.box_list[i].stateChanged.connect(self.show_selected)

        # q.setStyleSheet("font-size: 20px; font-weight: bold; height: 40px; margin-left: 5px")
        self.setModel(q.model())
        self.setView(q)

    def addQCheckBox(self, i):
        self.box_list[i].setChecked(True)

    def delQCheckBox(self, i):
        self.box_list[i].setChecked(False)

    def all_selected(self):
        """
        decide whether to check all
        :return:
        """
        # change state
        if self.state == 0:
            self.state = 1
            for i in range(1, len(self.items)):
                self.box_list[i].setChecked(True)
        else:
            self.state = 0
            for i in range(1, len(self.items)):
                self.box_list[i].setChecked(False)
        self.show_selected()

    def get_selected(self) -> list:
        """
        get selected items
        :return:
        """
        ret = []
        for i in range(1, len(self.items)):
            if self.box_list[i].isChecked():
                ret.append(self.box_list[i].text())
        return ret

    def show_selected(self):
        """
        show selected items
        :return:
        """
        self.text.clear()
        ret = '; '.join(self.get_selected())
        self.text.setText(ret)
