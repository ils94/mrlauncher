import requests
from bs4 import BeautifulSoup
from tkinter import Tk, Button, Text, messagebox, ttk, Frame, Label, X, E, W, END, CURRENT, BOTH
from tkinter.font import Font
import threading
from socket import socket, AF_INET, SOCK_STREAM
import os
import time
from os import system
import webbrowser
from functools import partial
import os.path


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
    t = threading.Thread(target=function)
    t.setDaemon(True)
    t.start()


def error_message(msg):
    label_checking["text"] = "Something went wrong! Please try again."
    start_button["state"] = "normal"
    messagebox.showerror("Error", msg)


def repair_game():
    value = messagebox.askyesno("Repair Game",
                                "This will re-download the game to fix file corruption. Do you wish to continue?")

    if value:
        label_checking["text"] = "Re-downloading the game, please wait..."
        start_button["state"] = "disabled"
        download_game()


def check_java():
    check = system("java -version") == 0
    if not check:
        value = messagebox.askokcancel("Install Java",
                                       "No Java installation detected in your system.\n\nYou need Java installed to be able to play Mirage Realms.\n\nPress ''Ok'' to open Java download webpage.")
        if value:
            webbrowser.open("https://www.java.com/en/download/manual.jsp")


def ping_server():
    while True:
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
            print(str(e))
            server_status["text"] = "Error pinging the server."

        time.sleep(30)


def bs4soup(link):
    try:
        referer = "https://www.google.com/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/108.0.0.0 Safari/537.36", "referer": referer}

        return BeautifulSoup(requests.get(link, headers=headers).text, 'html.parser')
    except Exception as e:
        error_message(e)


def get_releases():
    try:
        soup = bs4soup("https://www.miragerealms.co.uk/devblog/category/releases/")

        releases = soup.findAll('article')

        releases_article = str(releases[0].text).replace("Read More", "").lstrip().rstrip()

        releases_link = find_links(soup, "-released/")

        return releases_article, releases_link
    except Exception as e:
        return str(e)


def get_hotfixes():
    try:
        soup = bs4soup("https://www.miragerealms.co.uk/devblog/category/hotfixes/")

        hotfixes = soup.findAll('article')

        hotfix_article = str(hotfixes[0].text).replace("Read More", "").lstrip().rstrip()

        hotfix_link = find_links(soup, "/hotfixes/")

        return hotfix_article, hotfix_link
    except Exception as e:
        return str(e)


def find_links(soup, string):
    links1 = []
    links2 = []

    for a in soup.find_all('a', href=True):
        if a.text:
            links1.append(a['href'])

    for link in links1:
        if string in link:
            links2.append(link)

    if len(links2) != 0:
        return links2[0]
    else:
        return "No link :("


def start_game():
    start_button["state"] = "disabled"

    if os.path.isfile("mr.jar"):
        question = messagebox.askyesnocancel("Download new version",
                                             "There might be a new version of the game, do you want to download it?")

        question = str(question)

        if question == "True":
            label_checking["text"] = "Downloading new update, please wait..."
            download_game()
        elif question == "False":
            open_game_client()
        else:
            start_button["state"] = "normal"
    else:
        label_checking["text"] = "Downloading the game, please wait..."
        download_game()


def open_game_client():
    label_checking["text"] = "The game is launching!"
    os.startfile("mr.jar")
    time.sleep(3)
    os._exit(0)


def download_game():
    try:
        download_link = "https://files.miragerealms.co.uk/mirage/clients/live/Mirage.jar"

        start_button["state"] = "disabled"
        file_name = "mr.jar"

        with open(file_name, "wb") as f:
            response = requests.get(download_link, stream=True, verify=False)
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
        open_game_client()
    except Exception as e:
        start_button["state"] = "normal"
        pb["value"] = 0
        label_checking["text"] = "Error downloading the game."
        error_message(e)


def load_news():
    hyperlink = HyperlinkManager(text_news)

    releases = get_releases()
    hotfixes = get_hotfixes()

    text_news["state"] = "normal"

    text_news.delete("1.0", END)

    text_news.insert("1.0", "LASTEST RELEASE VERSION:\n\n")
    text_news.insert(END, releases[0])
    text_news.insert(END, "\n\n" + releases[1], hyperlink.add(partial(webbrowser.open, releases[1])))

    text_news.insert(END, "\n\n------------------------------------------------------------")
    text_news.insert(END, "\n\nLASTEST HOTFIXES:\n\n")
    text_news.insert(END, hotfixes[0])
    text_news.insert(END, "\n\n" + hotfixes[1], hyperlink.add(partial(webbrowser.open, hotfixes[1])))

    text_news["state"] = "disabled"


root = Tk()

window_width = 500
window_height = 500

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width / 2) - (window_width / 2)
y = (screen_height / 2) - (window_height / 2)

root.geometry("500x500+" + str(int(x)) + "+" + str(int(y)))
root.title("Mirage Realms Launcher")
if os.path.isfile("icon/miragerealms.ico"):
    root.iconbitmap("icon/miragerealms.ico")
root.resizable(False, False)

server_status = Label(root, text="Server status")
server_status.pack(padx=5, anchor=E)

text_news = Text(root, height=25)
text_news.pack(padx=5, fill=BOTH)
text_news.insert("1.0", "LOADING...")
text_news["state"] = "disabled"

label_checking = Label(root, text="", height=1)
label_checking.pack(padx=5, fill=X)

frame = Frame(root)
frame.pack(fill=X, padx=5)

bold_font = Font(weight="bold", size=11)
start_button = Button(frame, text="Play!", width=15, height=2, font=bold_font,
                      command=lambda: multithreading(start_game))
start_button.pack(anchor=E, side="right")

pb = ttk.Progressbar(frame, mode="determinate", length=100)
pb.pack(fill=X, padx=5, anchor=W, side="bottom")

multithreading(load_news)

multithreading(ping_server)

multithreading(check_java)

root.mainloop()
