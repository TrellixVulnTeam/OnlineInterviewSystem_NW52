# coding=utf-8
# main.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/27
# description: waiting room client main: ui+main_logic
import json
import threading
from tkinter import *
from tkinter import ttk
import time

from ws_client import WsClient


class OISWaitingRoomClient:
    """OIS Waiting Room Client Main Class: ui windows and main logic"""
    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.request = ba.request
        # self.tts = ba.tts
        self.ba.main = self

        self.main_window = Tk(className="(*^▽^*) OIIS")
        self.main_window.title("OIIS WRC")
        self.main_window.maxsize(900, 900)

        self.main_frame_set = {}
        self.interview_info_frame_set = {}

        self.status = ba.status
        self.interview_phase = ba.interview_phase

        self.waiting_status = None
        self.next_candidate = None
        self.called_list = json.load(open("./data/json/called_list.json", "r", encoding="utf-8"))

        self.ws_client = WsClient(ba)

    def start(self):

        """
        run app(open the window)
        :return:
        """
        self.log.add_log("OIISWaitingRoomClient: start the OIIS Waiting Room Client now", 1)

        self.ba.get_status()
        self.status = self.ba.status
        self.load_main_frame()

        self.ws_client.connect_to_server()

        self.main_window.mainloop()

    def load_main_frame(self):

        """
        加载主页面
        :return:
        """
        self.log.add_log("OIISWaitingRoomClient: load main frame...", 1)

        self.main_frame_set["frame"] = ttk.Frame(self.main_window, padding="8")
        self.main_frame_set["frame"].grid()

        self.main_frame_set["title"] = ttk.Label(self.main_frame_set["frame"], text="OIIS等候室端 主界面", background="lightblue", anchor=CENTER)
        self.main_frame_set["title"].grid(column=1, row=1)

        self.main_frame_set["status"] = ttk.Label(self.main_frame_set["frame"], text=self.status, foreground="yellow", background="red", anchor=CENTER)
        self.main_frame_set["status"].grid(column=1, row=2)

        self.main_frame_set["notice_textvar"] = StringVar()
        self.main_frame_set["notice_textvar"].set("加载中...")
        self.main_frame_set["notice"] = ttk.Label(self.main_frame_set["frame"], textvariable=self.main_frame_set["notice_textvar"], anchor=CENTER, foreground="red")
        self.main_frame_set["notice"].grid(column=1, row=3)

        self.main_frame_set["enterprise_id_entry"] = ttk.Entry(self.main_frame_set["frame"])
        self.main_frame_set["enterprise_id_entry"].grid(column=1, row=4)

        self.main_frame_set["init_calling"] = ttk.Button(self.main_frame_set["frame"], text="初始化叫号",
                                                         command=self.button_init_waiting)
        self.main_frame_set["init_calling"].grid(column=1, row=5)

        self.main_frame_set["start_waiting_button"] = ttk.Button(self.main_frame_set["frame"], text="开始等待",
                                                                 command=self.button_start_waiting_handle)
        self.main_frame_set["start_waiting_button"].grid(column=1, row=6)

        self.main_frame_set["end_waiting_button"] = ttk.Button(self.main_frame_set["frame"], text="结束等待",
                                                               command=self.button_end_waiting_handle)
        self.main_frame_set["end_waiting_button"].grid(column=1, row=7)

        self.main_frame_set["calledListBox"] = Listbox(self.main_frame_set["frame"])
        for i in self.called_list:
            self.main_frame_set["calledListBox"].insert(END, i)
        self.main_frame_set["calledListBox"].grid(column=1, rowspan=5)

        self.main_frame_set["author"] = ttk.Label(self.main_frame_set["frame"], text="Developed By Lanzhijiang", anchor=CENTER, foreground="white", background="lightblue")
        self.main_frame_set["author"].grid(column=1, row=15)

        self.main_frame_set["notice_textvar"].set("说明：请来到后点击'开始等待'；离开时点击'结束等待'")

    def button_start_waiting_handle(self):

        """
        响应开始等待按钮
        :return:
        """
        self.log.add_log("OIISWaitingRoomClient: start_waiting was pressed, start handle", 1)

        enterprise_id = self.main_frame_set["enterprise_id_entry"].get()
        if enterprise_id is None or enterprise_id == "":
            self.main_frame_set["notice_textvar"].set("未填写单位编号")
            return

        self.ws_client.send_command("start_waiting", {"comCode": "com%s" % enterprise_id, "candidateCode": self.next_candidate})
        self.main_frame_set["notice_textvar"].set("上报成功：start_waiting-%s" % enterprise_id)

        self.waiting_status = "in_waiting"

    def button_end_waiting_handle(self):

        """
        响应结束等待按钮
        :return:
        """
        self.log.add_log("OIISWaitingRoomClient: end_waiting was pressed, start handle", 1)

        enterprise_id = self.main_frame_set["enterprise_id_entry"].get()
        if enterprise_id is None or enterprise_id == "":
            self.main_frame_set["notice_textvar"].set("未填写单位编号")
            return

        self.waiting_status = "wait_for_next_to_come"
        self.ws_client.send_command("end_waiting", {"comCode": "com%s" % enterprise_id, "candidateCode": self.next_candidate})
        self.main_frame_set["notice_textvar"].set("上报成功：end_waiting-%s" % enterprise_id)

        overtime_count = threading.Thread(target=self.count_for_overtime, args=())
        overtime_count.start()

    def button_init_waiting(self):

        """
        按钮-初始化等待
        :return:
        """
        self.log.add_log("OIISWaitingRoomClient: init waiting", 1)
        enterprise_id = self.main_frame_set["enterprise_id_entry"].get()
        if enterprise_id is None or enterprise_id == "":
            self.main_frame_set["notice_textvar"].set("未填写单位编号")
            return
        self.ws_client.send_command("init_waiting", {"comCode": "com%s" % enterprise_id})

    def refresh_called_list(self):

        """
        刷新called_list
        :return:
        """
        self.log.add_log("OIISWaitingRoomClient: refresh the called list", 1)
        self.called_list.append("com%s %s" % (self.main_frame_set["enterprise_id_entry"].get(), self.next_candidate))
        self.main_frame_set["calledListBox"].insert(0, self.called_list[-1])
        json.dump(self.called_list, open("./data/json/called_list.json", "w", encoding="utf-8"))

    def event_skip_handle(self, next_candidate):

        """
        跳过当前等待的面试者
        :param next_candidate: 下一位面试者编号
        :return:
        """
        self.log.add_log("OIISWaitingRoomClient: skip the wait_for_come candidate")
        self.main_frame_set["notice_textvar"].set("事件：跳过 下一位：%s" % next_candidate)
        self.next_candidate = next_candidate
        self.refresh_called_list()

    def count_for_overtime(self):

        """
        开始计时(叫号超时)
        :return:
        """
        self.log.add_log("OIISWaitingRoomClient: wait for next candidate come to start waiting", 1)

        time.sleep(150)
        if self.waiting_status == "wait_for_next_to_come":
            self.ws_client.send_command("overtime_for_next_to_come", {"comCode": self.setting["comCode"], "candidateCode": self.next_candidate})
            # 屏幕红黄闪烁五次
            for i in range(0, 5):
                self.main_window.configure(background="yellow")
                time.sleep(1)
                self.main_window.configure(background="red")
        else:
            return

