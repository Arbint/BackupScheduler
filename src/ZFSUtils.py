import subprocess
from datetime import datetime

def ConvertSubprocessResultToDataSet(result):
    resultLines = result.stdout.strip().split("\n")
    if len(resultLines) <= 1:
        return None

    headers = RemoveEmptyEntry(resultLines[0].strip().split(" "))
    
    outDict = {}
    for header in headers:
        outDict[header] = []

    for entryLine in resultLines[1:]:
        entryValues = RemoveEmptyEntry(entryLine.split(" "))
        
        for i in range(0, len(entryValues)):
            entryKey = headers[i]
            entryValue = entryValues[i]
            outDict[entryKey] = entryValue

    return outDict

def RemoveEmptyEntry(inList):
    outList = []
    for item in inList:
        if item == "":
            continue

        outList.append(item)

    return outList


def GetZFSPoolAbsPath(zfsPoolName):
    processResult = subprocess.run(["zfs", "get", "mountpoint", zfsPoolName], capture_output=True, text=True, check=True)
    resultDict = ConvertSubprocessResultToDataSet(processResult)
    return resultDict["VALUE"]


def CreateZFSSnapshot(zfsPoolName, backupDestination):

    timeSubfix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backupSnapshotName = f"{zfsPoolName}@backup_{timeSubfix}"

    createSnapshotCmd = ["zfs", "snapshot", backupSnapshotName] 
    print(f"creating snapshot with cmd: {createSnapshotCmd}")
    subprocess.run(createSnapshotCmd, check=True)

    sendCmd = f"zfs send {backupSnapshotName} > {backupDestination}/snapshot_backup.zfs"
    print(f"send snapshot with cmd: {sendCmd}")
    subprocess.run(sendCmd, shell=True, check=True)

