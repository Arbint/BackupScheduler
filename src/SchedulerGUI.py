from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QPushButton, QLabel, QGridLayout, QApplication, QLineEdit
from PySide6.QtGui import QIntValidator 
from Scheduler import Scheduler 

class ScheduleGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.scheduler = Scheduler()

        self.setWindowTitle("Backup Scheduler")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.BuildFolderQuerySection("Folder to Backup: ", self.scheduler.SetFolderToBackup)
        self.BuildFolderQuerySection("Backup Destionation: ", self.scheduler.SetBackupDestination)

        backupIntervalLabel = QLabel("Backup Interval Minutes")
        self.masterLayout.addWidget(backupIntervalLabel)
        
        self.backupIntervalLineEdit = QLineEdit()
        self.backupIntervalLineEdit.setValidator(QIntValidator(bottom=1))
        self.backupIntervalLineEdit.textChanged.connect(self.BackupIntervalChanged)
        self.masterLayout.addWidget(self.backupIntervalLineEdit)

        self.ctrlLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.ctrlLayout)

        self.startBackupRoutineBtn = QPushButton("Start Backup Routine")
        self.startBackupRoutineBtn.clicked.connect(self.scheduler.StartBackupRoutine)
        self.ctrlLayout.addWidget(self.startBackupRoutineBtn)

        self.stopRoutineBtn = QPushButton("Stop")
        self.stopRoutineBtn.clicked.connect(self.scheduler.StopBackupRoutine)
        self.ctrlLayout.addWidget(self.stopRoutineBtn)

    def BackupIntervalChanged(self):
        intervalStr = self.backupIntervalLineEdit.text()
        self.scheduler.SetBackupIntervalMintues(int(intervalStr))

    def BuildFolderQuerySection(self, label: str, ConfigFunc):
        sectionLayout = QHBoxLayout()
        self.masterLayout.addLayout(sectionLayout)

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