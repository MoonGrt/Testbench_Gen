from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QRadioButton
import sys
from PyQt5.QtGui import QIcon
class TestbenchGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Verilog Testbench Generator')
        self.resize(800, 600)
        self.setWindowIcon(QIcon('images/verilog.png'))

        self.module_label = QLabel('Verilog Module:')
        self.module_input = QLineEdit()
        self.browse_button = QPushButton('Browse')
        self.browse_button.setFixedWidth(80)
        self.copy_button = QPushButton('Copy')
        self.copy_button.setFixedWidth(80)
        self.output_textedit = QTextEdit()
        self.result_label = QLabel('')

        self.option_group = QGroupBox()
        # self.option_group.setFixedHeight(35)
        self.option1 = QRadioButton('TestBench')
        self.option1.setFixedHeight(15)
        self.option2 = QRadioButton('Instance')
        self.option2.setFixedHeight(20)
        self.option1.setChecked(True)  # Set default option

        option_layout = QHBoxLayout()
        option_layout.addWidget(self.option1)
        option_layout.addWidget(self.option2)
        self.option_group.setLayout(option_layout)

        layoutH1 = QHBoxLayout()
        layoutH1.addWidget(self.module_label)
        layoutH1.addWidget(self.module_input)
        layoutH1.addWidget(self.browse_button)
        # layoutH1.addWidget(self.copy_button)

        spacer = QWidget()
        spacer.setFixedSize(120, 20)

        layoutH2 = QHBoxLayout()
        layoutH2.addWidget(spacer)
        layoutH2.addWidget(self.option_group)
        layoutH2.addWidget(self.copy_button)

        layoutV = QVBoxLayout()
        layoutV.addLayout(layoutH1)
        layoutV.addLayout(layoutH2)
        layoutV.addWidget(self.output_textedit)
        layoutV.addWidget(self.result_label)

        central_widget = QWidget()
        central_widget.setLayout(layoutV)
        self.setCentralWidget(central_widget)

        self.browse_button.clicked.connect(self.browse_file)
        self.copy_button.clicked.connect(self.copy_to_clipboard)

    def browse_file(self):
        # Implement file browsing functionality
        pass

    def copy_to_clipboard(self):
        # Implement copy to clipboard functionality
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestbenchGenerator()
    window.show()
    sys.exit(app.exec_())
