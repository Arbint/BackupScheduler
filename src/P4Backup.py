from Backup import Backup
import subprocess
import os
import shutil
import Logger
from ZFSUtils import GetZFSPoolAbsPath, CreateZFSSnapshot

import re
from Communcation import Emailer


class P4Backup(Backup):
    def __init__(self):
        super().__init__()
        self.p4ServiceName = "perforce"
        self.emailer = Emailer()
        self.shouldInfomUsers = False
        self.lockServerCmd = ['p4', "admin", "lock"]
        self.unlockServerCmd = ['p4', "admin", "unlock"]

    def PreBackup(self):
        pass

    def PostBackup(self):
        pass

    def LockServer(self):
        subprocess.run(self.lockServerCmd, check=True)

    def UnlockServerCmd(self):
        subprocess.run(self.unlockServerCmd, check=True)


    def DoBackupImpl(self, p4ServerRoot: str, backupDestination: str):
        """
        Args:
            - p4ServerRoot(str) the root directory of the p4Server to Backup 
            - backupDestination(str) the destination path to backup the p4Server, it should contains the name of the folder of the Backed up p4Server
        """

        try:
            self.PreBackup()

            os.makedirs(backupDestination, exist_ok = True)

            self.BackupCheckPointAndJournal(p4ServerRoot, backupDestination)
            self.BackupDepots(p4ServerRoot, backupDestination)  

            #TODO: this probably do not work...
            self.BackupServerConfigurationFiles(p4ServerRoot, backupDestination)
            
            self.PostBackup()

        except Exception as e:
            self.PostBackup()
            print(f"can't backup server: {e}")


    def BackupServerConfigurationFiles(self, p4ServerRoot, backupDestination):
        configFileSrcPath = os.path.join(p4ServerRoot, "p4dctl.conf")
        configFileDestPath =  os.path.join(backupDestination, "p4dctl.conf")
        if os.path.exists(configFileSrcPath):
            self.BackupComponent(configFileSrcPath, configFileDestPath)


    def BackupCheckPointAndJournal(self, p4ServerRoot, backupDestination):
        checkpointSrcPath, journalSrcPath = self.CreateCheckpointAndRotateJournal(p4ServerRoot)  

        if checkpointSrcPath and os.path.exists(checkpointSrcPath):
            self.BackupComponent(checkpointSrcPath, backupDestination)
            self.BackupComponent(checkpointSrcPath + ".md5", backupDestination)

        if journalSrcPath and os.path.exists(journalSrcPath):
            self.BackupComponent(journalSrcPath, backupDestination)

    def CreateCheckpointAndRotateJournal(self, p4ServerRoot):
        #ask p4d to create the journal and checkpoint file
        subprocess.run(['p4d', '-r', p4ServerRoot, '-jc'], check=True)

        checkpointFileName = self.GetFileWithNewestNumSubfix(p4ServerRoot, "checkpoint")
        journalFileName  = self.GetFileWithNewestNumSubfix(p4ServerRoot, "journal")

        checkpointFilePath = os.path.join(p4ServerRoot, checkpointFileName)
        journalFilePath = os.path.join(p4ServerRoot, journalFileName)

        return checkpointFilePath, journalFilePath

    def GetFileWithNewestNumSubfix(self, p4ServerRootDir, fileNameBase):
        num = 0
        newestFileName = ""
        for fileName in os.listdir(p4ServerRootDir):
            if fileNameBase in fileName:
                fileNumStr = fileName.split('.')[-1]
                if not fileNumStr.isdigit():
                    continue

                fileNum = int(fileNumStr)
                if  fileNum > num:
                    num = fileNum
                    newestFileName = fileName

        return newestFileName
     
    def BackupDepots(self, p4ServerRoot, backupDestination):
        try:
            depots =[d for d in os.listdir(p4ServerRoot) if os.path.isdir(os.path.join(p4ServerRoot, d))]
            for depot in depots:
                depotSrcPath = os.path.join(p4ServerRoot, depot)
                depotDestPath = os.path.join(backupDestination, depot)
                if os.path.exists(depotSrcPath):
                    self.BackupComponent(depotSrcPath, depotDestPath)
        except Exception as e:
            print(f"Can't backup depot {e}")


    def BackupComponent(self, src, destDir):
        try:
            if os.path.isdir(src):
                shutil.copytree(src, destDir)
            else:
                shutil.copy2(src, destDir)
            print(f"backed up: {src}->{destDir}")
        except Exception as e:
            print(f"error backing up {src}->{e}")


    def BackupTerminated(self):
        Logger.Logger.AddLogEntry(f"p4 backup process terminated, re institiating server")
        self.PostBackup()

    def IsServerRunning(self):
        return self.GetServeryStat() == self.runningState

    def IsServerPendingStart(self):
        return self.GetServeryStat() == self.startPendingState

    def IsServerStopped(self):
        return self.GetServeryStat() == self.stoppedState

    def IsServerPendingStop(self):
        return self.GetServeryStat() == self.stopPendingState

        
    def GetAllUserEmails(self):
        users = subprocess.run("p4 users", capture_output=True, text=True)        
        emails = re.findall(r'<([^>]+)>', users.stdout)
        return emails

    def SendEmailToAllUsers(self, subject, msg):
        if not self.shouldInfomUsers:
            return

        self.emailer.SendGroupEmail(self.GetAllUserEmails(), subject, msg)


    def GetServerInBackupModeMsg(self):
        return """This an automated email, the perforce server is down and in backup mode, you will get an message when it's back online.
        """

    def GetServerBackOnlineModeMsg(self):
        return """This an aotomated email, the perfore server is backup online."""


