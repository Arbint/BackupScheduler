from pathlib import Path
import os

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

