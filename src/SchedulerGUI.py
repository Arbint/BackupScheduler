from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QPushButton, QLabel, QGridLayout, QApplication, QLineEdit, QListWidget, QListWidgetItem, QCheckBox
from PySide6.QtGui import QIntValidator
from Scheduler import BackupScheduler 
from DurationView import DurationView

class ScheduleGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.scheduler = BackupScheduler()
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

        self.flipFlopCheckbox = QCheckBox("Flip Flop")
        self.flipFlopCheckbox.setChecked(self.scheduler.filpFlopState)
        self.flipFlopCheckbox.checkStateChanged.connect(self.FlipFlopStateUpdated)
        self.ctrlLayout.addWidget(self.flipFlopCheckbox)
        
        self.buttonLayout = QHBoxLayout()
        self.ctrlLayout.addLayout(self.buttonLayout)
        self.startBackupRoutineBtn = QPushButton("Start Backup Routine")
        self.startBackupRoutineBtn.clicked.connect(self.scheduler.StartBackupRoutine)
        self.buttonLayout.addWidget(self.startBackupRoutineBtn)

        self.stopRoutineBtn = QPushButton("Stop")
        self.stopRoutineBtn.clicked.connect(self.scheduler.StopBackupRoutine)
        self.buttonLayout.addWidget(self.stopRoutineBtn)

    def FlipFlopStateUpdated(self):
        checked = self.flipFlopCheckbox.isChecked()
        self.scheduler.SetFlipFlopState(checked)


    def BuildTimeConfigSection(self, parent):
        backupIntervalLabel = QLabel("Backup Interval Minutes")
        parent.addWidget(backupIntervalLabel)
        
        durationView = DurationView()
        durationView.hoursChanged.connect(self.scheduler.duration.SetHours)
        durationView.daysChanged.connect(self.scheduler.duration.SetDays)
        durationView.minutesChanged.connect(self.scheduler.duration.SetMinutes)
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

if __name__ == "__main__":
    app = QApplication()

    gui = ScheduleGUI()
    gui.show()

    app.exec()