import os
import sys
import shutil

class Scheduler:
    def __init__(self):
        self.folderToBackup = ""
        self.backupDestination = ""
        self.backupIntervalMinutes = 5 

    def SetBackupIntervalMintues(self, newMinutes: int):
        self.backupIntervalMinutes = newMinutes

    def SetFolderToBackup(self, newFolderToBackup: str):
        self.folderToBackup = newFolderToBackup

    def SetBackupDestination(self, newBackupDestination: str):
        self.backupDestination = newBackupDestination

    def StartBackupRoutine(self):
        print(f"starting backup {self.folderToBackup} to {self.backupDestination}, with interval: {self.backupIntervalMinutes} minutes")

    def StopBackupRoutine(self):
        print(f"Stopping")