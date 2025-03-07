from Scheduler import BackupScheduler
from P4Backup import P4Backup
import ctypes
import sys

class SchedulerCLI:
    def __init__(self, **args):
        
        self.schedule = BackupScheduler()
        self.schedule.ConfigureBackupImpl(P4Backup())


def IsAdmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except: 
        return False

if __name__ == "__main__":
    if not IsAdmin():
        print("Requesting admin privileges...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.Exit(0)
    else:
        SchedulerCLI(sys.argv)
