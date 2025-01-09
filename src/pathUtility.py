from pathlib import Path
import os
import Logger
import subprocess

def GetSrcDir():
    return Path(__file__).resolve().parent

def GetPrjDir():
    return GetSrcDir().parent

def GetDataDir():
    return GetPrjDir() / "Data"  
    
def GetRecordFilePath():
    dataDir = GetDataDir()
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)

    dataPath = dataDir / "data"

    return dataPath.resolve()

def CreateSnapshotWindows(dirToSnapShot):
    diskshadowScriptPath = os.path.join(GetSrcDir(), "diskshadowScript.txt")
    try:
        snapshotDrive = "X:"
        diskShadowScript = f"""
        set context persistent
        add volume {os.path.splitdirve(dirToSnapShot)[0]} alias "snapshotAlias"
        create
        expose %snapshotAlias% {snapshotDrive}
        """

        with open(diskshadowScriptPath, "w") as scriptFile:
            scriptFile.write(diskShadowScript)

        subprocess.run(["diskshadow", "/s", diskshadowScriptPath], check=True)
        os.remove(diskshadowScriptPath)
        return snapshotDrive + dirToSnapShot[len(os.path.splitdrive(dirToSnapShot)[0]):]

    except Exception as e:
        if os.path.exists(diskshadowScriptPath):
            os.remove(diskshadowScriptPath)

        Logger.Logger.AddLogEntry(f"Failed to create windows snapshot {e}", True)
        return None


print(CreateSnapshotWindows(GetPrjDir(), ))