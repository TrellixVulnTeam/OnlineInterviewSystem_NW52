# coding=utf-8
# run.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/09
# description: run app(candidate client)
import time

file = open("./data/json/first_boot.txt", "r+")
is_first_boot = file.read()
if is_first_boot == "yes":
    import os
    os.system("python3 -m pip install flask requests")
    # base_path = os.getcwd()
    # print(base_path)
    # os.system("python -m pip install %s\other\PyAudio-0.2.11-cp37-cp37m-win_amd64.whl" % base_path)
    file.write("not any more")
    file.close()

from data.log import OISLog
from data.encryption import Encryption
from request import OISClientRequest
from user_manager import OISClientUserManager
# from tts import Tts
# from player import Player
import json

from main import OISCandidateClient
from tts import Tts
from player import Player


class BaseAbilities:

    def __init__(self):

        self.setting = json.load(open("./data/json/setting.json", "r", encoding="utf-8"))
        self.now_account = None
        self.account_token = None

        self.log = OISLog()
        self.encryption = Encryption()

        self.request = OISClientRequest(self)
        self.user_manager = OISClientUserManager(self)
        self.player = Player(self)
        self.tts = Tts(self)

        self.status = None
        self.interview_phase = ""

    def get_status(self):

        """
        获取当前状态
        :return:
        """
        interview_phase = self.get_interview_phase()
        self.interview_phase = interview_phase
        if interview_phase == 1:
            self.status = "第一批初级面试"
        elif interview_phase == 2:
            self.status = "第二批初级面试"

        self.status = self.status + "  终端号: %s " % self.setting["comCode"].replace("com", "")
        if self.setting["interviewMethod"] == 1:
            self.status = self.status + " 一对一面试"
        elif self.setting["interviewMethod"] == 2:
            self.status = self.status + " 群面"
        elif self.setting["interviewMethod"] == 3:
            self.status = self.status + "终极面试"

        self.status = self.status + " 单位: %s" % self.setting["bindEnterpriseCode"]

    def get_interview_phase(self):

        """
        获取当前为什么面试环节
        :return:
        """
        self.log.add_log("OIISCandidateClient: calculate what phase of interview is now", 1)

        arr = self.setting["interviewPhaseArrangement"]
        now_time = time.strftime("%H%M", time.localtime())

        for time_range in list(arr.keys()):
            a, b = time_range.split("-")[0], time_range.split("-")[1]
            if a < now_time < b:
                self.log.add_log("OIISCandidateClient: now phase: %s" % arr[time_range], 1)
                return arr[time_range]


if __name__ == "__main__":
    print("""
        ######################################
                 OIIS-CandidateClient
                   By Lanzhijiang
               lanzhijiang@foxmail.com
         2022-2022(c) all copyrights reserved
        ######################################
        """)
    ba = BaseAbilities()
    cc = OISCandidateClient(ba)
    cc.start()

