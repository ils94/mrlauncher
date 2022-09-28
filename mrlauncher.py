import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Progressbar
import threading
from socket import *
import os
import time
from os import system
import webbrowser
from functools import partial
import os.path

releases_article = ""
releases_link = ""
hotfix_article = ""
hotfix_link = ""
version = ""
is_update_to_date = False
download_link = ""


class HyperlinkManager:
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return


def multithreading(function):
    try:
        threading.Thread(target=function).start()
    except Exception as e:
        errorMessage(e)


def errorMessage(msg):
    label_checking["text"] = "Something went wrong! Please try again."
    start_button["state"] = "normal"
    messagebox.showerror("Error", msg)


def repairGame():
    value = messagebox.askyesno("Repair Game",
                                "This will re-download the game to fix file corruption. Do you wish to continue?")

    if value:
        label_checking["text"] = "Re-downloading the game, please wait..."
        threading.Thread(target=downloadGame).start()


def checkJava():
    check = system("java -version") == 0
    if not check:
        value = messagebox.askokcancel("Install Java",
                                       "No Java installation detected in your system.\n\nYou need Java installed to be able to play Mirage Realms.\n\nPress ''Ok'' to open Java download webpage.")
        if value:
            webbrowser.open("https://www.java.com/en/download/manual.jsp")


def pingServer():
    try:
        server_status["text"] = "Checking server status..."
        server_status["fg"] = "black"

        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(3.0)

        connection = sock.connect_ex(("159.253.56.69", 1337))

        if connection == 0:
            server_status["text"] = "Server ON"
            server_status["fg"] = "green"
        else:
            server_status["fg"] = "red"
            server_status["text"] = "Server OFF"
    except Exception as e:
        errorMessage(e)


def bs4Soup(link):
    try:
        return BeautifulSoup(requests.get(link).text, 'html.parser')
    except Exception as e:
        errorMessage(e)


def gatherInfos():
    try:
        global releases_article
        global releases_link
        global hotfix_article
        global hotfix_link
        global version
        global download_link

        start_button["state"] = "disabled"

        soup = bs4Soup("https://www.miragerealms.co.uk/devblog/category/releases/")

        releases = soup.findAll('article')

        releases_article = str(releases[0].text).replace("Read More", "").lstrip().rstrip()

        releases_link = findLinks(soup, "/releases/version")

        soup = bs4Soup("https://www.miragerealms.co.uk/devblog/category/hotfixes/")

        hotfixes = soup.findAll('article')

        hotfix_article = str(hotfixes[0].text).replace("Read More", "").lstrip().rstrip()

        hotfix_link = findLinks(soup, "/hotfixes/")

        soup = bs4Soup("https://www.miragerealms.co.uk/devblog/play/")

        site_version = soup.find_all('h4', attrs={'elementor-heading-title elementor-size-default'})

        version = site_version[0].text

        download_link = findLinks(soup, ".jar")

        loadNews()
        checkVersion()
        start_button["state"] = "normal"

    except Exception as e:
        errorMessage(e)


def findLinks(soup, string):
    try:
        links1 = []
        links2 = []

        for a in soup.find_all('a', href=True):
            if a.text:
                links1.append(a['href'])

        for link in links1:
            if string in link:
                links2.append(link)

        return links2[0]
    except Exception as e:
        errorMessage(e)


def startGame():
    try:
        if os.path.isfile("mr.jar") and os.path.isfile("version.txt"):
            if is_update_to_date:
                start_button["state"] = "disabled"
                label_checking["text"] = "The game is launching!"
                os.startfile("mr.jar")
                time.sleep(3)
                os._exit(0)
            else:
                label_checking["text"] = "Downloading new update, please wait..."
                downloadGame()
        else:
            label_checking["text"] = "Downloading the game, please wait..."
            downloadGame()
    except Exception as e:
        errorMessage(e)


def startGameThread():
    try:
        threading.Thread(target=startGame).start()
    except Exception as e:
        errorMessage(e)


def downloadGame():
    try:
        global download_link

        start_button["state"] = "disabled"

        saveVersion(version)

        file_name = "mr.jar"
        with open(file_name, "wb") as f:
            response = requests.get(download_link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    pb["value"] = done * 2

        pb["value"] = 0
        label_checking["text"] = "Download complete! Game is now launching!"
        os.startfile(file_name)
        time.sleep(3)
        os._exit(0)
    except Exception as e:
        errorMessage(e)


def saveVersion(ver):
    try:
        file = open("version.txt", "w")
        file.write(ver)
        file.close()
    except Exception as e:
        errorMessage(e)


def loadVersion():
    try:
        file = open("version.txt")
        ver = file.read()
        file.close()
        return ver
    except Exception as e:
        saveVersion("None")
        print(e)


def checkVersion():
    try:
        global is_update_to_date
        if os.path.isfile("version.txt"):
            if loadVersion() == version:
                label_checking["text"] = "The client is up to date!"
                is_update_to_date = True
            else:
                label_checking["text"] = "There is a new update available!"
        else:
            label_checking["text"] = "The game is ready to be downloaded!"
    except Exception as e:
        errorMessage(e)


def loadNews():
    try:
        text_news["state"] = "normal"
        global releases_article
        global releases_link
        global hotfix_article
        global hotfix_link

        hyperlink = HyperlinkManager(text_news)

        text_news.delete("1.0", END)

        text_news.insert("1.0", "LASTEST RELEASE VERSION:\n\n")
        text_news.insert(END, releases_article)
        text_news.insert(END, "\n\n" + releases_link, hyperlink.add(partial(webbrowser.open, releases_link)))

        text_news.insert(END, "\n\n------------------------------------------------------------")
        text_news.insert(END, "\n\nLASTEST HOTFIXES:\n\n")
        text_news.insert(END, hotfix_article)
        text_news.insert(END, "\n\n" + hotfix_link, hyperlink.add(partial(webbrowser.open, hotfix_link)))

        text_news["state"] = "disabled"
    except Exception as e:
        errorMessage(e)


root = Tk()

window_width = 500
window_height = 500

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width / 2) - (window_width / 2)
y = (screen_height / 2) - (window_height / 2)

root.geometry("500x500+" + str(int(x)) + "+" + str(int(y)))
root.title("Mirage Realms Launcher")
root.iconbitmap("icon/miragerealms.ico")
root.resizable(False, False)

menu_bar = Menu(root)

menu = Menu(menu_bar, tearoff=0)

menu.add_command(label="Repair...", command=lambda: multithreading(repairGame))
menu.add_command(label="Update server status...", command=lambda: multithreading(pingServer))
menu.add_command(label="Reload launcher...", command=lambda: multithreading(gatherInfos))

menu_bar.add_cascade(label="Menu", menu=menu)

root.config(menu=menu_bar)

server_status = Label(root, text="Server status")
server_status.pack(padx=5, anchor=E)

text_news = Text(root)
text_news.pack(padx=5, fill=X)
text_news["state"] = "disabled"

label_checking = Label(root, text="Loading...", width=30, height=1)
label_checking.pack(padx=5, fill=X)

frame = Frame(root)
frame.pack(fill=X, padx=5)

start_button = Button(frame, text="Play!", width=15, height=2, command=lambda: multithreading(startGame))
start_button.pack(anchor=E, side="right")

pb = Progressbar(frame, mode="determinate", length=100)
pb.pack(fill=X, padx=5, anchor=W, side="bottom")

multithreading(gatherInfos)

multithreading(pingServer)

multithreading(checkJava)

root.mainloop()
