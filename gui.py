import json
from tkinter import *
from tkinter.filedialog import askopenfilename
import cert2drive


def update():
    is_updated = cert2drive.update_cert()
    if(is_updated == 1):
        print("done")
    else:
        print("error")


def browse_file(context):
    file_name = askopenfilename(
        initialdir="/", title="Select a file", filetype=[('All files', '*.*')])
    if (context == "__private_key__"):
        entry_private_key.delete(0, END)
        entry_private_key.insert(
            END, file_name)
        cert2drive.settings["ssh_config"]["private_key"] = file_name
        print(file_name)
        # with open('config.json', 'w') as configJson:
        #     json.dump(cert2drive.settings, configJson)


# init
window = Tk()

# Menu
menubar = Menu(tearoff=False)
fileMenu = Menu(tearoff=False)
#recentMenu = Menu(tearoff=False)

menubar.add_cascade(label="File", menu=fileMenu)

#fileMenu.add_cascade(label="Open Recent", menu=recentMenu)
fileMenu.add_command(label="Save config")
fileMenu.add_separator()
fileMenu.add_command(label="Exit", command=window.quit)


# Edit window
window.title("Synology cert2drive")
window.geometry("720x480")
window.minsize(480, 272)
# window.iconbitmap("icon.ico")
window.configure(menu=menubar)
window.config(background="#2B2B2B")

# Entry Port
label_post = Label(window, text="Port :", bg="#2B2B2B", fg="white")
label_post.grid(column=0, row=0, ipadx=5, pady=5, sticky=W+N)
entry_post = Entry(window)
entry_post.insert(
    END, cert2drive.settings["synology_config"]["port"])
entry_post.grid(column=1, columnspan=2, row=0, ipadx=5, pady=5, sticky=N)

# Entry Host
label_host = Label(window, text="Host :", bg="#2B2B2B", fg="white")
label_host.grid(column=0, row=1, ipadx=5, pady=5, sticky=W+N)
entry_host = Entry(window)
entry_host.insert(
    END, cert2drive.settings["synology_config"]["host"])
entry_host.grid(column=1, columnspan=2, row=1, ipadx=5, pady=5, sticky=N)


# Entry User name
label_username = Label(window, text="User name :", bg="#2B2B2B", fg="white")
label_username.grid(column=0, row=2, ipadx=5, pady=5, sticky=W+N)
entry_username = Entry(window)
entry_username.insert(
    END, cert2drive.settings["synology_config"]["username"])
entry_username.grid(column=1, columnspan=2, row=2, ipadx=5, pady=5, sticky=N)

# Browse private key
label_private_key = Label(window, text="Private key :",
                          bg="#2B2B2B", fg="white")
label_private_key.grid(column=0, row=3, ipadx=5, pady=5, sticky=W+N)
entry_private_key = Entry(window)
entry_private_key.insert(
    END, cert2drive.settings["ssh_config"]["private_key"])
entry_private_key.grid(column=1, columnspan=2, row=3,
                       ipadx=5, pady=5, sticky=N)
private_key_browse_btn = Button(
    window, text="Browse", bg="white", fg="#2B2B2B", relief='flat', highlightthickness=0, bd=0, command=lambda: browse_file("__private_key__"))
private_key_browse_btn.grid(column=3, row=3, padx=10, pady=5, sticky=W+N)

# Buttons
# update_cert_btn = Button(frame, text="Update",
#                          bg="white", fg="#2B2B2B", command=update)
# update_cert_btn.pack(pady=25, fill=X)

# Add frames

# Show
window.mainloop()
