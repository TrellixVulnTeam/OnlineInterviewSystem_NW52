# coding=utf-8
# main.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/22
# description: class client main: ui+main_logic

import json
import time
from ws_client import WsClient


class OIISClassClient:
    """OIIS Class Client Main Class: ui windows and main logic"""
    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.user_manager = ba.user_manager
        self.request = ba.request
        self.tts = ba.tts
        self.player = ba.player

        self.called_list = json.load(open("./data/json/called_list.json", "r", encoding="utf-8"))

        self.ba.main = self
        self.ws_client = WsClient(ba)

    def start(self):

        """
        run app(open the window)
        :return:
        """
        self.log.add_log("OIISClassClient: start the OIIS Class Client now， using CLI INTERFACE", 1)
        self.tts.start("O2S Class Client启动中...")
        time.sleep(1.5)
        while True:
            self.tts.start("请输入账号")
            account = input("> 请输入账号(class1)：")
            self.tts.start("请输入密码")
            password = input("> 请输入密码：")
            res = self.user_manager.login(account, password)
            if res:
                print("> 登录成功！尝试创建Websocket连接到服务器")
                self.tts.start("登陆成功，尝试创建Websocket连接到服务器")
                break
            else:
                print("> 登录失败。请检查你的账号或者密码是否正确")
                self.tts.start("登录失败。请检查你的账号或者密码是否正确")
                time.sleep(1)

        self.log.add_log("OIISClassClient: login success, connect to server", 1)
        self.ws_client.connect_to_server()
        self.tts.start("连接服务器成功！开始！")
        for i in self.called_list:
            print(i)
        print(": 进入命令控制面板")
        while True:
            print("""
命令指引：
    0: 退出登录
    1: 再播放一遍刚刚播放过的内容

            """)
            command = input("> ")
            if command == "0":
                self.user_manager.logout()
                self.tts.start("再见！")
                break
            elif command == "1":
                self.player.say()

    def pre_call(self, call_list):

        """
        预叫号
        :param call_list: 呼叫列表
        :return:
        """
        self.log.add_log("OIISClassClient: do pre_call now", 1)

        self.tts.start("PRE CALL：预叫号。执行。")
        self.tts.start("请以下同学现在做好准备，5分钟左右之后会有正式叫号，正式叫号后再出发")

        self.real_call(call_list, "")

    def call(self, call_list):

        """
        正式叫号
        :param call_list: 呼叫列表
        :return:
        """
        self.log.add_log("OIISClassClient: do call now", 1)

        self.tts.start("FORMAL CALL：正式叫号。执行。")
        self.tts.start("请以下同学现在出发前往对应面试终端前进行面试！")

        self.real_call(call_list, "请现在出发")
        self.tts.start("再通知一遍")
        self.real_call(call_list, "请现在出发，现在出发")

    def final_call(self, call_list):

        """
        最后叫号
        :param call_list: 呼叫列表
        :return:
        """
        self.log.add_log("OIISClassClient: do pre_call now", 1)

        self.tts.start("FINAL CALL：最终叫号。执行。")
        self.tts.start("警告，警告。请以下同学在120秒内到达对应面试终端进行面试！！！")

        self.real_call(call_list, "马上出发！马上出发！")

    def result_publish(self, result_list):

        """
        发布结果
        :param result_list: 结果列表
        :return:
        """
        self.log.add_log("OIISClassClient: do result_publish now", 1)

        self.tts.start("RESULT PUBLISH：面试结果发布。执行。")
        self.tts.start("久等了~面试结果即将发布。恭喜以下的同学，通过了面试！")

        for i in range(0, len(result_list)):
            result_object = result_list[i]
            name, code, target_enterprise, target_job = result_object["name"], result_object["candidateCode"], result_object["enterpriseName"], result_object["jobName"]

            speech = "%s、%s同学，编号%s。恭喜你获得了在%s的%s工作机会！可喜可贺，可喜可贺！" % (i, name, code, target_enterprise, target_job)
            self.tts.start(speech)

    def real_call(self, call_list, adding):

        """
        叫号主部分（都大同小异了）
        :param call_list: 呼叫列表
        :param adding: 补充语句
        :return:
        """
        for i in range(0, len(call_list)):
            call_object = call_list[i]
            name, code, target_enterprise, target_com = call_object["name"], call_object["candidateCode"], \
                                                        call_object["appliedEnterprise"], \
                                                        int(call_object["comCode"].replace("com", ""))
            com_belonged_room = 0
            if 0 < target_com <= 64:
                com_belonged_room = 5
            elif 64 < target_com:
                com_belonged_room = 6
            speech = "%s、%s同学，编号%s。你面试的单位是%s。请尽快前往行政楼二楼%s号电脑室。%s" % (i, name, code, target_enterprise, com_belonged_room, adding)
            print(speech)
            self.called_list.append(speech)
            self.tts.start(speech)

        # add to local file
        json.dump(self.called_list, open("./data/json/called_list.json", "w", encoding="utf-8"))

    def announce(self, announce):

        """
        播放通知
        :param announce: 通知内容
        :return:
        """
        self.log.add_log("OIISClassClient: announce-%s" % announce, 1)
        self.tts.start(announce)
