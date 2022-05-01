# coding=utf-8
# author: Lan_zhijiang
# description: backend init
# date: 2022/4/9
import time

from database.mongodb import MongoDBManipulator
from data.encryption import Encryption
from data.log import OISLog
from core.main import OIISBackendMain

from api.http.server import HttpServer
from api.ws.server import WsServer

import json
import threading
import schedule


class BaseAbilities:
    """基础能力：log，MongoDB、MemcachedDB传递"""
    def __init__(self):

        self.log = OISLog()
        self.setting = json.load(open("./data/json/setting.json", "r", encoding="utf-8"))

        self.ws_conn_list = {
            "interviewer": {},
            "class": {},
            "other": {},
            "waiting_room": {},
            "a_client": {}
        }
        self.lost_conn_list = {
            "interviewer": [],
            "class": [],
            "a_client": [],
            "waiting_room": []
        }

        self.mongodb_manipulator = MongoDBManipulator(self.log, self.setting)
        self.encryption = Encryption()

        self.main = OIISBackendMain(self)

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


class BackendInit:

    def __init__(self):

        self.base_abilities = BaseAbilities()

        self.log = self.base_abilities.log

        self.http_server = HttpServer(self.base_abilities)
        self.ws_server = WsServer(self.base_abilities)

    def schedule_jobs(self):

        """
        预定任务
        7:55 pre_call(init)
        8:00 call(init)
        :return
        """
        self.base_abilities.log.add_log("OIISBackendMain: start schedule jobs", 1)

        while True:
            schedule.run_pending()
            time.sleep(5)

    def run_backend(self):

        """
        启动后端
        :return
        """
        self.base_abilities.log.add_log("######## NL-BACKEND RUN NOW ########", 1)
        self.base_abilities.log.add_log("BackendInit: now start backend", 1)

        http_thread = threading.Thread(target=self.http_server.run_server, args=())
        # ws_thread = threading.Thread(target=self.ws_server.run_server, args=())
        schedule_thread = threading.Thread(target=self.schedule_jobs, args=())
        http_thread.start()
        # schedule_thread.start()  # no schedule
        # ws_thread.start()
        self.ws_server.run_server()
