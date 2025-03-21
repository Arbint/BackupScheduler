from pathlib import Path
import pathUtility
import os

class Logger:
    def __init__(self):
        print(f"Logger path is: {Logger.GetLogFilePath()}")

    @staticmethod
    def GetLogDir():
        logDir = pathUtility.GetPrjDir() / "log"
        if not os.path.exists(logDir):
            os.makedirs(logDir, exist_ok=True)

        return logDir

    @staticmethod
    def GetLogFilePath():
        return Logger.GetLogDir() / "log.txt"

    @staticmethod
    def GetErrorLogFilePath():
        return Logger.GetLogDir() / "Error.txt"

    @staticmethod 
    def AddLogEntry(entry: str, printToConsole : bool = True):
        if printToConsole:
            print(entry)

        with open(Logger.GetLogFilePath(), 'a') as logFile:
            logFile.write(f"{entry}\n")


    @staticmethod
    def AddErrorLog(entry: str, printToConsole: bool = True):
        if printToConsole:
            print(entry)

        with open(Logger.GetErrorLogFilePath(), 'a') as logFile:
            logFile.write(f"{entry}\n")
