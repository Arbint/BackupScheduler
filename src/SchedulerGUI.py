from PySide6.QtWidgets import (QWidget,
                               QVBoxLayout,
                               QHBoxLayout,
                               QFileDialog,
                               QPushButton,
                               QLabel,
                               QGridLayout,
                               QApplication, 
                               QLineEdit,
                               QListWidget,
                               QListWidgetItem,
                               QCheckBox,
                               QSlider
                               )

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from Scheduler import BackupScheduler 
from DurationView import DurationView
from Logger import Logger
from P4Backup import P4Backup
import ctypes
import sys

class ScheduleGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.scheduler = BackupScheduler()
        self.scheduler.ConfigureBackupImpl(P4Backup())
        self.scheduler.SetLogCallback(self.AddLog)

        self.setWindowTitle("Backup Scheduler")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.BuildFolderQuerySection(self.masterLayout, "Folder to Backup: ", self.scheduler.SetFolderToBackup)
        self.BuildFolderQuerySection(self.masterLayout, "Backup Destionation: ", self.scheduler.SetBackupDestination)

        self.BuildTimeConfigSection(self.masterLayout)
        self.BuildCtrlSection(self.masterLayout)

        self.BuildLogList(self.masterLayout)

    def BuildCtrlSection(self, parent):
        self.ctrlLayout = QVBoxLayout()
        parent.addLayout(self.ctrlLayout)

        maxCountSliderLayout = QHBoxLayout()
        self.ctrlLayout.addLayout(maxCountSliderLayout)

        self.backupMaxCountLabel = QLabel()
        self.SetMaxBackupCountLabel(self.scheduler.maxBackupCount)
        self.backupMaxCountSlider = QSlider(Qt.Horizontal, self)
        self.backupMaxCountSlider.setMinimum(1)
        self.backupMaxCountSlider.setMaximum(20)
        self.backupMaxCountSlider.setValue(self.scheduler.maxBackupCount)
        self.backupMaxCountSlider.setTickPosition(QSlider.TicksBelow)
        self.backupMaxCountSlider.setTickInterval(1)
        self.backupMaxCountSlider.valueChanged.connect(self.BackupMaxCountSliderUpdated)

        maxCountSliderLayout.addWidget(self.backupMaxCountLabel)
        maxCountSliderLayout.addWidget(self.backupMaxCountSlider)
        
        self.ctrlBtnLayout = QHBoxLayout()
        self.ctrlLayout.addLayout(self.ctrlBtnLayout)
        self.startBackupRoutineBtn = QPushButton("Start Backup Routine")
        self.startBackupRoutineBtn.clicked.connect(self.scheduler.StartBackupRoutine)
        self.ctrlBtnLayout.addWidget(self.startBackupRoutineBtn)

        self.stopRoutineBtn = QPushButton("Stop Backup Routine")
        self.stopRoutineBtn.clicked.connect(self.scheduler.StopBackupRoutine)
        self.ctrlBtnLayout.addWidget(self.stopRoutineBtn)

        self.doOneTimeBackupBtn = QPushButton("Onetime Backup Now")
        self.doOneTimeBackupBtn.clicked.connect(self.scheduler.DoOneTimeBackup)
        self.ctrlBtnLayout.addWidget(self.doOneTimeBackupBtn)

    def BackupMaxCountSliderUpdated(self):
        newCount = self.backupMaxCountSlider.value()
        self.scheduler.SetMaxbackupCount(newCount)
        self.SetMaxBackupCountLabel(newCount)

    def SetMaxBackupCountLabel(self, newCount):
        self.backupMaxCountLabel.setText(f"Backup Max Count: {newCount}      ")

    def BuildTimeConfigSection(self, parent):
        backupIntervalLabel = QLabel("Backup Interval")
        parent.addWidget(backupIntervalLabel)
        
        durationView = DurationView()
        durationView.hoursChanged.connect(self.scheduler.duration.SetHours)
        durationView.daysChanged.connect(self.scheduler.duration.SetDays)
        durationView.minutesChanged.connect(self.scheduler.duration.SetMinutes)
        durationView.secondChanged.connect(self.scheduler.duration.SetSeconds)

        parent.addWidget(durationView)


    def BuildLogList(self, parentLayout):
        sectionLayout = QVBoxLayout()
        parentLayout.addLayout(sectionLayout) 

        logLabel = QLabel("Log")
        sectionLayout.addWidget(logLabel)

        self.logList = QListWidget()
        sectionLayout.addWidget(self.logList)


    def BuildFolderQuerySection(self, parentLayout, label: str, ConfigFunc):
        sectionLayout = QHBoxLayout()
        parentLayout.addLayout(sectionLayout)

        folderLabel = QLabel(label)
        sectionLayout.addWidget(folderLabel)

        folderLineEdit = QLineEdit()
        folderLineEdit.setEnabled(False)
        sectionLayout.addWidget(folderLineEdit)

        selectFolderBtn = QPushButton("...")
        selectFolderBtn.clicked.connect(lambda : self.SelectFolder(folderLineEdit, ConfigFunc))
        sectionLayout.addWidget(selectFolderBtn)


    def SelectFolder(self, folderLineEdit: QLineEdit, DirConfigFunc):
        dir = QFileDialog().getExistingDirectory()
        DirConfigFunc(dir)
        folderLineEdit.setText(dir)


    def AddLog(self, logEntry):
        self.logList.addItem(logEntry)

def IsAdmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except: 
        return False

if __name__ == "__main__":
    if not IsAdmin():
        print("Requesting admin privileges...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    else:
        app = QApplication()
        gui = ScheduleGUI()
        gui.show()
        app.exec()
        gui.scheduler.BackupAppTerminated()


