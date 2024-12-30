from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QLayout
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Signal

class DurationView(QWidget):
    daysChanged = Signal(int)
    hoursChanged = Signal(int)
    minutesChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        self.AddNumEntry(self.masterLayout, "Days", self.daysChanged)
        self.AddNumEntry(self.masterLayout, "Hours", self.hoursChanged)
        self.AddNumEntry(self.masterLayout, "Minutes", self.minutesChanged)

    def AddNumEntry(self, parent: QLayout, label: str, changeSignal):
        label = QLabel(label)
        parent.addWidget(label)

        lineEdit = QLineEdit()
        lineEdit.setValidator(QIntValidator())
        lineEdit.textChanged.connect(lambda : changeSignal.emit(int(lineEdit.text())))
        parent.addWidget(lineEdit)
