from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QLayout
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Signal

class DurationView(QWidget):
    firstDelayChanged = Signal(int)
    daysChanged = Signal(int)
    hoursChanged = Signal(int)
    minutesChanged = Signal(int)
    secondChanged = Signal(int)

    def __init__(self):
        super().__init__()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.AddNumEntry(self.masterLayout, "First Delay", self.firstDelayChanged)

        peoridialLayout = QHBoxLayout()
        self.masterLayout.addLayout(peoridialLayout)
        self.AddNumEntry(peoridialLayout, "Days", self.daysChanged)
        self.AddNumEntry(peoridialLayout, "Hours", self.hoursChanged)
        self.AddNumEntry(peoridialLayout, "Minutes", self.minutesChanged)
        self.AddNumEntry(peoridialLayout, "second", self.secondChanged)

    def AddNumEntry(self, parent: QLayout, label: str, changeSignal):
        label = QLabel(label)
        parent.addWidget(label)

        lineEdit = QLineEdit()
        lineEdit.setValidator(QIntValidator())
        lineEdit.textChanged.connect(lambda : changeSignal.emit(int(lineEdit.text())))
        parent.addWidget(lineEdit)
