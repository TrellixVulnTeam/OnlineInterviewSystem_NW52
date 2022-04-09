# coding=utf-8
# author: Lan_zhijiang
# description: backend init
# date: 2022/4/9

from database.mongodb import MongoDBManipulator
from database.memcached import MemcachedManipulator
from data.encryption import Encryption
from data.log import OISLog

from api.http.server import HttpServer

import json


class BaseAbilities:
    """基础能力：log，MongoDB、MemcachedDB传递"""
    def __init__(self):

        self.log = OISLog()
        self.setting = json.load(open("./data/json/setting.json", "r", encoding="utf-8"))

        self.mongodb_manipulator = MongoDBManipulator(self.log, self.setting)
        self.memcached_manipulator = MemcachedManipulator(self.log, self.setting)
        self.encryption = Encryption()


class BackendInit:

    def __init__(self):

        self.base_abilities = BaseAbilities()

        self.http_server = HttpServer(self.base_abilities)

    def run_backend(self):

        """
        启动后端
        :return
        """
        self.base_abilities.log.add_log("######## NL-BACKEND RUN NOW ########", 1)
        self.base_abilities.log.add_log("BackendInit: now start backend", 1)

        self.http_server.run_server()
