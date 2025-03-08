import paramiko
import os
import sys
import stat
from scp import SCPClient

class SSHAgent:
    def __init__(self):
        self.hostName = os.getenv("BACKUP_HOST_NAME")
        self.hostUserName = os.getenv("BACKUP_HOST_USER")
        #self.hostKeyPath = os.getenv("BACKUP_HOST_KEY")
        self.hostUserPwd = os.getenv("BACKUP_HOST_KEY_PASSWORD")

        #self.sshKey = paramiko.Ed25519Key(filename = self.hostKeyPath, password = self.hostUserPwd)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        #print(f"found host name: {self.hostName}")
        #print(f"found host user name: {self.hostUserName}")
        #print(f"found host user password: {self.hostUserPwd}")

    def ConnectToHost(self):
            print("connecting to server")
            self.client.connect(self.hostName,
                                allow_agent=False,
                                look_for_keys=False,
                                username = self.hostUserName,
                                password=self.hostUserPwd,timeout = 5)

            print("connection successful")


    def RunCmd(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())

    def SendFile(self, localPathToCopy, destination):
        sshCpy = SCPClient(self.client.get_transport())
        try:
            sshCpy.put(localPathToCopy, destination, recursive=os.path.isdir(localPathToCopy))
            print(f"copied from {localPathToCopy} to {self.hostName}:{destination}")
        finally:
            sshCpy.close()

    def GetFile(self, remotePathToCopy, destination):
        sshCpy = SCPClient(self.client.get_transport())
        try:
            sshCpy.get(remotePathToCopy, destination, recursive=self.IsRemotePathDir(remotePathToCopy))
            print(f"copied from {self.hostName}:{remotePathToCopy} to {destination}")
        finally:
            sshCpy.close()


    def IsRemotePathDir(self, remotePath):
        isDir = False
        sftp = self.client.open_sftp()
        try: 
            isDir = stat.S_ISDIR(sftp.stat(remotePath).st_mode)
        finally: 
            sftp.close()

        return isDir
        

    def CloseConnection(self):
        self.client.close()

    def __del__(self):
        print("closing connection")
        self.CloseConnection()
            
if __name__ == "__main__":
    sshAgent = SSHAgent()
    sshAgent.ConnectToHost()
    sshAgent.RunCmd("dir/p")
    #sshAgent.SendFile("/home/perforce/backup/2025-03-08_15-48-39", "D:/P4ServerBackups")
    #sshAgent.GetFile("D:/P4ServerBackups/2025-03-08_15-48-39", "/home/perforce/backup/receive")


