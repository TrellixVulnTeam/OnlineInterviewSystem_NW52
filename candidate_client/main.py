# coding=utf-8
# main.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/09
# description: candidate client main: ui+main_logic
import json
import threading
import webbrowser
from tkinter import *
from tkinter import ttk
import time


class OISCandidateClient:
    """OIS Candidate Client Main Class: ui windows and main logic"""
    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.user_manager = ba.user_manager
        self.request = ba.request
        self.tts = ba.tts

        self.main_window = Tk(className="(*^▽^*) OIIS")
        self.main_window.title("OIIS CC")
        self.main_window.maxsize(350, 600)

        self.temp_frame_set = {}
        self.login_frame_set = {}
        self.main_frame_set = {}
        self.interview_info_frame_set = {}

        self.status = ba.status
        self.interview_phase = ba.interview_phase
        self.enterprise_interview_info = {}

        self.interview_status = "logged_out"
        self.meeting_room_code = ""

    def start(self):

        """
        run app(open the window)
        :return:
        """
        self.log.add_log("OIISCandidateClient: start the OIIS Candidate Client now", 1)
        if self.setting["comCode"] is None:
            self.log.add_log("OIISCandidateClient: config is empty, load reset_frame", 1)
            self.load_reset_config_frame()
            return

        res, err = self.request.get_enterprise_info(self.setting["bindEnterpriseCode"])
        if res is not False:
            self.enterprise_interview_info = res["enterpriseInfo"]
            # self.meeting_room_password = self.setting["comCode"] + self.enterprise_interview_info["interviewer"][0]["phone"][-4:]
        else:
            self.log.add_log("OIISCandidateClient: can't get enterprise info, err-%s" % err, 3)

        self.ba.get_status()
        self.status = self.ba.status
        self.load_login_frame()

    def tts_auto(self):

        """
        自动监测notice_textvar的变化，从而进行tts合成
        :return:
        """
        self.log.add_log("Tts: auto tts, start", 1)

        last = ""
        while True:
            time.sleep(1.5)
            if self.interview_status == "logged_out":
                break
            else:
                now = self.main_frame_set["notice_textvar"].get()
                if now != last:
                    self.tts.start(now)
                    last = now

    def load_reset_config_frame(self):

        """
        加载重置配置界面
        :return:
        """
        self.temp_frame_set = {}
        self.temp_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.temp_frame_set["frame"].grid()

        self.temp_frame_set["title"] = ttk.Label(self.temp_frame_set["frame"], text="OIIS面试者端 重置配置", anchor=CENTER,
                                                 background="lightblue")
        self.temp_frame_set["title"].grid(column=1, row=1)

        self.temp_frame_set["notice_textvar"] = StringVar()
        self.temp_frame_set["notice_textvar"].set("请重置配置，输入该机编号即可")

        self.temp_frame_set["notice"] = ttk.Label(self.temp_frame_set["frame"],
                                                  textvariable=self.temp_frame_set["notice_textvar"], anchor=CENTER,
                                                  foreground="red")
        self.temp_frame_set["notice"].grid(column=1, row=3)

        self.temp_frame_set["bind_com_code_entry"] = ttk.Entry(self.temp_frame_set["frame"])
        self.temp_frame_set["bind_com_code_entry"].grid(column=1, row=4)

        self.temp_frame_set["reset_button"] = ttk.Button(self.temp_frame_set["frame"], text="重置",
                                                         command=self.button_reset_config_handle)
        self.temp_frame_set["reset_button"].grid(column=1, row=6)

        self.main_window.mainloop()

    def load_login_frame(self):

        """
        加载登录界面
        :return:
        """
        self.log.add_log("OIISCandidateClient: load login frame...", 1)
        # load login frame
        self.login_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.login_frame_set["frame"].grid()

        self.login_frame_set["title"] = ttk.Label(self.login_frame_set["frame"], text="OIIS面试者端 登录界面", anchor=CENTER, background="lightblue")
        self.login_frame_set["title"].grid(column=1, row=1)

        self.login_frame_set["status"] = ttk.Label(self.login_frame_set["frame"], text=self.status, foreground="yellow", background="red")
        self.login_frame_set["status"].grid(column=1, row=2)

        self.login_frame_set["notice_textvar"] = StringVar()
        self.login_frame_set["notice_textvar"].set("请登录，账号即编号，密码即设置的密码")

        self.login_frame_set["notice"] = ttk.Label(self.login_frame_set["frame"], anchor=CENTER, textvariable=self.login_frame_set["notice_textvar"], foreground="red")
        self.login_frame_set["notice"].grid(column=1, row=3)

        self.login_frame_set["account_entry"] = ttk.Entry(self.login_frame_set["frame"])
        self.login_frame_set["account_entry"].grid(column=1, row=4)

        self.login_frame_set["password_entry"] = ttk.Entry(self.login_frame_set["frame"], show="*")
        self.login_frame_set["password_entry"].grid(column=1, row=5)

        self.login_frame_set["login_button"] = ttk.Button(self.login_frame_set["frame"], text="登录", command=self.button_login_handle)
        self.login_frame_set["login_button"].grid(column=1, row=6)

        self.login_frame_set["other"] = ttk.Label(self.login_frame_set["frame"], text="UI丑没办法的啦，体谅一下好吗",
                                                   anchor=CENTER, foreground="lightblue", background="red")
        self.login_frame_set["other"].grid(column=1, row=8)

        self.login_frame_set["author"] = ttk.Label(self.login_frame_set["frame"], text="Developed By Lanzhijiang", anchor=CENTER, foreground="lightblue")
        self.login_frame_set["author"].grid(column=1, row=7)

        self.main_window.mainloop()

    def load_main_frame(self):

        """
        加载主页面
        :return:
        """
        self.log.add_log("OIISCandidateClient: load main frame...", 1)

        self.main_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.main_frame_set["frame"].grid()

        self.main_frame_set["title"] = ttk.Label(self.main_frame_set["frame"], text="OIIS面试者端 主界面", background="lightblue")
        self.main_frame_set["title"].grid(column=1, row=1)

        self.main_frame_set["status"] = ttk.Label(self.main_frame_set["frame"], text=self.status, foreground="yellow", background="red")
        self.main_frame_set["status"].grid(column=1, row=2)

        self.main_frame_set["notice_textvar"] = StringVar()
        self.main_frame_set["notice_textvar"].set("加载中...")
        self.main_frame_set["notice"] = ttk.Label(self.main_frame_set["frame"], textvariable=self.main_frame_set["notice_textvar"], anchor=CENTER, foreground="red")
        self.main_frame_set["notice"].grid(column=1, row=3)

        tts_thread = threading.Thread(target=self.tts_auto, args=())
        tts_thread.start()

        self.main_frame_set["interview_info_frame"] = ttk.Frame(self.main_frame_set["frame"], padding=2)
        self.main_frame_set["interview_info_frame"].grid(column=1, row=4)
        self.load_interview_info_frame()

        self.main_frame_set["enterprise_jobs_combobox_title"] = ttk.Label(self.main_frame_set["interview_info_frame"],
                                                                                    text="岗位列表：",
                                                                                    anchor=W)
        self.main_frame_set["enterprise_jobs_combobox_title"].grid(column=1, row=5)

        jobs_raw = self.enterprise_interview_info["jobs"]
        jobs = []
        for i in list(jobs_raw.keys()):
            str_ = "%s: %s" % (i, jobs_raw[i])
            jobs.append(str_)
        self.main_frame_set["job_combobox"] = ttk.Combobox(self.main_frame_set["frame"])
        self.main_frame_set["job_combobox"]["value"] = jobs
        self.main_frame_set["job_combobox"].grid(column=1, row=6)

        self.main_frame_set["submit_job_button"] = ttk.Button(self.main_frame_set["frame"], text="提交", command=self.button_submit_job_handle)
        self.main_frame_set["submit_job_button"].grid(column=1, row=7)

        self.main_frame_set["open_meeting_room"] = ttk.Button(self.main_frame_set["frame"], text="查看会议号",
                                                              command=self.button_open_meeting_room_handle)
        self.main_frame_set["open_meeting_room"].grid(column=1, row=8)

        self.main_frame_set["author"] = ttk.Label(self.main_frame_set["frame"], text="Developed By Lanzhijiang", anchor=CENTER, foreground="white", background="lightblue")
        self.main_frame_set["author"].grid(column=1, row=10)

        self.main_frame_set["notice_textvar"].set("请选择岗位后提交，别手滑了！只能提交一次")

    def load_interview_info_frame(self):

        """
        加载面试信息
        :return:
        """
        self.log.add_log("OIISCandidateClient: load interview info frame", 1)

        user_interview_info = self.user_manager.get_user_interview_info()
        if user_interview_info is False:
            self.log.add_log("OIISCandidateClient: load interview info frame failed, get user_interview_info failed", 3)
            return

        print(user_interview_info)

        self.interview_info_frame_set["candidate_brief_info"] = ttk.Label(self.main_frame_set["interview_info_frame"], text="高二%s班" % user_interview_info["class"] + " " + user_interview_info["nickname"] + "  " + user_interview_info["code"], anchor=E)
        self.interview_info_frame_set["candidate_brief_info"].grid(column=1, row=1)

        self.interview_info_frame_set["enterprise_name"] = ttk.Label(self.main_frame_set["interview_info_frame"],
                                                                     text="应聘企事业：%s" % self.enterprise_interview_info["name"],
                                                                     anchor=W)
        self.interview_info_frame_set["enterprise_name"].grid(column=1, row=3)

        self.interview_info_frame_set["now_for_job_textvar"] = StringVar()
        self.interview_info_frame_set["now_for_job_textvar"].set("正在应聘岗位: ?")
        self.interview_info_frame_set["now_for_job"] = ttk.Label(self.main_frame_set["interview_info_frame"],
                                                                 textvariable=self.interview_info_frame_set["now_for_job_textvar"],
                                                                 anchor=W)
        self.interview_info_frame_set["now_for_job"].grid(column=1, row=4)

    def button_reset_config_handle(self):

        """
        响应重置配置按钮
        :return:
        """
        self.log.add_log("OIISCandidateClient: reset config was pressed, start handle", 1)
        com_code = self.temp_frame_set["bind_com_code_entry"].get()
        res, err = self.request.get_com_info(com_code)
        if res is False or not res["comInfo"]:
            self.temp_frame_set["notice_textvar"].set("面试终端编号错误，请重新输入: %s" % err)
        else:
            com_info = res["comInfo"]
            self.setting["bindEnterpriseCode"] = com_info["bindEnterprise"]
            self.setting["bindInterviewerCode"] = com_info["bindInterviewer"]
            self.setting["comCode"] = com_code
            self.setting["interviewCandidateQueue"] = []
            self.setting["interviewCandidateQueue"] = list(com_info["interviewQueue"]["wait"].keys())

            json.dump(self.setting, open("./data/json/setting.json", "w", encoding="utf-8"))
            self.temp_frame_set["notice_textvar"].set("设置成功，请重新启动客户端")

    def button_login_handle(self):

        """
        响应登录按钮
        :return:
        """
        self.log.add_log("OIISCandidateClient: login button was pressed, start handle", 1)
        self.login_frame_set["notice_textvar"].set("登录中...")

        account, password = self.login_frame_set["account_entry"].get(), self.login_frame_set["password_entry"].get()
        if account == "" or password == "":
            self.login_frame_set["notice_textvar"].set("账号或密码不能为空")
            
            return
        if self.user_manager.login(account, password):
            self.log.add_log("OIISCandidateClient: login success", 1)
            self.login_frame_set["notice_textvar"].set("登录成功，加载中...")
            
            self.login_frame_set["frame"].destroy()
            self.interview_status = "wait"
            self.load_main_frame()
        else:
            self.log.add_log("OIISCandidateClient: login failed", 1)
            self.login_frame_set["notice_textvar"].set("请确认登录终端机号正确，账号密码正确，面试阶段正确")

    def button_logout_handle(self):

        """
        响应登出按钮
        :return:
        """
        self.log.add_log("OIISCandidateClient: logout button was pressed, start handle", 1)
        self.main_frame_set["notice_textvar"].set("登出中...")

        if self.user_manager.logout():
            self.log.add_log("OIISCandidateClient: logout success", 1)
            self.main_frame_set["notice_textvar"].set("登出成功！")
            
            time.sleep(2)
            self.interview_status = "logged_out"
            time.sleep(2)
            self.main_frame_set["frame"].destroy()
            self.load_login_frame()
        else:
            self.log.add_log("OIISCandidateClient: logout failed", 1)
            self.main_frame_set["notice_textvar"].set("发生错误！")

    def button_submit_job_handle(self):

        """
        响应提交按钮
        :return:
        """
        self.log.add_log("OIISCandidateClient: login button was pressed, start handle", 1)
        self.main_frame_set["notice_textvar"].set("数据上传中...")
        
        job_id = self.main_frame_set["job_combobox"].get().split(":")[0]  # a string
        try:
            job_id_int = int(job_id)
        except ValueError:
            self.log.add_log("OIISCandidateClient: job can't be empty", 3)
            self.main_frame_set["notice_textvar"].set("请选择岗位，不能是空")
            return
        res, err = self.request.set_apply_job(job_id_int)
        if res:
            # set job success
            self.main_frame_set["enterprise_jobs_combobox_title"].destroy()
            self.main_frame_set["job_combobox"].destroy()
            self.main_frame_set["submit_job_button"].destroy()

            self.main_frame_set["notice_textvar"].set("成功！等待面试官点击'开始面试'")
            self.interview_info_frame_set["now_for_job_textvar"].set("正在应聘岗位: %s" % self.enterprise_interview_info["jobs"][str(job_id)])

            count_thread = threading.Thread(target=self.start_count, args=())
            count_thread.start()
        else:
            # set job failed
            self.main_frame_set["notice_textvar"].set("错误，请上报: %s" % err)

    def button_open_meeting_room_handle(self):

        """
        响应打开面试室按钮
        :return:
        """
        self.log.add_log("OIISInterviewerClient: open_meeting_room button was pressed, start handle", 1)
        self.meeting_room_code = self.request.get_meeting_room_code()
        self.main_frame_set["notice_textvar"].set("腾讯会议号码是：%s" % self.meeting_room_code)

        # time.sleep(1.5)
        # webbrowser.open("https://meeting.hadream.ltd/%s" % self.setting["comCode"], new=0, autoraise=True)
        # self.main_frame_set["notice_textvar"].set("会议密码是%s" % self.meeting_room_password)

    def start_count(self):

        """
        开始计时
        start: 0
        open end_button: 5
        force_end: 8m30s
        :return:
        """
        self.log.add_log("OIISInterviewerClient: wait for interview start", 1)
        time.sleep(5)
        while True:
            res, err = self.request.is_interview_started()
            if res is False and err != "success":
                self.log.add_log("OIISCandidateClient: fail to get is_interview_started", 3)
                break
            else:
                if res:
                    self.log.add_log("OIISCandidateClient: interview has started", 1)
                    self.main_frame_set["notice_textvar"].set("面试开始。最少5分钟，最多8分钟，请把控好时间")
                    break
            time.sleep(5)
        self.interview_status = "in_interview"

        self.log.add_log("OIISInterviewerClient: start count interview time", 1)

        # time.sleep(300)
        time.sleep(20)
        self.log.add_log("OIISInterviewerClient: 5min passed", 1)
        self.main_frame_set["notice_textvar"].set("已经五分钟了哦！")
        is_end_thread = threading.Thread(target=self.is_interview_end, args=())
        is_end_thread.start()

        time.sleep(18)
        # time.sleep(180)
        if self.interview_status == "in_interview":
            self.main_frame_set["notice_textvar"].set("已经八分钟了！")
            time.sleep(15)
            self.end_interview()

    def is_interview_end(self):

        """
        检测面试是否结束
        :return:
        """
        self.log.add_log("OIISInterviewerClient: start detect is interview end", 1)
        while True:
            res, err = self.request.is_interview_end()
            if res is False and err != "success":
                self.log.add_log("OIISCandidateClient: fail to get is_interview_end", 3)
                break
            else:
                if res:
                    break

        self.end_interview()

    def end_interview(self):

        """
        结束面试
        :return:
        """
        self.log.add_log("OIISCandidateClient: interview has end", 1)
        self.main_frame_set["notice_textvar"].set("面试结束。")
        time.sleep(2.5)
        self.main_window["logout_button"] = ttk.Button(self.main_frame_set["frame"], text="登出", command=self.button_logout_handle)
        self.login_frame_set["logout_button"].grid(column=1, row=9)
        self.main_frame_set["notice_textvar"].set("请退出登录，不用关闭终端")
        time.sleep(2.5)
        self.main_frame_set["notice_textvar"].set("摆放好凳子与设备，安静回班。")
        self.interview_status = "wait"
        time.sleep(5)
