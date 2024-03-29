"""
SMMO Player Checker
Author:      HugTed
Date:        05/1/2022
Version:     0.10.1
"""

import configparser
import json
import random
import sys
import threading
import time
import webbrowser
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import requests
from websocket import create_connection
from PIL import ImageTk, Image
from discord_webhook import DiscordWebhook
import keyboard

TARGET_LIST = []
TARGET_INDEX = 0
with open("./data/banned.txt", "r") as f:
    BANNED_LIST = json.load(f)
with open("./data/temp.txt", "r") as f:
    TEMP_LIST = json.load(f)


def newPlayer():
    global TARGET_LIST, TARGET_INDEX, TEMP_LIST
    TARGET_INDEX += 1
    if len(TARGET_LIST) != TARGET_INDEX:
        if TEMP_LIST.count(TARGET_LIST[TARGET_INDEX]) == 3:
            TARGET_INDEX += 1
        TEMP_LIST.append(TARGET_LIST[TARGET_INDEX])
        openYomu(TARGET_LIST[TARGET_INDEX])
    if TARGET_INDEX % 10 == 0:
        with open("./data/temp.txt", "w") as f:
            json.dump(TEMP_LIST, f)


def banPlayer():
    global TARGET_LIST, TARGET_INDEX, BANNED_LIST
    BANNED_LIST.append(TARGET_LIST[TARGET_INDEX])
    with open("./data/banned.txt", "w") as f:
        json.dump(BANNED_LIST, f)
    newPlayer()


def checkBan(user):
    global BANNED_LIST
    if int(user) in BANNED_LIST:
        return "X"
    else:
        return "O"


def clearTemp():
    global TEMP_LIST
    TEMP_LIST = []
    with open("./data/temp.txt", "w") as f:
        json.dump(TEMP_LIST, f)


def checkTemp(user):
    global TEMP_LIST
    return TEMP_LIST.count(int(user))


def openYomu(data):
    ws = create_connection("ws://localhost:8069")
    msg = {"type": "openLink", "url": f"https://simple-mmo.com/user/attack/{data}?new_page=true"}
    ws.send(json.dumps(msg, separators=(',', ':')))
    result = ws.recv()
    ws.close()
    if result == "success":
        return True
    else:
        return False


