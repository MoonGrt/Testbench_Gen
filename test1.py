from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QComboBox, QVBoxLayout
from PyQt5.QtCore import Qt

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.time_label = QLabel('T:')
        self.time_input = QLineEdit()
        self.time_input.textChanged.connect(self.time_input_changed)
        self.time_unit = QComboBox()
        self.time_unit.addItems(["ps", "ns", "us", "ms", "s"])
        self.time_unit.setCurrentIndex(1)
        self.time_unit.currentIndexChanged.connect(self.update_frequency)

        self.frequency_label = QLabel('f:')
        self.frequency_input = QLineEdit()
        self.frequency_input.textChanged.connect(self.frequency_input_changed)
        self.frequency_unit = QComboBox()
        self.frequency_unit.addItems(["", "K", "M", "G"])
        self.frequency_unit.setCurrentIndex(2)
        self.frequency_unit.currentIndexChanged.connect(self.update_time)

        # 设置标志来控制更新流程
        self.updating = False

        layout = QVBoxLayout()
        layout.addWidget(self.time_label)
        layout.addWidget(self.time_input)
        layout.addWidget(self.time_unit)
        layout.addWidget(self.frequency_label)
        layout.addWidget(self.frequency_input)
        layout.addWidget(self.frequency_unit)

        self.setLayout(layout)

    def time_input_changed(self, text):
        if not self.updating:
            try:
                value = float(text)
            except ValueError:
                value = 0.0
            self.update_frequency_from_time(value)

    def frequency_input_changed(self, text):
        if not self.updating:
            try:
                value = float(text)
            except ValueError:
                value = 0.0
            self.update_time_from_frequency(value)

    def update_frequency(self, index):
        if not self.updating:
            time = float(self.time_input.text())
            self.update_frequency_from_time(time)

    def update_time(self, index):
        if not self.updating:
            frequency = float(self.frequency_input.text())
            self.update_time_from_frequency(frequency)

    def update_frequency_from_time(self, time):
        self.updating = True
        frequency = self.convert_to_frequency(time)
        self.frequency_input.setText(str(frequency))
        self.updating = False

    def update_time_from_frequency(self, frequency):
        self.updating = True
        time = self.convert_to_time(frequency)
        self.time_input.setText(str(time))
        self.updating = False

    def convert_to_frequency(self, time):
        time_unit_index = self.time_unit.currentIndex()
        time_unit_value = 10 ** ((time_unit_index+2) * 3)
        frequency_unit_index = self.frequency_unit.currentIndex()
        frequency_unit_value = 10 ** (frequency_unit_index * 3)
        return time_unit_value / (time * frequency_unit_value)

    def convert_to_time(self, frequency):
        frequency_unit_index = self.frequency_unit.currentIndex()
        frequency_unit_value = 10 ** (frequency_unit_index * 3)
        time_unit_index = self.time_unit.currentIndex()
        time_unit_value = 10 ** ((4-time_unit_index) * 3)
        return time_unit_value / (frequency * frequency_unit_value)

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()
