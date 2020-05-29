import json
import collections
from tkinter import *
from tkinter.filedialog import *
from tkinter import messagebox
import cert2drive
import base64
import zlib

c_red = "#E80651"
c_red_light = "#e95779"
c_black = "#2B2B2B"
c_black_light = "#494949"
c_black_lighter = "#606060"

ICON = zlib.decompress(base64.b64decode('eJxjYGAEQgEBBiDJwZDBy'
                                        'sAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc='))


def update_config():
    cert2drive.settings["synology_config"]["host"] = entry_host.get()
    cert2drive.settings["synology_config"]["port"] = int(entry_port.get())
    cert2drive.settings["synology_config"]["username"] = entry_username.get()
    cert2drive.settings["ssh_config"]["private_key"] = entry_private_key.get()
    entry_folders_domains = []
    for entry_folder, entry_domain in zip(entry_folders, entry_domains):
        entry_folder_domain = collections.defaultdict(list)
        entry_folder_domain["domain"] = entry_domains[entry_domain].get()
        entry_folder_domain["folder"] = entry_folders[entry_folder].get()
        entry_folders_domains.append(entry_folder_domain)
    cert2drive.settings["certificates_config"] = entry_folders_domains


def update():
    update_config()
    is_updated = cert2drive.update_cert()
    if(is_updated == 1):
        print("done")
        messagebox.showinfo(
            title="Updated", message="Certificates has been saved")
    else:
        print("error")
        messagebox.showerror(
            title="Updated", message="Error")


def add_cert_entry(user_certificate=False):
    row_position = len(entry_domains) + len(entry_folders) + 4 + 1
    i = len(entry_domains) + 1
    lb = Label(window, text="Domain "+str(i)+" :", bg=c_black, fg="white")
    lb.grid(column=0, row=row_position, ipadx=5, pady=5, sticky=W+N)
    label_domains["domain" + str(i)] = lb

    e = Entry(window)
    e.grid(column=1, row=row_position, ipadx=5, pady=5, sticky=W+E)
    entry_domains["domain" + str(i)] = e
    if(user_certificate):
        entry_domains["domain" + str(i)].insert(
            END, user_certificate["domain"])

    lb = Label(window, text="Folder for Domain " +
               str(i)+" :", bg=c_black, fg="white")
    lb.grid(column=0, row=row_position+1, ipadx=5, pady=5, sticky=W+N)
    label_folders["folder" + str(i)] = lb

    e = Entry(window)
    e.grid(column=1, row=row_position+1, ipadx=5, pady=5, sticky=W+E)
    entry_folders["folder" + str(i)] = e
    if (user_certificate):
        entry_folders["folder" + str(i)].insert(
            END, user_certificate["folder"])

    b = Button(
        window, text="Browse", bg=c_black_light, fg="white", relief="flat", overrelief="flat", activebackground=c_black_lighter, activeforeground="white", highlightthickness=0, bd=0)
    b['command'] = lambda arg=entry_folders["folder" +
                                            str(i)]: browse_folder(arg)
    b.grid(column=4, row=row_position, rowspan=2,
           padx=10, pady=5, sticky=N + E + S + W)
    entry_folders_btn["folderbtn" + str(i)] = b

    remove_entry_domain_btn["removedomainbtn" + str(i)] = Button(
        window, text="Remove", bg=c_red_light, fg="white", activebackground=c_red, activeforeground="white", relief="flat", overrelief="flat", highlightthickness=0, bd=0)
    remove_entry_domain_btn["removedomainbtn" + str(i)]['command'] = lambda arg1=entry_domains["domain" + str(i)], arg2=label_domains["domain" + str(
        i)], arg3=entry_folders["folder" + str(i)], arg4=label_folders["folder" + str(
            i)], arg5=remove_entry_domain_btn["removedomainbtn" + str(i)], arg6=entry_folders_btn["folderbtn" + str(i)]: remove_items(arg1, arg2, arg3, arg4, arg5, arg6)
    remove_entry_domain_btn["removedomainbtn" + str(i)].grid(column=5, row=row_position, rowspan=2,
                                                             padx=(0, 10), pady=5, sticky=N + E + S + W)


def save_config():
    update_config()
    with open('config.json', 'w') as configJson:
        json.dump(cert2drive.settings, configJson)
    print("Config saved")


