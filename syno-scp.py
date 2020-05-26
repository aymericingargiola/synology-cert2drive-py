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
    full_dir = Path(dir).resolve()
    if not os.path.exists(full_dir):
        full_dir.mkdir(parents=True)
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
dir_temp = 'temp'
if (os.path.exists(Path(dir_temp).resolve())):
    shutil.rmtree(dir_temp, onerror=del_rw)
else:
    createDir(dir_temp)


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
scp.get('/usr/syno/etc/certificate/_archive/', dir_temp, True)
ssh.close()
print("Downloaded")

# Get domains in temp folder
print("\nGet domains from Synology's certificates...")
syno_domains = []
for folder in os.walk(dir_temp):
    if ('renew.json' in folder[2]):
        with open(folder[0] + "\\" + "renew.json", "r") as renewJson:
            syno_domain = collections.defaultdict(list)
            syno_domain["domain"] = json.load(renewJson)['domains']
            syno_domain["folder"] = folder[0]
            syno_domains.append(syno_domain)
    else:
        pass

print("Domains found: ")
for item in syno_domains:
    print(item["domain"])

# Match with user list in config.json
folders_match = []
print("\nChecking domains...")
for user_certificate in settings['certificatesConfig']:
    if not any(d['domain'] == user_certificate["domain"] for d in syno_domains):
        print("Certificate for", user_certificate["domain"], "was not found")
    else:
        print("Certificate for", user_certificate["domain"], "was found")
        folder_match = collections.defaultdict(list)
        folder_match["synoFolder"] = next(item for item in syno_domains if item["domain"] == user_certificate["domain"])["folder"]
        folder_match["userFolder"] = user_certificate["folder"]
        folders_match.append(folder_match)
if(len(folders_match) == 0):
    shutil.rmtree(dir_temp, onerror=del_rw)
    sys.exit("No domains available")

# Copy files
print("\nCopy files...")
for match in folders_match:
    createDir(match["userFolder"])
    for fileName in os.listdir(match["synoFolder"]):
        if (fileName == "privkey.pem" or fileName == "cert.pem"):
            force_copy(os.path.join(match["synoFolder"], fileName), match["userFolder"], fileName)
            print("Copied " + match["synoFolder"] + "\\" + fileName + " -> " + match["userFolder"])
shutil.rmtree(dir_temp, onerror=del_rw)
print("Done\n")
    