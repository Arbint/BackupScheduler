import os
import sys
import shutil
import threading
import time
from datetime import datetime
import schedule

from Logger import Logger

class BackupScheduler:
    def __init__(self):
        self.folderToBackup = ""
        self.backupDestination = ""
        self.backupIntervalMinutes = 5 
        self.shouldUpdateScheudler = False
        self.logCallbackFunc = None

        self.schedulerThread = threading.Thread(target = self.UpdateBackupThread)
        self.schedulerThread.daemon = True
        self.schedulerThread.start()

    def UpdateBackupThread(self):
        while True:
            if self.shouldUpdateScheudler:
                schedule.run_pending()

            time.sleep(1)

    def SetBackupIntervalMintues(self, newMinutes: int):
        self.backupIntervalMinutes = newMinutes

    def SetFolderToBackup(self, newFolderToBackup: str):
        self.folderToBackup = newFolderToBackup

    def SetBackupDestination(self, newBackupDestination: str):
        self.backupDestination = newBackupDestination

    def StartBackupRoutine(self):
        print(f"starting backup {self.folderToBackup} to {self.backupDestination}, with interval: {self.backupIntervalMinutes} minutes")

        self.shouldUpdateScheudler = True
        schedule.clear()
        schedule.every(self.backupIntervalMinutes).seconds.do(self.DoBackup)
        
    def DoBackup(self):  
        backupTime = datetime.now()
        backupTimeStr = backupTime.strftime("%Y-%m-%d_%H-%M-%S")

        origFolderName = os.path.basename(self.folderToBackup)

        backupFolderName = f"{origFolderName}_{backupTimeStr}"

        logMsg = f"{backupTimeStr}: copying {self.folderToBackup} to {self.backupDestination}/{backupFolderName}" 
        print(logMsg)
        Logger.AddLogEntry(logMsg)

        if self.logCallbackFunc:
            self.logCallbackFunc(logMsg)

    def SetLogCallback(self, callbackFunc):
        self.logCallbackFunc = callbackFunc

    def StopBackupRoutine(self):
        print(f"Stopping")
        self.shouldUpdateScheudler = False
