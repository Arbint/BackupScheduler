import os
import sys
import shutil
import threading
import time
from datetime import datetime
import schedule
from Duration import DurationModel
from Logger import Logger
from pathUtility import GetRecordFilePath
from Backup import DefaultSystemBackupImpl, Backup
import pickle
import stat


class BackupScheduler:
    def __init__(self):
        self.folderToBackup = ""
        self.backupDestination = ""
        self.backupImpl = DefaultSystemBackupImpl()
        self.shouldUpdateScheudler = False
        self.logCallbackFunc = None
        self.backupIntervalDuration = DurationModel()
        self.backupDelayDuration = DurationModel()

        self.schedulerThread = threading.Thread(target = self.UpdateBackupThread)
        self.schedulerThread.daemon = True
        self.schedulerThread.start()
        self.maxBackupCount = 2 

    def SetMaxbackupCount(self, maxBackupCount):
        self.maxBackupCount = maxBackupCount

    def UpdateBackupThread(self):
        while True:
            if self.shouldUpdateScheudler:
                schedule.run_pending()

            time.sleep(1)

    def DoOneTimeBackup(self):
        self.DoBackup()

    def ConfigureBackupImpl(self, backupImpl: Backup):
        self.backupImpl = backupImpl

    def SetFolderToBackup(self, newFolderToBackup: str):
        self.folderToBackup = newFolderToBackup

    def SetBackupDestination(self, newBackupDestination: str):
        self.backupDestination = newBackupDestination

    def StartBackupRoutine(self):
        self.CheckInputValidity()
        if self.backupDelayDuration.ToSecond() == 0:
            self.StartPeoridicalBackup()
        else:
            self.AddLog(f"Starting With Delay: {self.backupDelayDuration.ToSecond()} seconds")
            self.shouldUpdateScheudler=True
            schedule.clear()
            schedule.every(self.backupDelayDuration.ToSecond()).seconds.do(self.StartPeoridicalBackup)


    def StartPeoridicalBackup(self):
        self.CheckInputValidity()
        self.AddLog(f"starting backup {self.folderToBackup} to {self.backupDestination}, with interval: {self.backupIntervalDuration}", True)

        self.shouldUpdateScheudler = True
        schedule.clear()
        schedule.every(self.backupIntervalDuration.ToSecond()).seconds.do(self.DoBackup)


    def CheckInputValidity(self):
        backupIntervalSeconds = self.backupIntervalDuration.ToSecond()
        if backupIntervalSeconds <= 0:
            errorMsg = f"backup interval {backupIntervalSeconds} is invalid"
            self.AddLog(errorMsg, True)
            raise ValueError(errorMsg)

        if not os.path.exists(self.backupDestination):
            errorMsg = f"backup destination: {self.backupDestination} is invalid"
            self.AddLog(errorMsg, True)
            raise ValueError(errorMsg)

        if not os.path.exists(self.folderToBackup):
            errorMsg = f"backup folder: {self.folderToBackup} is invalid"
            self.AddLog(errorMsg, True)
            raise ValueError(errorMsg)

    def DoBackup(self):  
        backupTime = datetime.now()
        backupTimeStr = backupTime.strftime("%Y-%m-%d_%H-%M-%S")

        origFolderName = os.path.basename(self.folderToBackup)
        self.RemoveEarliestIfMaxCountReached(origFolderName)

        backupFolderName = f"{origFolderName}_{backupTimeStr}"

        backupDestinationPath = os.path.join(self.backupDestination, backupFolderName)
        self.backupImpl.DoBackup(self.folderToBackup, backupDestinationPath)

        self.WriteBackupRecord(backupTime, backupDestinationPath)

        logMsg = f"{backupTimeStr}: {self.folderToBackup} backed up to {backupDestinationPath}" 
        self.AddLog(logMsg, True)
    
    def AddLog(self, logMsg, logToConsole = False):
        Logger.AddLogEntry(logMsg, logToConsole)

        if self.logCallbackFunc:
            self.logCallbackFunc(logMsg)

    
    def RemoveEarliestIfMaxCountReached(self, folderToBackup):
        backedUpFolders = self.FindBackupsForFolderInDestination(folderToBackup)
        if len(backedUpFolders) <= 0:
            return

        if len(backedUpFolders) < self.maxBackupCount:
            return

        earliest = backedUpFolders[0]
        earliestTime = self.GetBackupTimeForFolder(earliest)
        for i in range(1, len(backedUpFolders)):
            folderName = backedUpFolders[i] 
            folderCreationTime = self.GetBackupTimeForFolder(folderName)    
            if folderCreationTime < earliestTime:
                earliestTime = folderCreationTime
                earliest = folderName

        shutil.rmtree(os.path.join(self.backupDestination, earliest), onerror=self.RemoveReadOnly)

    def RemoveReadOnly(self, func, path, excInfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def GetBackupTimeForFolder(self, folder):
        record = self.GetRecordDictionary()
        if folder in record:
            return record[folder]
        return self.GetFolderOSRecordedCreationTime(folder)


    def GetFolderOSRecordedCreationTime(self, folderName):
        folderPath = os.path.join(self.backupDestination, folderName)
        try:
            creationTime = os.path.getctime(folderPath)
            creationTime = datetime.fromtimestamp(creationTime)
            return creationTime
        except Exception as e:
            self.AddLog(f"Error retrieving creation time: {e}", True)
            return None


    def SetLogCallback(self, callbackFunc):
        self.logCallbackFunc = callbackFunc

    def StopBackupRoutine(self):
        self.AddLog(f"Stopping", True)
        self.backupImpl.Stop()
        self.shouldUpdateScheudler = False

    def BackupAppTerminated(self):
        self.backupImpl.BackupTerminated()

    def WriteBackupRecord(self, backupTime, folderName):
        record = self.GetRecordDictionary()
        record[folderName] = backupTime

        with open(GetRecordFilePath(), 'wb') as dataFile:
            pickle.dump(record, dataFile)

    def GetRecordDictionary(self):
        dataFilePath = GetRecordFilePath()
        try:
            with open(dataFilePath, 'rb') as dataFile:
                return pickle.load(dataFile)

        except FileNotFoundError:
            self.AddLog("can't find the record file, create a new empty dictionary", True)
            return {}

    def FindBackupsForFolderInDestination(self, folderName):
        outFolders = []
        for folder in os.listdir(self.backupDestination):
            if folderName in folder:
                outFolders.append(folder)

        return outFolders