def remove_items(*args):
    for arg in args:
        for key, value in entry_folders.items():
            if value is arg:
                del entry_folders[key]
                break
        for key, value in entry_domains.items():
            if value is arg:
                del entry_domains[key]
                break
        for key, value in label_folders.items():
            if value is arg:
                del label_folders[key]
                break
        for key, value in label_domains.items():
            if value is arg:
                del label_domains[key]
                break
        for key, value in entry_folders_btn.items():
            if value is arg:
                del entry_folders_btn[key]
                break
        for key, value in remove_entry_domain_btn.items():
            if value is arg:
                del remove_entry_domain_btn[key]
                break
        arg.destroy()
    entry_folders_domains = []
    for entry_folder, entry_domain in zip(entry_folders, entry_domains):
        entry_folder_domain = collections.defaultdict(list)
        entry_folder_domain["domain"] = entry_domains[entry_domain].get()
        entry_folder_domain["folder"] = entry_folders[entry_folder].get()
        entry_folders_domains.append(entry_folder_domain)
        cert2drive.settings["certificates_config"] = entry_folders_domains


def browse_file(context):
    file_name = askopenfilename(
        initialdir="/", title="Select a file", filetype=[('All files', '*.*')])
    if (context == "__private_key__"):
        entry_private_key.delete(0, END)
        entry_private_key.insert(
            END, file_name)


def browse_folder(context):
    folder = askdirectory(
        initialdir="/", title="Select a folder")
    context.delete(0, END)
    context.insert(END, folder)


# init
window = Tk()
window.iconbitmap(default=ICON)

# Menu
menubar = Menu(tearoff=False)
fileMenu = Menu(tearoff=False)
# recentMenu = Menu(tearoff=False)

menubar.add_cascade(label="File", menu=fileMenu)

# fileMenu.add_cascade(label="Open Recent", menu=recentMenu)
fileMenu.add_command(label="Save config", command=save_config)
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=window.quit)


# Edit window
window.title("Synology cert2drive")
window.geometry("480x600")
window.minsize(480, 272)
# window.iconbitmap("icon.ico")
window.configure(menu=menubar)
window.config(background=c_black)

# Entry Host
label_host = Label(window, text="Host :", bg=c_black, fg="white")
label_host.grid(column=0, row=0, ipadx=5, pady=5, sticky=W+N)
entry_host = Entry(window)
entry_host.insert(
    END, cert2drive.settings["synology_config"]["host"])
entry_host.grid(column=1, row=0, ipadx=5, pady=5, sticky=W+E)

# Entry Port
label_port = Label(window, text="Port :", bg=c_black, fg="white")
label_port.grid(column=0, row=1, ipadx=5, pady=5, sticky=W+N)
entry_port = Entry(window)
entry_port.insert(
    END, cert2drive.settings["synology_config"]["port"])
entry_port.grid(column=1, row=1, ipadx=5, pady=5, sticky=W+E)

# Entry User name
label_username = Label(window, text="User name :", bg=c_black, fg="white")
label_username.grid(column=0, row=2, ipadx=5, pady=5, sticky=W+N)
entry_username = Entry(window)
entry_username.insert(
    END, cert2drive.settings["synology_config"]["username"])
entry_username.grid(column=1, row=2, ipadx=5, pady=5, sticky=W+E)

# Browse private key
label_private_key = Label(window, text="Private key :",
                          bg=c_black, fg="white")
label_private_key.grid(column=0, row=3, ipadx=5, pady=5, sticky=W+N)
entry_private_key = Entry(window)
entry_private_key.insert(
    END, cert2drive.settings["ssh_config"]["private_key"])
entry_private_key.grid(column=1, row=3,
                       ipadx=5, pady=5, sticky=W+E)
private_key_browse_btn = Button(
    window, text="Browse", bg=c_black_light, fg="white", relief="flat", overrelief="flat", activebackground=c_black_lighter, activeforeground="white", highlightthickness=0, bd=0, command=lambda: browse_file("__private_key__"))
private_key_browse_btn.grid(
    column=4, row=3, columnspan=2, padx=10, pady=5, sticky=N + E + S + W)

# Entry Certificates Options
entry_domains = {}
label_domains = {}
remove_entry_domain_btn = {}
entry_folders = {}
label_folders = {}
entry_folders_btn = {}
for user_certificate in cert2drive.settings['certificates_config']:
    add_cert_entry(user_certificate)

# Add entry cert button
add_cert_btn = Button(window, text="Add",
                      bg=c_black_light, fg="white", relief="flat", overrelief="flat", activebackground=c_black_lighter, activeforeground="white", highlightthickness=0, bd=0, command=add_cert_entry)
add_cert_btn.grid(column=1, columnspan=1, row=98, rowspan=1,
                  padx=0, pady=5, sticky=W+E+S+N)
window.grid_columnconfigure(1, weight=1)

# Update cert button
update_cert_btn = Button(window, text="Update",
                         bg=c_black_light, fg="white", relief="flat", overrelief="flat", activebackground=c_black_lighter, activeforeground="white", highlightthickness=0, bd=0, command=update)
update_cert_btn.grid(column=1, columnspan=1, row=99, rowspan=1,
                     padx=0, pady=5, sticky=W+E+S+N)
window.grid_columnconfigure(1, weight=1)

# Add frames

# Show
window.mainloop()
