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

            #create the checkpoint and journal
            checkpointFile, journalFile = self.CreateCheckpoint(p4ServerRoot)

            # backup checkpoint and journal
            checkpointPath = os.path.join(backupDestination, "checkpoint.1")
            if checkpointFile and os.path.exists(checkpointFile):
                self.BackupComponent(checkpointFile, checkpointPath)
            journalPath = os.path.join(backupDestination, "journal.1")
            if journalFile and os.path.exists(journalFile):
                self.BackupComponent(journalFile, journalPath)

            #compress checkpoint
            # if os.path.exist(checkpointPath):
            #     shutil.make_archive(checkpointPath, "gzip", root_dir = backupDir, base_dir="checkpoint.1")
            #     os.remove(checkpointPath)

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

    def CreateCheckpoint(self, p4ServerRoot):
        #ask p4d to create the journal and checkpoint file
        subprocess.run(['p4d', '-r', p4ServerRoot, '-jc'], check=True)

        checkpointFile = os.path.join(p4ServerRoot, "checkpoint.1")
        journalFile = os.path.join(p4ServerRoot, "journal.1")

        return checkpointFile, journalFile
     
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

    def BackupComponent(src, destDir):
        try:
            if os.path.isdir(src):
                shutil.copytree(src, destDir)
            else:
                shutil.copy2(src, destDir)
            print(f"backed up: {src}->{destDir}")
        except Exception as e:
            print(f"error backing up {src}->{e}")


