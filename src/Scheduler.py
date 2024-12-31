import os
import sys
import shutil
import threading
import time
from datetime import datetime
import schedule
from Duration import DurationModel

from Logger import Logger

class BackupScheduler:
    def __init__(self):
        self.folderToBackup = ""
        self.backupDestination = ""
        self.shouldUpdateScheudler = False
        self.logCallbackFunc = None
        self.duration = DurationModel()

        self.schedulerThread = threading.Thread(target = self.UpdateBackupThread)
        self.schedulerThread.daemon = True
        self.schedulerThread.start()
        self.filpFlopState = True

    def SetFlipFlopState(self, newFlipFlopState):
        self.filpFlopState = newFlipFlopState

    def UpdateBackupThread(self):
        while True:
            if self.shouldUpdateScheudler:
                schedule.run_pending()

            time.sleep(1)

    def SetFolderToBackup(self, newFolderToBackup: str):
        self.folderToBackup = newFolderToBackup

    def SetBackupDestination(self, newBackupDestination: str):
        self.backupDestination = newBackupDestination

    def StartBackupRoutine(self):
        print(f"starting backup {self.folderToBackup} to {self.backupDestination}, with interval: {self.duration}")

        self.shouldUpdateScheudler = True
        schedule.clear()
        schedule.every(self.duration.ToMinutes()).minutes.do(self.DoBackup)
        
    def DoBackup(self):  
        backupTime = datetime.now()
        backupTimeStr = backupTime.strftime("%Y-%m-%d_%H-%M-%S")

        origFolderName = os.path.basename(self.folderToBackup)
        backupFolderName = f"{origFolderName}_{backupTimeStr}"

        backupDestinationPath = os.path.join(self.backupDestination, backupFolderName)
        shutil.copytree(self.folderToBackup, backupDestinationPath)

        logMsg = f"{backupTimeStr}: copying {self.folderToBackup} to {backupDestinationPath}" 
        print(logMsg)
        Logger.AddLogEntry(logMsg)

        if self.logCallbackFunc:
            self.logCallbackFunc(logMsg)

    def SetLogCallback(self, callbackFunc):
        self.logCallbackFunc = callbackFunc

    def StopBackupRoutine(self):
        print(f"Stopping")
        self.shouldUpdateScheudler = False
