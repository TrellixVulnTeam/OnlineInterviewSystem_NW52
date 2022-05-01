# coding=utf-8
# main.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/24
# description: interviewer client main: ui+main_logic

import threading
from tkinter import *
from tkinter import ttk
import time
import webbrowser
import io
import requests
from PIL import Image, ImageTk

from ws_client import WsClient


class OIISInterviewerClient:
    """OIIS Interviewer Client Main Class: ui windows and main logic"""
    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.user_manager = ba.user_manager
        self.request = ba.request
        self.player = ba.player
        self.tts = ba.tts
        self.ba.main = self
        self.ws_client = WsClient(ba)

        self.main_window = Tk(className="(*^▽^*) OIIS")
        self.main_window.title("OIIS IC")
        self.main_window.maxsize(350, 600)

        self.interview_status = "wait"

        self.login_frame_set = {}
        self.main_frame_set = {}
        self.interview_history_frame_set = {}
        self.interview_info_frame_set = {}

        self.enterprise_interview_info = {}
        self.interview_history = []
        self.com_info = {}
        self.now_candidate = ba.now_candidate
        self.now_candidate_info = None
        self.meeting_room_password = ""

    def start(self):

        """
        run app(open the window)
        :return:
        """
        self.log.add_log("OIISInterviewerClient: start the OIIS Interviewer Client now", 1)

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
            now = self.main_frame_set["notice_textvar"].get()
            if now != last:
                self.tts.start(now)
                last = now

    def load_login_frame(self):

        """
        加载登录界面
        :return:
        """
        self.log.add_log("OIISInterviewerClient: load login frame...", 1)
        # load login frame
        self.login_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.login_frame_set["frame"].grid()

        self.login_frame_set["title"] = ttk.Label(self.login_frame_set["frame"], text="OIIS面试官端 登录界面", anchor=CENTER, background="lightblue")
        self.login_frame_set["title"].grid(column=0, row=1)

        self.login_frame_set["notice_textvar"] = StringVar()
        self.login_frame_set["notice_textvar"].set("请登录，账号即编号，密码即手机号")

        self.login_frame_set["notice"] = ttk.Label(self.login_frame_set["frame"], textvariable=self.login_frame_set["notice_textvar"], anchor=CENTER, foreground="red")
        self.login_frame_set["notice"].grid(column=0, row=3)

        self.login_frame_set["account_entry"] = ttk.Entry(self.login_frame_set["frame"])
        self.login_frame_set["account_entry"].grid(column=0, row=4)

        self.login_frame_set["password_entry"] = ttk.Entry(self.login_frame_set["frame"], show="*")
        self.login_frame_set["password_entry"].grid(column=0, row=5)

        self.login_frame_set["login_button"] = ttk.Button(self.login_frame_set["frame"], text="登录", command=self.button_login_handle)
        self.login_frame_set["login_button"].grid(column=0, row=6)

        self.login_frame_set["other"] = ttk.Label(self.login_frame_set["frame"], text="没时间优化，UI丑，体谅一下好吗",
                                                   anchor=CENTER, foreground="lightblue", background="red")
        self.login_frame_set["other"].grid(column=0, row=8)

        self.login_frame_set["author"] = ttk.Label(self.login_frame_set["frame"], text="Developed By Lanzhijiang", anchor=CENTER, foreground="lightblue")
        self.login_frame_set["author"].grid(column=0, row=9)

        self.main_window.mainloop()

    def load_main_frame(self):

        """
        加载主页面
        :return:
        """
        self.log.add_log("OIISInterviewerClient: load main frame...", 1)

        self.main_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.main_frame_set["frame"].grid()

        self.main_frame_set["title"] = ttk.Label(self.main_frame_set["frame"], text="OIIS面试官端 主界面", background="lightblue")
        self.main_frame_set["title"].grid(column=0, row=1)

        self.main_frame_set["notice_textvar"] = StringVar()
        self.main_frame_set["notice_textvar"].set("加载中...")

        tts_thread = threading.Thread(target=self.tts_auto, args=())
        tts_thread.start()

        self.main_frame_set["notice"] = ttk.Label(self.main_frame_set["frame"], textvariable=self.main_frame_set["notice_textvar"], anchor=CENTER, foreground="red")
        self.main_frame_set["notice"].grid(column=0, row=3)

        self.main_frame_set["interview_info_frame"] = ttk.Frame(self.main_frame_set["frame"], padding=2)
        self.main_frame_set["interview_info_frame"].grid(column=0, row=4)
        self.load_interview_info_frame()

        self.main_frame_set["open_meeting_room"] = ttk.Button(self.main_frame_set["frame"], text="进入会议室", command=self.button_open_meeting_room_handle)
        self.main_frame_set["open_meeting_room"].grid(column=0, row=8)

        self.main_frame_set["notice_textvar"].set("请务必先行进入会议室")

    def load_now_interview_info(self, candidate_code):

        """
        加载当前面试信息(归属interview_info_frame)
        now candidate's info(name code photo selfIntroduction)
        :return:
        """
        self.log.add_log("OIISInterviewerClient: load now interview frame", 1)

        # load candidate info
        res, err = self.request.get_candidate_info(candidate_code)
        if res is False:
            self.log.add_log("OIISInterviewerClient: can't load now's candidate info!")
            self.main_frame_set["notice_textvar"].set("发生错误！无法获取当前面试者信息")
            self.ws_client.send_response("candidate_online", {"code": 1, "msg": "can't get candidate info"})
            return
        else:
            candidate_info = res["candidateInfo"]
            self.now_candidate_info = candidate_info
            self.now_candidate = candidate_code

        candidate_brief = "高二%s班%s同学 编号%s" % (candidate_info["class"], candidate_info["name"], candidate_code)
        self.interview_info_frame_set["candidate_brief"] = ttk.Label(self.main_frame_set["interview_info_frame"],
                                                                     text=candidate_brief, anchor=E)
        self.interview_info_frame_set["candidate_brief"].grid(column=0, row=2)

        if candidate_info["selfIntroduction"] is None or candidate_info["selfIntroduction"] == "":
            candidate_info["selfIntroduction"] = "这个人没写，可以看看TA的简历"
        self.interview_info_frame_set["self_introduction"] = ttk.Label(self.main_frame_set["interview_info_frame"],
                                                                       text="自我介绍：" + candidate_info["selfIntroduction"], anchor=E)
        self.interview_info_frame_set["self_introduction"].grid(column=0, row=3)

        try:
            photo = ImageTk.PhotoImage(Image.open(io.BytesIO(requests.get("http://119.29.85.53:6000/%s" % candidate_info["photo"]).content)).resize((90, 160)))
            self.interview_info_frame_set["photo"] = ttk.Label(text="个人照片", image=photo)
            self.interview_info_frame_set["photo"].grid(column=0, row=4)
        except:
            pass

        self.main_frame_set["notice_textvar"].set("面试者已经上线，等待提交面试岗位")

    def destroy_now_interview_info(self):

        """
        删除当前面试信息
        :return:
        """
        self.log.add_log("OIISInterviewerClient: delete now interview info(candidate part)", 1)
        keys = ["candidate_brief", "self_introduction", "photo"]
        for key in keys:
            try:
                self.interview_info_frame_set[key].destroy()
            except KeyError:
                pass

    def load_interview_info_frame(self):

        """
        加载面试信息frame
        interviewer's enterprise info
        :return:
        """
        self.log.add_log("OIISInterviewerClient: load interview info frame", 1)
        
        res, err = self.request.get_enterprise_info(self.setting["bindEnterpriseCode"])
        if res is False:
            self.log.add_log("OIISInterviewerClient: can't get enterprise info, err-%s" % err, 3)
            return
        self.enterprise_interview_info = res["enterpriseInfo"]
        self.meeting_room_password = self.setting["bindComCode"] + self.enterprise_interview_info["interviewer"][0]["phone"][-4:]

        self.interview_info_frame_set["enterprise_name"] = ttk.Label(self.main_frame_set["interview_info_frame"],
                                                                     text="所属企事业：%s" % self.enterprise_interview_info["name"])
        self.interview_info_frame_set["enterprise_name"].grid(column=0, row=1)

    def load_interview_history_frame(self):

        """
        加载面试历史frame(main_frame的子frame)
        :return:
        """
        self.log.add_log("OIISInterviewerClient: load interview history frame", 1)

        self.main_frame_set["interview_history_frame"] = ttk.Frame(self.main_frame_set["frame"], padding=2)
        self.main_frame_set["interview_history_frame"].grid(column=0, row=4)

        self.interview_history_frame_set["title"] = ttk.Label(self.main_frame_set["interview_history_frame"], text="面试历史")
        self.interview_history_frame_set["title"].grid(column=0, row=1)

        sb = Scrollbar(self.main_frame_set["interview_history_frame"])
        sb.grid(column=2, rowspan=len(self.interview_history))
        lb = Listbox(self.main_frame_set["interview_history_frame"], yscrollcommand=sb.set)
        for i in self.interview_history:
            lb.insert(END, i)
        lb.grid(columnspan=3, rowspan=len(self.interview_history))
        sb.config(command=lb.yview)

    def start_count(self):

        """
        开始计时
        start: 0
        open end_button: 5
        force_end: 8m30s
        :return:
        """
        self.log.add_log("OIISInterviewerClient: start count interview time", 1)
        # time.sleep(300)
        time.sleep(20)
        self.log.add_log("OIISInterviewerClient: 5min passed, shown end_interview_button", 1)
        self.main_frame_set["notice_textvar"].set("已经五分钟了哦！")
        self.main_frame_set["end_interview_button"] = ttk.Button(self.main_frame_set["frame"],
                                                                 text="结束面试",
                                                                 command=self.button_end_interview_handle)
        self.main_frame_set["end_interview_button"].grid(column=0, row=5)
        time.sleep(18)
        # time.sleep(180)
        if self.interview_status == "in_interview":
            self.main_frame_set["notice_textvar"].set("已经八分钟了！即将强制结束面试！")
            time.sleep(10)
            if self.interview_status == "in_interview":
                self.button_end_interview_handle()

    def button_login_handle(self):

        """
        响应登录按钮
        :return:
        """
        self.log.add_log("OIISInterviewerClient: login button was pressed, start handle", 1)
        self.login_frame_set["notice_textvar"].set("登录中...")

        account, password = self.login_frame_set["account_entry"].get(), self.login_frame_set["password_entry"].get()
        if account == "" or password == "":
            self.login_frame_set["notice_textvar"].set("账号或密码不能为空")
            return
        self.setting["bindComCode"] = "com%s" % account[0:2]
        if self.user_manager.login(account, password):
            self.log.add_log("OIISInterviewerClient: login success", 1)
            self.login_frame_set["notice_textvar"].set("登录成功，加载中...")
            # update setting
            self.log.add_log("OIISInterviewerClient: try to update com_info and bindEnterprise", 1)
            res, err = self.request.user_info_get_multi(account, ["mappingComCode"])
            if res is False:
                self.log.add_log("OIISInterviewerClient: fail to get com_code! critical error", 3)
                self.login_frame_set["notice_textvar"].set("遇到严重错误！请上报: can't get com_code")
            else:
                com_code = res["userInfo"]["mappingComCode"]
                self.setting["bindComCode"] = com_code
                res, err = self.request.get_com_info(com_code)
                if res is False:
                    self.log.add_log("OIISInterviewerClient: fail to get com_code! critical error", 3)
                    self.login_frame_set["notice_textvar"].set("遇到严重错误！请上报: can't get com_info")
                else:
                    self.com_info = res["comInfo"]
                    self.setting["bindComCode"] = com_code
                    self.setting["bindEnterpriseCode"] = self.com_info["bindEnterprise"]

            self.login_frame_set["frame"].destroy()
            self.load_main_frame()

            self.log.add_log("OIISInterviewerClient: login success, try connect to websocket server", 1)
            self.ws_client.connect_to_server()
        else:
            self.setting["bindComCode"] = None
            self.log.add_log("OIISInterviewerClient: login failed", 1)
            self.login_frame_set["notice_textvar"].set("请确认账号密码是否正确")

    def button_logout_handle(self):

        """
        响应登出按钮
        :return:
        """
        self.log.add_log("OIISInterviewerClient: logout button was pressed, start handle", 1)
        self.main_frame_set["notice_textvar"].set("登出中...")

        if self.user_manager.logout():
            self.log.add_log("OIISInterviewerClient: logout success", 1)
            self.main_frame_set["notice_textvar"].set("登出成功！")
            time.sleep(1.5)
            self.main_frame_set["frame"].destroy()
            self.load_login_frame()
        else:
            self.log.add_log("OIISInterviewerClient: logout failed", 1)
            self.main_frame_set["notice_textvar"].set("发生错误！")

    def button_start_interview_handle(self):

        """
        响应开始面试按钮
        :return:
        """
        self.log.add_log("OIISInterviewerClient: start_interview button was pressed, start handle", 1)

        self.interview_status = "interview_start"
        self.ws_client.send_command("interviewer_start_interview", {"comCode": self.setting["bindComCode"], "candidateCode": self.now_candidate})
        self.main_frame_set["start_interview_button"].destroy()
        self.interview_history.append("%s: %s，面试岗位：%s" % (self.now_candidate, self.now_candidate_info["name"], self.now_candidate_info["appliedJobName"]))

        self.interview_status = "in_interview"
        self.main_frame_set["notice_textvar"].set("面试开始，遇到通讯问题请联系lanzhijiang@foxmail.com")
        count_thread = threading.Thread(target=self.start_count, args=())
        count_thread.start()

    def button_end_interview_handle(self):

        """
        响应结束面试按钮
        :return:
        """
        self.log.add_log("OIISInterviewerClient: end_interview button was pressed, start handle", 1)

        self.interview_status = "interview_end"
        self.main_frame_set["end_interview_button"].destroy()
        self.ws_client.send_command("interviewer_end_interview", {"comCode": self.setting["bindComCode"], "candidateCode": self.now_candidate})
        # self.load_interview_history_frame()
        self.destroy_now_interview_info()

        self.interview_status = "wait"
        self.main_frame_set["notice_textvar"].set("面试已结束，等待下一位面试者...")

    def button_open_meeting_room_handle(self):

        """
        响应打开面试室按钮
        :return:
        """
        self.log.add_log("OIISInterviewerClient: open_meeting_room button was pressed, start handle", 1)
        self.main_frame_set["notice_textvar"].set("即将在浏览器打开会议室")

        time.sleep(1.5)
        webbrowser.open("https://meeting.hadream.ltd/%s" % self.setting["bindComCode"], new=0, autoraise=True)
        self.main_frame_set["notice_textvar"].set("会议密码是%s；进入后不要退出" % self.meeting_room_password)
    
    def event_candidate_online_handle(self, candidate_code):
        
        """
        响应：时间-面试者上线
        :param candidate_code: 面试者编号
        :return: 
        """
        self.log.add_log("OIISInterviewerClient: process event-candidate_online", 1)
        self.load_now_interview_info(candidate_code)
        self.ba.now_candidate = candidate_code
        self.main_frame_set["notice_textvar"].set("面试者%s已经上线，等待选择岗位..." % candidate_code)

    def event_candidate_offline_handle(self):

        """
        响应：时间-面试者下线
        :return:
        """
        self.ba.now_candidate = None
        self.main_frame_set["notice_textvar"].set("面试者下线，结束面试。")
        if self.interview_status == "in_interview":
            self.button_end_interview_handle()
        self.main_frame_set["notice_textvar"].set("等待下一位面试者...")
        self.destroy_now_interview_info()

    def event_candidate_job_sat_handle(self, job_name):

        """
        响应：事件-面试者岗位已选择
        :param job_name: 工作名
        :return:
        """
        self.log.add_log("OIISInterviewerClient: process event-candidate_job_sat", 1)

        self.now_candidate_info["appliedJobName"] = job_name
        self.interview_info_frame_set["applied_job"] = ttk.Label(self.main_frame_set["interview_info_frame"],
                                                                 text="面试岗位：%s" % job_name,
                                                                 anchor=E)
        self.interview_info_frame_set["applied_job"].grid(column=0, row=5)
        self.main_frame_set["notice_textvar"].set("岗位已选择。")
        time.sleep(1.5)
        self.main_frame_set["start_interview_button"] = ttk.Button(self.main_frame_set["frame"],
                                                                   text="开始面试",
                                                                   command=self.button_start_interview_handle)
        self.main_frame_set["start_interview_button"].grid(column=0, row=5)
        self.main_frame_set["notice_textvar"].set("待面试者加入会议后请点击'开始面试'，将开始计时")

        time.sleep(30)
        if self.interview_status != "in_interview":
            self.log.add_log("OIISInterviewerClient: interview still not start, remind", 1)
            self.main_frame_set["notice_textvar"].set("请尽快开始面试！")

        time.sleep(30)
        if self.interview_status != "in_interview":
            self.main_frame_set["notice_textvar"].set("自动开始面试")
            self.button_start_interview_handle()

    def evnet_final_end_interview_handle(self):

        """
        响应：事件-面试已经全部完成
        :return:
        """
        self.log.add_log("OIISInterviewerClient: process event-final_end_interview", 1)

        self.main_frame_set["notice_textvar"].set("恭喜！面试已经全部完成！可以开始审计结果")
        self.main_frame_set["notice_textvar"].set("请在11点20前将结果提交到survey.hadream.ltd上")
        self.main_frame_set["interview_info_frame"].destroy()
        self.load_interview_history_frame()