class P4BackupWindows(P4Backup):
    def __init__(self):
        super().__init__()
        self.windowsStartServiceCmd = ["sc", "start", self.p4ServiceName]
        self.windowsStopServiceCmd = ["sc", "stop", self.p4ServiceName]
        self.windowsQueryServiceCmd = ["sc", "query", self.p4ServiceName]
        self.runningState = "RUNNING"
        self.stoppedState = "STOPPED"
        self.startPendingState = "START_PENDING"
        self.stopPendingState = "STOP_PENDING"


    def PreBackup(self):
        self.StopServer()


    def PostBackup(self):
        self.RestartServer()


    def RestartServer(self):
        print(f"####### Trying To Restart Server ############")
        if self.IsServerPendingStart() or self.IsServerRunning():
            print(f"Server Started or pending Start, not need to start again")
            return
        subprocess.run(self.windowsStartServiceCmd, check=True)   
        self.SendEmailToAllUsers("Perforce Server Is Back Online", self.GetServerBackOnlineModeMsg())

    def StopServer(self):
        print(f"####### Trying To Stop Server ############")
        if self.IsServerPendingStop() or self.IsServerStopped():
            print(f"Server stopped or pending stop, no need to stop again")
            return 
        subprocess.run(self.windowsStopServiceCmd, check=True)
        self.SendEmailToAllUsers("Perforce Server In Backup Mode", self.GetServerBackOnlineModeMsg())


    def GetServeryStat(self):
        try: 
            result = subprocess.run(self.windowsQueryServiceCmd, capture_output=True, text=True)
            print(f"---------------quried server stat: {result.stdout} \n -------------")
            if self.runningState in result.stdout:
                return self.runningState
            
            if self.startPendingState in result.stdout:
                return self.startPendingState

            if self.stopPendingState in result.stdout:
                return self.stopPendingState

        except subprocess.CalledProcessError as e:
            print(f"Error checking server status: {e}")
            return None


class P4BackupLinux(P4Backup):
    def __init__(self):
        super().__init__()
        print("Linux Backup Used")

    def PreBackup(self): 
        self.lockServer()

    def PostBackup(self):
        self.unlockServer()


class P4BackupLinuxWithZFS(P4Backup):
    def __init__(self):
        super().__init__()
        print("Linux backup used with ZFS")


    def DoBackupImpl(self, zfsPoolName: str,  backupDestination: str):
        try:
            poolLocation = GetZFSPoolAbsPath(zfsPoolName)
            backupSubDir = self.CreateBackupSubDir(backupDestination)

            print(f"backing up server pool at location: {poolLocation}")
            self.BackupCheckPointAndJournal(poolLocation, backupSubDir)
            CreateZFSSnapshot(zfsPoolName, backupSubDir)

        except subprocess.CalledProcessError as e:
            print(f"Backup failed: {e}")

        


Backuper = P4BackupLinuxWithZFS()
Backuper.DoBackupImpl("perforce_pool", "/home/perforce/backup/")
