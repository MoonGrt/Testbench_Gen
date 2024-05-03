import sys
from PyQt5.QtWidgets import QApplication, QWidget, QRadioButton, QHBoxLayout

class OptionBox(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('水平二选一选项框')
        # self.setGeometry(300, 300, 250, 150)

        # 创建两个单选按钮
        self.radioButton1 = QRadioButton('选项1')
        self.radioButton2 = QRadioButton('选项2')

        # 设置单选按钮的高度
        self.radioButton1.setFixedHeight(20)
        self.radioButton2.setFixedHeight(20)

        # 创建水平布局
        hbox = QHBoxLayout()
        hbox.addWidget(self.radioButton1)
        hbox.addWidget(self.radioButton2)

        # 设置窗口的布局
        self.setLayout(hbox)

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OptionBox()
    sys.exit(app.exec_())
