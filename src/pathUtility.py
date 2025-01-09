from pathlib import Path
import os
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

def CreateSnapshotWindows(dirToSnapShot, snapshotDrive = "X:"):
    """
    this needs a windows server version, and cannot be used on regular windows os. 
    """
    diskshadowScriptPath = os.path.join(GetSrcDir(), "diskshadowScript.txt")
    try:
        diskShadowScript = f"""
        set context persistent
        add volume {os.path.splitdrive(dirToSnapShot)[0]} 
        expose * {snapshotDrive}
        create
        """

        with open(diskshadowScriptPath, "w") as scriptFile:
            scriptFile.write(diskShadowScript)

        subprocess.run(["diskshadow", "-s", diskshadowScriptPath], check=True)
        os.remove(diskshadowScriptPath)
        return snapshotDrive + dirToSnapShot[len(os.path.splitdrive(dirToSnapShot)[0]):]

    except Exception as e:
        if os.path.exists(diskshadowScriptPath):
            os.remove(diskshadowScriptPath)

        print(f"Failed to create windows snapshot {e}")
        return None

def DeleteWindowsSnapshot(snapShotDrive = "X:"):
    diskshadowScriptPath = os.path.join(GetSrcDir(), "diskshadowScript.txt")
    try:
        with open(diskshadowScriptPath, "w") as scriptFile:
            scriptFile.write(f"delete shadows exposed {snapShotDrive}")
    except Exception as e:
        print(f"Failed to remove snapshot")
