import os
import sys
from pathlib import Path
import base64
import collections
import shutil
import stat
import json
import paramiko
from scp import SCPClient

with open('config.json', 'r') as configJson:
    settings = json.load(configJson)


def createDir(dir):
    fullDir = Path(dir).resolve()
    if not os.path.exists(fullDir):
        fullDir.mkdir(parents=True)
    else:
        pass


def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

def force_copy(file, dest, name):
    try:
        shutil.copy(file, dest)
    except IOError:
        os.chmod(dest+"\\"+name, stat.S_IWRITE)
        shutil.copy(file, dest)

# Process temp directory
dirTemp = 'temp'
if (os.path.exists(Path(dirTemp).resolve())):
    shutil.rmtree(dirTemp, onerror=del_rw)
else:
    createDir(dirTemp)


# SSH Connection
print("\nConnecting to Synology...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(
    hostname=settings['synologyConfig']['host'],
    username=settings['synologyConfig']['username'],
    pkey=paramiko.RSAKey.from_private_key_file(
        settings['sshConfig']['privateKey'])
)
print("Connected")

# SCP Download
print("\nDownloading certificates...")
scp = SCPClient(ssh.get_transport())
scp.get('/usr/syno/etc/certificate/_archive/', dirTemp, True)
ssh.close()
print("Downloaded")

# Get domains in temp folder
print("\nGet domains from Synology's certificates...")
synoDomains = []
for folder in os.walk(dirTemp):
    if ('renew.json' in folder[2]):
        with open(folder[0] + "\\" + "renew.json", "r") as renewJson:
            synoDomain = collections.defaultdict(list)
            synoDomain["domain"] = json.load(renewJson)['domains']
            synoDomain["folder"] = folder[0]
            synoDomains.append(synoDomain)
    else:
        pass

print("Domains found: ")
for item in synoDomains:
    print(item["domain"])

# Match with user list in config.json
foldersMatch = []
print("\nChecking domains...")
for userCertificate in settings['certificatesConfig']:
    if not any(d['domain'] == userCertificate["domain"] for d in synoDomains):
        print("Certificate for", userCertificate["domain"], "was not found")
    else:
        print("Certificate for", userCertificate["domain"], "was found")
        folderMatch = collections.defaultdict(list)
        folderMatch["synoFolder"] = next(item for item in synoDomains if item["domain"] == userCertificate["domain"])["folder"]
        folderMatch["userFolder"] = userCertificate["folder"]
        foldersMatch.append(folderMatch)

# Copy files
print("\nCopy files...")
for match in foldersMatch:
    createDir(match["userFolder"])
    for fileName in os.listdir(match["synoFolder"]):
        if (fileName == "privkey.pem" or fileName == "cert.pem"):
            force_copy(os.path.join(match["synoFolder"], fileName), match["userFolder"], fileName)
            print("Copied " + match["synoFolder"] + "\\" + fileName + " -> " + match["userFolder"])
shutil.rmtree(dirTemp, onerror=del_rw)
print("Done\n")
    