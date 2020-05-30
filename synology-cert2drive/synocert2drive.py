import os
import sys
import pathlib
import base64
import collections
import shutil
import stat
import json
import paramiko
import scp

with open('config.json', 'r') as configJson:
    settings = json.load(configJson)


def create_dir(dir):
    full_dir = pathlib.Path(dir).resolve()
    if not os.path.exists(full_dir):
        full_dir.mkdir(parents=True)


def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


def force_copy(file, dest, name):
    try:
        shutil.copy(file, dest)
    except IOError:
        os.chmod(dest+"\\"+name, stat.S_IWRITE)
        shutil.copy(file, dest)


def update_cert():
    result = collections.defaultdict(list)

    # Process temp directory
    dir_temp = 'temp'
    if (os.path.exists(pathlib.Path(dir_temp).resolve())):
        shutil.rmtree(dir_temp, onerror=del_rw)
    else:
        create_dir(dir_temp)

    # SSH Connection
    print("\nConnecting to Synology...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(
            hostname=settings['synology_config']['host'],
            port=settings['synology_config']['port'],
            username=settings['synology_config']['username'],
            pkey=paramiko.RSAKey.from_private_key_file(
                settings['ssh_config']['private_key'])
        )
    except Exception as exception:
        if (type(exception).__name__ == "UnicodeDecodeError"):
            print("Error : This private key is not supported")
            result["message"] = "This private key is not supported"
        elif (type(exception).__name__ == "FileNotFoundError"):
            print("Error : Your private key was not found")
            result["message"] = "Your private key was not found"
        elif (type(exception).__name__ == "NoValidConnectionsError" or type(exception).__name__ == "SSHException"):
            print("Error : Port is not reachable")
            result["message"] = "Port is not reachable"
        elif (type(exception).__name__ == "gaierror"):
            print("Error : Host is not reachable")
            result["message"] = "Host is not reachable"
        elif (type(exception).__name__ == "AuthenticationException"):
            print("Error : Authentication failed")
            result["message"] = "Authentication failed"
        elif (type(exception).__name__ == "OSError"):
            return update_cert()
        else:
            print(type(exception).__name__)
            print(exception)
            result["message"] = type(exception).__name__
        result["code"] = -1
        return result
    print("Connected")

    # SCP Download
    print("\nDownloading certificates...")
    scp_client = scp.SCPClient(ssh.get_transport())
    scp_client.get('/usr/syno/etc/certificate/_archive/', dir_temp, True)
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
    for user_certificate in settings['certificates_config']:
        if not any(d['domain'] == user_certificate["domain"] for d in syno_domains):
            print("Certificate for",
                  user_certificate["domain"], "was not found")
        else:
            print("Certificate for", user_certificate["domain"], "was found")
            folder_match = collections.defaultdict(list)
            folder_match["syno_folder"] = next(
                item for item in syno_domains if item["domain"] == user_certificate["domain"])["folder"]
            folder_match["user_folder"] = user_certificate["folder"]
            folders_match.append(folder_match)
    if(len(folders_match) == 0):
        shutil.rmtree(dir_temp, onerror=del_rw)
        print("No domains available")
        result["code"] = -1
        result["message"] = "No domains available"
        return result

    # Copy files
    print("\nCopy files...")
    for match in folders_match:
        create_dir(match["user_folder"])
        for file_name in os.listdir(match["syno_folder"]):
            if (file_name == "privkey.pem" or file_name == "cert.pem"):
                force_copy(os.path.join(
                    match["syno_folder"], file_name), match["user_folder"], file_name)
                print("Copied " + match["syno_folder"] + "\\" +
                      file_name + " -> " + match["user_folder"])
    shutil.rmtree(dir_temp, onerror=del_rw)
    print("Done\n")

    if (len(folders_match) > 0):
        result["code"] = 1
        result["message"] = "Done"
        return result
    else:
        result["code"] = -1
        result["message"] = "Error"
        return result


if __name__ == "__main__":
    update_cert()