class MyWindow:
    def __init__(self, win):
        self.back = None
        self.searching = True
        self.s = ttk.Style()
        self.s.theme_use('default')
        self.s.configure("blue.Horizontal.TProgressbar", foreground='cornflower blue', background='cornflower blue')
        self.s.configure('W.TButton', font=('calibri', 10, 'bold', 'underline'))

        self.frame = Frame(win)
        self.frame.place(x=25, y=75)

        self.listNodes = Listbox(self.frame, width=31, height=15, font=("Helvetica", 12))
        self.listNodes.pack(side="left", fill="y")

        self.scrollbar = Scrollbar(self.frame, orient="vertical")
        self.scrollbar.config(command=self.listNodes.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.listNodes.config(yscrollcommand=self.scrollbar.set)
        self.listNodes.insert(END, "All Players")
        self.listNodes.insert(END, "Guild Wars")

        self.searching = False
        self.lbl1 = Label(win, text='Add ID:')
        self.t1 = Entry(bd=3, width=27)
        self.btn1 = Button(win, text='Add')
        self.lbl1.place(x=25, y=25)
        self.t1.place(x=75, y=25)
        self.b1 = Button(win, text='Add', command=self.addGuild)
        self.b1.place(x=260, y=23)

        self.lbl7 = Label(win, text='Guilds:')
        self.lbl7.place(x=25, y=50)

        self.lbl2 = Label(win, text='Options:')
        self.lbl2.place(x=375, y=25)

        self.lbl3 = Label(win, text='Max Level:')
        self.lbl3.place(x=375, y=50)
        self.t2 = Entry(bd=3, width=30)
        self.t2.place(x=450, y=50)

        self.lbl4 = Label(win, text='Min Level:')
        self.lbl4.place(x=375, y=75)
        self.t3 = Entry(bd=3, width=30)
        self.t3.place(x=450, y=75)

        self.lbl5 = Label(win, text='Min Gold:')
        self.lbl5.place(x=375, y=100)
        self.t4 = Entry(bd=3, width=30)
        self.t4.place(x=450, y=100)

        self.safe_mode = IntVar()
        self.is_dead = IntVar()
        self.verbose = IntVar()
        self.box1 = Checkbutton(text="Remove Safe Mode", variable=self.safe_mode)
        self.box1.place(x=450, y=125)
        self.box2 = Checkbutton(text="Remove Dead", variable=self.is_dead)
        self.box2.place(x=450, y=150)
        self.box2 = Checkbutton(text="Verbose", variable=self.verbose)
        self.box2.place(x=450, y=175)
        self.b3 = ttk.Button(win, style='W.TButton', text='SEARCH', width=37,
                             command=lambda: self.start_submit_thread(None, win))
        self.b3.place(x=375, y=210)

        self.img = ImageTk.PhotoImage(Image.open(f'./images/smmo.png'))
        self.image = Label(win, image=self.img, height=140, width=140)
        self.image.place(x=440, y=245)

        self.lbl6 = Label(win, text='Output:')
        self.lbl6.place(x=25, y=375)
        self.b2 = Button(win, width=5, text='Clear', relief='groove', command=self.clearOutput)
        self.b2.place(x=75, y=372)
        self.b4 = Button(win, width=5, text='Save', relief='groove', command=self.save)
        self.b4.place(x=118, y=372)
        self.b5 = Button(win, width=5, text='Hook', relief='groove', state=DISABLED, command=self.sendHook)
        self.b5.place(x=161, y=372)
        self.b6 = Button(win, width=5, text='Web', relief='groove', state=DISABLED, command=self.openWeb)
        self.b6.place(x=204, y=372)
        self.b8 = Button(win, width=5, text='Y0mu', relief='groove', state=DISABLED, command=self.openYomu)
        self.b8.place(x=244, y=372)
        self.b9 = Button(win, width=6, text='Clear 3x', relief='groove', state=NORMAL, command=clearTemp)
        self.b9.place(x=285, y=372)
        self.img_on = ImageTk.PhotoImage(Image.open(f'./images/on.png'))
        self.img_off = ImageTk.PhotoImage(Image.open(f'./images/off.png'))
        self.web_check = BooleanVar()
        self.web_check.set(False)
        self.b7 = Button(win, borderwidth=0, image=self.img_off, command=self.switch, relief=SUNKEN)
        self.b7.place(x=340, y=370)
        self.out1 = ScrolledText(win, height=20)
        self.out1.place(x=25, y=400)

        self.progressbar = ttk.Progressbar(win, style="blue.Horizontal.TProgressbar", length=658, mode='indeterminate')
        self.progressbar.place(x=25, y=725)

        self.result_list = {}
        self.result_index = 0

        with open(f'./data/guildlist.txt', 'r') as f:
            guildlist = json.load(f)
        for item in guildlist.values():
            self.listNodes.insert(END, item)

        if api_key == "SMMO API KEY" and web_hook == "DISCORD WEB HOOK" and own_guild == -1:
            self.out1.insert(END, "Please make sure you have configured your `config.ini` correctly, if this is your first launch please reference the example in README.\n")
        else:
            if api_key == "SMMO API KEY":
                self.out1.insert(END, "Please make sure you have a valid SMMO API KEY in `config.ini`\n")
            if web_hook == "DISCORD WEB HOOK":
                self.out1.insert(END, "Please make sure you have a valid WEBHOOK in `config.ini`\n")
            if own_guild == -1:
                self.out1.insert(END, "Please make sure you have a valid GuildID in `config.ini`\n")

    def addGuild(self):
        id = str(self.t1.get())
        with open(f'./data/guildlist.txt', 'r') as f:
            guildlist = json.load(f)
        endpoint = f'https://api.simple-mmo.com/v1/guilds/info/{id}'
        payload = {'API_KEY': api_key}
        try:
            r = requests.post(url=endpoint, data=payload)
            lib = r.json()
            guildlist[f'{id}'] = lib["name"]
            with open(f'./data/guildlist.txt', 'w') as f:
                json.dump(guildlist, f)
            self.listNodes.insert(END, lib["name"])
        except:
            self.out1.delete('1.0', END)
            self.out1.insert(END, "ERROR - GUILD ID ONLY")

    def switch(self):
        if self.web_check.get():
            self.b7.config(image=self.img_off)
            self.web_check.set(False)
            self.b6.config(state=DISABLED)
            self.b5.config(state=DISABLED)
            self.b8.config(state=DISABLED)
        else:
            self.b7.config(image=self.img_on)
            self.web_check.set(True)
            self.b6.config(state=NORMAL)
            self.b5.config(state=NORMAL)
            self.b8.config(state=NORMAL)

    def sendHook(self):
        if len(self.result_list) > 0:
            cur_inp = self.out1.get("1.0", END)
            if len(cur_inp) >= 1900:
                index = 0
                output = "**SMMO Player Checker - Results**\n"
                search_terms = cur_inp.split("--------------")[0]
                results = cur_inp.split("--------------")[1].split("\n\n")
                output += search_terms
                while index < len(results):
                    if len(output) <= 1500:
                        output += f'{results[index]}\n'
                        index += 1
                    else:
                        webhook = DiscordWebhook(url=web_hook, content=output)
                        webhook.execute()
                        time.sleep(3)
                        output = f'{results[index]}\n'
                        index += 1
            else:
                output = "**SMMO Player Checker - Results**\n" + cur_inp
            webhook = DiscordWebhook(url=web_hook, content=output)
            webhook.execute()
        else:
            self.out1.insert(END, "No cached search results.\n")

    def openWeb(self):
        if len(self.result_list) > 0:
            root = Tk()
            root.title(f'SMMO Web Utility')
            root.iconbitmap(rf'./images/smmo.ico')
            root.geometry("250x100")

            options = list(self.result_list.keys())
            self.root_sel = StringVar(root)
            self.root_sel.set(options[0])
            w = OptionMenu(root, self.root_sel, *options)
            w.config(width=25)
            w.place(x=25, y=10)

            self.back = Button(root, width=5, text='<<', relief='groove', command=self.root_back)
            self.back.place(x=65, y=45)

            self.go = Button(root, width=5, text='GO', relief='groove', command=self.root_go)
            self.go.place(x=105, y=45)

            self.forward = Button(root, width=5, text='>>', relief='groove', command=self.root_forward)
            self.forward.place(x=145, y=45)

            self.check_state()

            webbrowser.open(f'https://web.simple-mmo.com/user/attack/{self.result_list[options[0]]}', autoraise=True)
        else:
            self.out1.insert(END, "No cached search results.\n")

    def openYomu(self):
        if len(self.result_list) > 0:
            if not openYomu(TARGET_LIST[0]):
                self.out1.insert(END, "Unable to open Y0mu's Client, please have mobile sim open.\n")
                return

            root = Tk()
            root.title(f'SMMO Yomu Utility')
            root.iconbitmap(rf'./images/smmo.ico')
            root.geometry("600x400")

            table_frame = Frame(root)
            table_frame.pack()

            table_scroll = Scrollbar(table_frame)
            table_scroll.pack(side=RIGHT, fill=Y)

            self.my_table = ttk.Treeview(table_frame, yscrollcommand=table_scroll.set)
            self.my_table.pack()

            table_scroll.config(command=self.my_table.yview)

            self.my_table['columns'] = ('player_id', 'player_name', 'player_banned', 'player_temp')

            self.my_table.column("#0", width=0, stretch=NO)
            self.my_table.column("player_id", anchor=CENTER, width=60)
            self.my_table.column("player_name", anchor=CENTER, width=80)
            self.my_table.column("player_banned", anchor=CENTER, width=10)
            self.my_table.column("player_temp", anchor=CENTER, width=10)

            self.updateTable()
        else:
            self.out1.insert(END, "No cached search results.\n")


    def updateTable(self):
        for user in self.result_list:
            self.my_table.insert(parent='', index='end',iid=list(self.result_list.keys()).index(user), text='', values=(f'{user}', f'{self.result_list[user]}', checkBan(user), checkTemp(user)))
            self.my_table.pack()

    def check_state(self):
        if self.result_index == 0 and self.result_index == len(self.result_list) - 1:
            self.back.config(state=DISABLED)
            self.forward.config(state=DISABLED)
        elif self.result_index == 0:
            self.back.config(state=DISABLED)
        elif self.result_index == len(self.result_list) - 1:
            self.forward.config(state=DISABLED)
        else:
            self.forward.config(state=NORMAL)
            self.back.config(state=NORMAL)

    def root_back(self):
        local_results = list(self.result_list.keys())
        self.result_index -= 1
        self.root_sel.set(local_results[self.result_index])
        webbrowser.open(f'https://web.simple-mmo.com/user/attack/{self.result_list[local_results[self.result_index]]}',
                        new=0)
        self.check_state()

    def root_go(self):
        local_results = list(self.result_list.keys())
        self.result_index = local_results.index(self.root_sel.get())
        webbrowser.open(f'https://web.simple-mmo.com/user/attack/{self.result_list[local_results[self.result_index]]}',
                        new=0)
        self.check_state()

    def root_forward(self):
        local_results = list(self.result_list.keys())
        self.result_index += 1
        self.root_sel.set(local_results[self.result_index])
        webbrowser.open(f'https://web.simple-mmo.com/user/attack/{self.result_list[local_results[self.result_index]]}',
                        new=0)
        self.check_state()

    def save(self):
        cur_inp = self.out1.get("1.0", END)
        fl = open("./data/output.txt", "w")
        fl.write(cur_inp)

    def clearOutput(self):
        self.out1.delete('1.0', END)
        self.searching = False
        self.result_list = {}

    def search(self):
        while self.searching:
            guild_name = str((self.listNodes.get(ACTIVE)))
            guild_id = 0
            self.out1.delete('1.0', END)
            if guild_name == "":
                self.out1.insert(END, "ERROR")
                return
            if guild_name == "All Players":
                users = random.sample(range(100, 500000), 20000)
            elif guild_name == "Guild Wars":
                guilds = []
                endpoint = f'https://api.simple-mmo.com/v1/guilds/wars/{own_guild}/1'
                payload = {'API_KEY': api_key}
                r = requests.post(url=endpoint, data=payload)
                lib = r.json()
                for war in lib:
                    if war["guild_1"]["id"] != own_guild:
                        guilds.append(war["guild_1"]["id"])
                    else:
                        guilds.append(war["guild_2"]["id"])
            else:
                with open(f'./data/guildlist.txt', 'r') as f:
                    guildlist = json.load(f)
                for id, name in guildlist.items():
                    if name == guild_name:
                        guild_id = id
                if guild_id == 0:
                    self.out1.insert(END, "ERROR")
                    return
                self.out1.insert(END, f'Found Guild - {guild_id}\n')
                users = []
                endpoint = f'https://api.simple-mmo.com/v1/guilds/members/{guild_id}'
                payload = {'API_KEY': api_key}
                r = requests.post(url=endpoint, data=payload)
                lib = r.json()
                for user in lib:
                    users.append(user["user_id"])
                with open(f'./data/{guild_id}.txt', 'w') as f:
                    json.dump(users, f)
                self.out1.insert(END, f'Found Members - {len(users)}\n')
            try:
                max_level = int(self.t2.get())
            except:
                max_level = 1000000
            try:
                min_level = int(self.t3.get())
            except:
                min_level = 0
            try:
                min_gold = int(self.t4.get())
            except:
                min_gold = 0
            search_term = f'Search Params:\nMax Level: {max_level}\nMin Level: {min_level}\nMin Gold: {min_gold}\n'
            if self.safe_mode.get() == 1:
                search_term += "Safe Mode Players Removed\n"
            if self.is_dead.get() == 1:
                search_term += "Dead Players Removed\n"
            if self.verbose.get() == 1:
                search_term += "Verbose On\n"
            if min_gold != 0:
                search_term += "Gold Searching - Limits searches to API limits, remove gold requirement for quicker search\n"
            search_term += "--------------\n"
            self.out1.insert(END, search_term)
            if guild_name == "Guild Wars":
                self.searchUsers(guilds, max_level, min_level, min_gold, 1)
            elif min_gold == 0:
                self.searchUsers(lib, max_level, min_level, min_gold)
            else:
                self.searchUsers(users, max_level, min_level, min_gold)
            self.out1.insert(END, "Complete!\n")
            self.searching = False

    def printUser(self, lib, option=0):
        if self.verbose.get() == 0 and option == 0:
            self.out1.insert(END, f'[{lib["name"]}](<https://web.simple-mmo.com/user/attack/{lib["id"]}>)\n')
        elif self.verbose.get() == 0 and option == 1:
            self.out1.insert(END, f'[{lib["name"]}](<https://web.simple-mmo.com/user/attack/{lib["user_id"]}>)\n')
        elif option == 1:
            self.out1.insert(END,
                             f'Name: {lib["name"]}\nLevel: {lib["level"]}\nHP: {lib["current_hp"]}/{lib["max_hp"]}\n[Attack Link](<https://web.simple-mmo.com/user/attack/{lib["user_id"]}>)\n\n')
        else:
            self.out1.insert(END,
                             f'Name: {lib["name"]}\nLevel: {lib["level"]}\nHP: {lib["hp"]}/{lib["max_hp"]}\nGold: {lib["gold"]}\n[Attack Link](<https://web.simple-mmo.com/user/attack/{lib["id"]}>)\n\n')

    def start_submit_thread(self, event, win):
        global submit_thread
        submit_thread = threading.Thread(target=self.search)
        self.searching = True
        self.result_list = {}
        submit_thread.daemon = True
        submit_thread.start()
        self.progressbar.start()
        win.after(1000, self.check_submit_thread(win))

    def check_submit_thread(self, win):
        if submit_thread.is_alive():
            win.after(1000, lambda: self.check_submit_thread(win))
        else:
            self.progressbar.stop()

    def searchUsers(self, users, max_level, min_level, min_gold, gw=0):
        index = 0
        error_index = 0
        kill_timestamp = (datetime.now() - timedelta(hours=48)).timestamp()
        if gw == 1:
            if min_gold != 0:
                self.out1.insert(END, "Gold filtering not enabled in Guild Wars mode.\n")
            for guild in users:
                if not self.searching:
                    return
                try:
                    endpoint = f"https://api.simple-mmo.com/v1/guilds/members/{guild}"
                    payload = {'API_KEY': api_key}
                    r = requests.post(url=endpoint, data=payload)
                    lib = r.json()
                    if r.status_code != "200":
                        self.out1.insert(END, f'API Error, please check your key and try again later!\n')
                        return
                except:
                    self.out1.insert(END, f'Error Locating Guild: {guild}')
                    time.sleep(2)
                    continue
                for user in lib:
                    if user["safe_mode"] == 0 and user["current_hp"] * 2 >= user["max_hp"]:
                        if user["level"] > 200 or (user["last_activity"] < kill_timestamp and user["level"] <= 200):
                            if min_level <= user["level"] <= max_level:
                                self.printUser(user, 1)
                                self.result_list[user["name"]] = user["user_id"]
                                TARGET_LIST.append(user["user_id"])
                time.sleep(2)
        elif min_gold == 0:
            for user in users:
                if not self.searching:
                    return
                if min_level <= user["level"] <= max_level:
                    if self.safe_mode.get() == 1 and self.is_dead.get() == 1:
                        if user["safe_mode"] == 0 and int(user["current_hp"] * 2) > user["max_hp"]:
                            self.printUser(user, 1)
                            self.result_list[user["name"]] = user["user_id"]
                            TARGET_LIST.append(user["user_id"])
                    elif self.is_dead.get() == 1:
                        if int(user["current_hp"] * 2) > user["max_hp"]:
                            self.printUser(user, 1)
                            self.result_list[user["name"]] = user["user_id"]
                            TARGET_LIST.append(user["user_id"])
                    elif self.safe_mode.get() == 1:
                        if user["safe_mode"] == 0:
                            self.printUser(user, 1)
                            self.result_list[user["name"]] = user["user_id"]
                            TARGET_LIST.append(user["user_id"])
                    else:
                        self.printUser(user)
                        self.result_list[user["name"]] = user["user_id"]
                        TARGET_LIST.append(user["user_id"])
        else:
            for userid in users:
                if not self.searching:
                    return
                try:
                    endpoint = "https://api.simple-mmo.com/v1/player/info/" + f'{userid}'
                    payload = {'API_KEY': api_key}
                    r = requests.post(url=endpoint, data=payload)
                    lib = r.json()
                    if "error" not in lib.keys():
                        index += 1
                        if lib["level"] >= min_level and lib["level"] <= max_level and lib["gold"] >= min_gold:
                            if self.safe_mode.get() == 1 and self.is_dead.get() == 1:
                                if lib["safeMode"] == 0 and int(lib["hp"] * 2) > lib["max_hp"]:
                                    self.printUser(lib)
                                    self.result_list[lib["name"]] = lib["id"]
                                    TARGET_LIST.append(lib["id"])
                            elif self.is_dead.get() == 1:
                                if int(lib["hp"] * 2) > lib["max_hp"]:
                                    self.printUser(lib)
                                    self.result_list[lib["name"]] = lib["id"]
                                    TARGET_LIST.append(lib["id"])
                            elif self.safe_mode.get() == 1:
                                if lib["safeMode"] == 0:
                                    self.printUser(lib)
                                    self.result_list[lib["name"]] = lib["id"]
                                    TARGET_LIST.append(lib["id"])
                            else:
                                self.printUser(lib)
                                self.result_list[lib["name"]] = lib["id"]
                                TARGET_LIST.append(lib["id"])

                except Exception as e:
                    print(e)
                    error_index += 1
                    if error_index == 10:
                        self.out1.insert(END, f'You might be rate limited, please try again later!')
                time.sleep(2)


if __name__ == "__main__":
    sys.setrecursionlimit(5000)
    config = configparser.ConfigParser()
    config.read(f'./config.ini')
    api_key = config.get('DEFAULT', 'API_KEY')
    web_hook = config.get('DEFAULT', 'web_hook')
    own_guild = int(config.get('DEFAULT', 'own_guild'))
    key1 = config.get('DEFAULT', 'hotkey1')
    key2 = config.get('DEFAULT', 'hotkey2')
    version = config.get('DEFAULT', 'version_number')

    window = Tk()
    mywin = MyWindow(window)
    window.title(f'SMMO Player Checker v{version}')
    window.iconbitmap(rf'./images/smmo.ico')
    window.geometry("700x750")
    keyboard.add_hotkey(key1, newPlayer)
    keyboard.add_hotkey(key2, banPlayer)
    window.mainloop()
