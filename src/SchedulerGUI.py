from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QPushButton, QLabel, QGridLayout, QApplication, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtGui import QIntValidator
from Scheduler import BackupScheduler 

class ScheduleGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.scheduler = BackupScheduler()
        self.scheduler.SetLogCallback(self.AddLog)

        self.setWindowTitle("Backup Scheduler")
        self.masterLayout = QHBoxLayout()
        self.setLayout(self.masterLayout)

        self.configureLayout = QVBoxLayout()
        self.masterLayout.addLayout(self.configureLayout)

        self.BuildFolderQuerySection(self.configureLayout, "Folder to Backup: ", self.scheduler.SetFolderToBackup)
        self.BuildFolderQuerySection(self.configureLayout, "Backup Destionation: ", self.scheduler.SetBackupDestination)

        backupIntervalLabel = QLabel("Backup Interval Minutes")
        self.configureLayout.addWidget(backupIntervalLabel)
        
        self.backupIntervalLineEdit = QLineEdit()
        self.backupIntervalLineEdit.setValidator(QIntValidator(bottom=1))
        self.backupIntervalLineEdit.textChanged.connect(self.BackupIntervalChanged)
        self.configureLayout.addWidget(self.backupIntervalLineEdit)

        self.ctrlLayout = QHBoxLayout()
        self.configureLayout.addLayout(self.ctrlLayout)

        self.startBackupRoutineBtn = QPushButton("Start Backup Routine")
        self.startBackupRoutineBtn.clicked.connect(self.scheduler.StartBackupRoutine)
        self.ctrlLayout.addWidget(self.startBackupRoutineBtn)

        self.stopRoutineBtn = QPushButton("Stop")
        self.stopRoutineBtn.clicked.connect(self.scheduler.StopBackupRoutine)
        self.ctrlLayout.addWidget(self.stopRoutineBtn)

        self.BuildLogList(self.configureLayout)

    def AddLog(self, logEntry):
        self.logList.addItem(logEntry)

    def BuildLogList(self, parentLayout):
        sectionLayout = QVBoxLayout()
        parentLayout.addLayout(sectionLayout) 

        logLabel = QLabel("Log")
        sectionLayout.addWidget(logLabel)

        self.logList = QListWidget()
        sectionLayout.addWidget(self.logList)


    def BackupIntervalChanged(self):
        intervalStr = self.backupIntervalLineEdit.text()
        self.scheduler.SetBackupIntervalMintues(int(intervalStr))

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

if __name__ == "__main__":
    app = QApplication()

    gui = ScheduleGUI()
    gui.show()

    app.exec()