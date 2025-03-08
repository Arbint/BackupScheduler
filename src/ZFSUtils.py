import subprocess


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
    backupSnapshotName = f"{zfsPoolName}:@backup_$(date +%Y-%m-%d)"

    subprocess.run(["zfs", "snapshot", zfsPoolName], check = True)
    subprocess.run(["sudo", "zfs", "send", backupSnapshotName, ">", f"{backupDestination}/snapshot_backup.zfs"])

