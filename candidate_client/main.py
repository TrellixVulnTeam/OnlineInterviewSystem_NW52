# coding=utf-8
# main.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/09
# description: candidate client main: ui+main_logic

from tkinter import *
from tkinter import ttk
import time

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
        self.interview_info_frame_set = {}

        self.status = ""
        self.enterprise_interview_info = self.user_manager.get_enterprise_interview_info()

        self.get_status()

    def get_status(self):

        """
        获取当前状态
        :return:
        """
        interview_phase = self.get_interview_phase()
        if interview_phase == 1:
            self.status = "第一批初级面试"
        elif interview_phase == 2:
            self.status = "第一批终极面试"
        elif interview_phase == 3:
            self.status = "第二批初级面试"
        elif interview_phase == 4:
            self.status = "第二批终极面试"

        if self.setting["interviewMethod"] == 1:
            self.status = self.status + " 一对一面试"
        elif self.setting["interviewMethod"] == 2:
            self.status = self.status + " 群面"
        elif self.setting["interviewMethod"] == 3:
            self.status = self.status + "终极面试"

        self.status = self.status + " 单位: %s" % self.setting["enterpriseOrder"]

    def get_interview_phase(self):

        """
        获取当前为什么面试环节
        :return:
        """
        self.log.add_log("OISCandidateClient: calculate what phase of interview is now", 1)

        arr = self.setting["interviewPhaseArrangement"]
        now_time = time.strftime("%H%M", time.localtime())

        for time_range in list(arr.keys()):
            a, b = time_range.split("-")[0], time_range.split("-")[1]
            if a < now_time < b:
                self.log.add_log("OISCandidateClient: now phase: %s" % arr[time_range], 1)
                return arr[time_range]

    def start(self):

        """
        run app(open the window)
        :return:
        """
        self.log.add_log("OISCandidateClient: start the OIS Candidate Client now", 1)

        self.load_login_frame()

    def load_login_frame(self):

        """
        加载登录界面
        :return:
        """
        self.log.add_log("OISCandidateClient: load login frame...", 1)
        # load login frame
        self.login_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.login_frame_set["frame"].grid()

        self.login_frame_set["title"] = ttk.Label(self.login_frame_set["frame"], text="OIS面试者端 登录界面", anchor=CENTER, background="lightblue")
        self.login_frame_set["title"].grid(column=1, row=1)

        self.login_frame_set["status"] = ttk.Label(self.login_frame_set["frame"], text=self.status, foreground="yellow", background="red")
        self.login_frame_set["status"].grid(column=1, row=1)

        self.login_frame_set["notice_textvar"] = StringVar()
        self.login_frame_set["notice_textvar"].set("本机对应单位编号：%s" % self.setting["enterpriseOrder"])
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

        self.login_frame_set["author"] = ttk.Label(self.login_frame_set["frame"], text="Developed By Lanzhijiang", anchor=CENTER, foreground="lightblue")
        self.login_frame_set["author"].grid(column=1, row=7)

        self.main_window.mainloop()

    def load_main_frame(self):

        """
        加载主页面
        :return:
        """
        self.log.add_log("OISCandidateClient: load main frame...", 1)

        self.main_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.main_frame_set["frame"].grid()

        self.main_frame_set["title"] = ttk.Label(self.main_frame_set["frame"], text="OIS面试者端 主界面", background="lightblue")
        self.main_frame_set["title"].grid(column=1, row=1)

        self.main_frame_set["status"] = ttk.Label(self.main_frame_set["frame"], text=self.status, foreground="yellow", background="red")
        self.main_frame_set["status"].grid(column=1, row=2)

        self.main_frame_set["notice_textvar"] = StringVar()
        self.main_frame_set["notice_textvar"].set("加载中...")
        self.main_frame_set["notice"] = ttk.Label(self.main_frame_set["frame"], textvariable=self.main_frame_set["notice_textvar"], anchor=CENTER, foreground="red")
        self.main_frame_set["notice"].grid(column=1, row=3)

        self.main_frame_set["interview_info_frame"] = ttk.Frame(self.main_frame_set["frame"], padding=2)
        self.main_frame_set["interview_info_frame"].grid(column=1, row=3)
        self.load_interview_info_frame()

        self.main_frame_set["entry"] = ttk.Entry(self.main_frame_set["frame"])
        self.main_frame_set["entry"].grid(column=1, row=4)

        self.main_frame_set["submit_button"] = ttk.Button(self.main_frame_set["frame"], text="提交", command=self.button_submit_handle)
        self.main_frame_set["submit_button"].grid(column=1, row=5)

        self.main_frame_set["submit_button"] = ttk.Button(self.main_frame_set["frame"], text="退出登录", command=self.button_logout_handle)
        self.main_frame_set["submit_button"].grid(column=1, row=6)

        self.login_frame_set["author"] = ttk.Label(self.login_frame_set["frame"], text="Developed By Lanzhijiang", anchor=CENTER, foreground="lightblue")
        self.login_frame_set["author"].grid(column=1, row=7)

    def load_interview_info_frame(self):

        """
        加载面试信息
        :return:
        """
        self.log.add_log("OISCandidateClient: load interview info frame", 1)

        user_interview_info = self.user_manager.get_user_interview_info()

        self.interview_info_frame_set["name"] = ttk.Label(self.main_frame_set["interview_info_frame"], text=user_interview_info["name"], anchor=LEFT)
        self.interview_info_frame_set["name"].grid(column=0, row=1)
        self.interview_info_frame_set["class"] = ttk.Label(self.main_frame_set["interview_info_frame"], text="高二%s班" % user_interview_info["class"], anchor=LEFT)
        self.interview_info_frame_set["class"].grid(column=0, row=2)
        self.interview_info_frame_set["order"] = ttk.Label(self.main_frame_set["interview_info_frame"], text="应聘编号：%s" % user_interview_info["order"], anchor=LEFT)
        self.interview_info_frame_set["order"].grid(column=0, row=3)

        self.interview_info_frame_set["enterprise_name"] = ttk.Label(self.main_frame_set["interview_info_frame"],
                                                            text="企业名称：%s" % self.enterprise_interview_info["name"],
                                                            anchor=RIGHT)
        self.interview_info_frame_set["enterprise_name"].grid(column=0, row=4)
        self.interview_info_frame_set["now_for_job_textvar"] = StringVar()
        self.interview_info_frame_set["now_for_job_textvar"].set("正在应聘岗位: ?")
        self.interview_info_frame_set["now_for_job"] = ttk.Label(self.main_frame_set["interview_info_frame"],
                                                        textvariable=self.interview_info_frame_set["now_for_job_textvar"],
                                                        anchor=RIGHT)
        self.interview_info_frame_set["now_for_job"].grid(column=0, row=5)

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
            self.log.add_log("OISCandidateClient: login success", 1)
            self.login_frame_set["notice_textvar"].set("登录成功，加载中...")
            time.sleep(2)
            self.login_frame_set["frame"].destroy()
            self.load_main_frame()
            self.start_interview()
        else:
            self.log.add_log("OISCandidateClient: login failed", 1)
            self.login_frame_set["notice_textvar"].set("账号或密码错误，或者网络问题，请重试")

    def button_logout_handle(self):

        """
        响应登出按钮
        :return:
        """
        self.log.add_log("OISCandidateClient: logout button was pressed, start handle", 1)
        self.main_frame_set["notice_textvar"].set("登出中...")

        if self.user_manager.logout():
            self.log.add_log("OISCandidateClient: logout success", 1)
            self.main_frame_set["notice_textvar"].set("登出成功！")
            time.sleep(2)
            self.main_frame_set["frame"].destroy()
            self.load_login_frame()
        else:
            self.log.add_log("OISCandidateClient: logout failed", 1)
            self.main_frame_set["notice_textvar"].set("发生错误！")

    def button_submit_handle(self):

        """
        响应提交按钮
        :return:
        """

    def start_interview(self):

        """
        开始面试
        :return:
        """

