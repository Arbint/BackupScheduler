import subprocess

def GetZFSPoolAbsPath(zfsPoolName):
    poolName = subprocess.run(["zfs", "get", "mountpoint", zfsPoolName])


poolPath = GetZFSPoolAbsPath("peforce_pool")
print(poolPath)