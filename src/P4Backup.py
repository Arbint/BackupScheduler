from Backup import Backup
import subprocess
import os
import shutil
import Logger
import re

class P4Backup(Backup):
    def __init__(self):
        self.p4ServiceName = "perforce"
        self.windowsStartServiceCmd = ["sc", "start", self.p4ServiceName]
        self.windowsStopServiceCmd = ["sc", "stop", self.p4ServiceName]
        self.windowsQueryServiceCmd = ["sc", "query", self.p4ServiceName]
        self.runningState = "RUNNING"
        self.stoppedState = "STOPPED"
        self.startPendingState = "START_PENDING"
        self.stopPendingState = "STOP_PENDING"
        

    def DoBackupImpl(self, p4ServerRoot: str, backupDestination: str):
        """
        Args:
            - p4ServerRoot(str) the root directory of the p4Server to Backup 
            - backupDestination(str) the destination path to backup the p4Server, it should contains the name of the folder of the Backed up p4Server
        """

        try:
            self.StopServer()
            os.makedirs(backupDestination, exist_ok = True)

            # backup checkpoint and journal
            checkpointSrcPath, journalSrcPath = self.CreateCheckpointAndRotateJournal(p4ServerRoot)  

            if checkpointSrcPath and os.path.exists(checkpointSrcPath):
                self.BackupComponent(checkpointSrcPath, backupDestination)
                self.BackupComponent(checkpointSrcPath + ".md5", backupDestination)

            if journalSrcPath and os.path.exists(journalSrcPath):
                self.BackupComponent(journalSrcPath, backupDestination)

            #backup depot files
            self.BackupDepots(p4ServerRoot, backupDestination)  

            #backup server configuration files
            configFileSrcPath = os.path.join(p4ServerRoot, "p4dctl.conf")
            configFileDestPath =  os.path.join(backupDestination, "p4dctl.conf")
            if os.path.exists(configFileSrcPath):
                self.BackupComponent(configFileSrcPath, configFileDestPath)
            
            self.RestartServer()
        except Exception as e:
            self.RestartServer()
            print(f"can't backup server: {e}")

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

    def RestartServer(self):
        print(f"####### Trying To Restart Server ############")
        if self.IsServerPendingStart() or self.IsServerRunning():
            print(f"Server Started or pending Start, not need to start again")
            return
        subprocess.run(self.windowsStartServiceCmd, check=True)   


    def StopServer(self):
        print(f"####### Trying To Stop Server ############")
        if self.IsServerPendingStop() or self.IsServerStopped():
            print(f"Server stopped or pending stop, no need to stop again")
            return 
        subprocess.run(self.windowsStopServiceCmd, check=True)


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
        self.RestartServer()

    def IsServerRunning(self):
        return self.GetServeryStat() == self.runningState

    def IsServerPendingStart(self):
        return self.GetServeryStat() == self.startPendingState

    def IsServerStopped(self):
        return self.GetServeryStat() == self.stoppedState

    def IsServerPendingStop(self):
        return self.GetServeryStat() == self.stopPendingState

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
        
    def GetAllUserEmails(self):
        users = subprocess.run("p4 users", capture_output=True, text=True)        
        emails = re.findall(r'<([^>]+)>', users.stdout)
        return emails


P4Backup().GetAllUserEmails()
