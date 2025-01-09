import shutil
import os

class Backup:
    def __init__(self):
        pass

    def DoBackup(self, folderToBackup: str, backupDestination: str):
        if not os.path.exists(folderToBackup):
            raise FileNotFoundError(f"Trying to back up a folder that does not exists: {folderToBackup}")

        destinationDir = os.path.dirname(backupDestination)
        if not os.path.exists(destinationDir):
            print(f"Backup Destination directory does not exists, making a new one: {destinationDir}")
            os.makedirs(destinationDir, exist_ok=True)
            
        self.DoBackupImpl(folderToBackup, backupDestination)

    def DoBackupImpl(self, folderToBackup: str,  backupDestination: str):
        print(f"trying to backup with the abstract base backup class, please use a concrete one")

    def BackupTerminated(self):
        print(f"stoppoing backup")

class DefaultSystemBackupImpl(Backup):
    def __init__(self):
        pass

    def DoBackupImpl(self, folderToBackup: str, backupDestination: str):
        shutil.copytree(folderToBackup, backupDestination)


        