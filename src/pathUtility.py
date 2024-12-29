from pathlib import Path

def GetSrcDir():
    return Path(__file__).resolve().parent

def GetPrjDir():
    return GetSrcDir().parent

