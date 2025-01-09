from Backup import Backup
import subprocess
import os
import shutil

class P4Backup(Backup):
    def __init__(self):
        pass

    def DoBackupImpl(self, p4ServerRoot: str, backupDestination: str):
        """
        Args:
            - p4ServerRoot(str) the root directory of the p4Server to Backup 
            - backupDestination(str) the destination path to backup the p4Server, it should contains the name of the folder of the Backed up p4Server
        """

        try:
            self.LockServer()
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
            
            self.UnlockServer()
        except Exception as e:
            self.UnlockServer()
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
    
    def LockServer(self):
        subprocess.run(['p4', 'admin', 'lockserver'])

    def UnlockServer(self):
        subprocess.run(['p4', 'admin', "unlockserver"])

    def BackupComponent(self, src, destDir):
        try:
            if os.path.isdir(src):
                shutil.copytree(src, destDir)
            else:
                shutil.copy2(src, destDir)
            print(f"backed up: {src}->{destDir}")
        except Exception as e:
            print(f"error backing up {src}->{e}")


