# coding=utf-8
# main.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/09
# description: candidate client main: ui+main_logic

from tkinter import *
from tkinter import ttk

from user_manager import OISClientUserManager


class OISCandidateClient:
    """OIS Candidate Client Main Class: ui windows and main logic"""
    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.user_manager = ba.user_manager

        self.main_window = Tk(className="(*^▽^*) OIS")
        self.main_window.title("OIS CC")
        self.main_window.maxsize(300, 600)
        
        self.login_frame_set = {}
        self.main_frame_set = {}

    def start(self):

        """
        run app(open the window)
        :return:
        """
        self.log.add_log("OISCandidateClient: start the OIS Candidate Client now", 1)

        self.log.add_log("OISCandidateClient: load login frame...", 1)
        # load login frame
        self.login_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.login_frame_set["frame"].grid()

        self.login_frame_set["title"] = ttk.Label(self.login_frame_set["frame"], text="OIS面试者端 登录界面", anchor=CENTER, background="lightblue")
        self.login_frame_set["title"].grid(column=1, row=1)

        self.login_frame_set["notice_textvar"] = StringVar()
        self.login_frame_set["notice_textvar"].set("账号为应聘编号 密码为您设置的密码")
        self.login_frame_set["notice"] = ttk.Label(self.login_frame_set["frame"], textvariable=self.login_frame_set["notice_textvar"], anchor=CENTER, foreground="red")
        self.login_frame_set["notice"].grid(column=1, row=3)

        # self.login_frame_set["account_entry_text"] = ttk.Label(self.login_frame_set["frame"], text="账号", width=12)
        # self.login_frame_set["account_entry_text"].grid(column=0, row=4)
        self.login_frame_set["account_entry"] = ttk.Entry(self.login_frame_set["frame"])
        self.login_frame_set["account_entry"].grid(column=1, row=4)
        # self.login_frame_set["password_entry_text"] = ttk.Label(self.login_frame_set["frame"], text="密码", width=12)
        # self.login_frame_set["password_entry_text"].grid(column=0, row=5)
        self.login_frame_set["password_entry"] = ttk.Entry(self.login_frame_set["frame"], show="*")
        self.login_frame_set["password_entry"].grid(column=1, row=5)

        self.login_frame_set["login_button"] = ttk.Button(self.login_frame_set["frame"], text="登录", command=self.button_login_handle)
        self.login_frame_set["login_button"].grid(column=1, row=6)

        self.main_window.mainloop()

    def button_login_handle(self):

        """
        响应登录按钮
        :return:
        """
        self.log.add_log("OISCandidateClient: login button was pressed, start handle", 1)
        self.login_frame_set["notice_textvar"].set("登录中...")

        account, password = self.login_frame_set["account_entry"].get(), self.login_frame_set["password_entry"].get()
        if account == "" or password == "":
            self.login_frame_set["notice_textvar"].set("账号或密码不能为空")
            return
        # if self.user_manager.login(account, password):
        if True:
            self.login_frame_set["notice_textvar"].set("登录成功，加载中...")
            self.load_main_frame()
        else:
            self.login_frame_set["notice_textvar"].set("账号或密码错误，或者网络问题，请重试")

    def load_main_frame(self):

        """
        加载主页面
        :return:
        """
        self.log.add_log("OISCandidateClient: load main frame...", 1)

        self.login_frame_set["frame"].destory()

        self.main_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.main_frame_set["frame"].grid()

        self.main_frame_set["title"] = ttk.Label(self.main_frame_set["frame"], text="OIS面试者端 主界面", background="lightblue")
        self.main_frame_set["title"].grid(column=1, row=1)

        self.main_frame_set["notice_textvar"] = StringVar()
        self.main_frame_set["notice_textvar"].set("加载中...")
        self.main_frame_set["notice"] = ttk.Label(self.main_frame_set["frame"], textvariable=self.main_frame_set["notice_textvar"], anchor=CENTER, foreground="red")
        self.main_frame_set["notice"].grid(column=1, row=2)




