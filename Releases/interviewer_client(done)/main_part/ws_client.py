# coding=utf-8
# ws_client.py
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/04/22
# description: websocket client
import ast
import socket
import threading
import time
from tkinter import *
from tkinter import ttk

import websockets
import asyncio


class WsClient:

    def __init__(self, ba):
        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        print("a")

        self.ws_url = self.setting["wsUrl"]
        self.ws_port = self.setting["wsPort"]
        self.ws = None
        self.wait_res_command = {}

        self.main = ba.main

    def send(self, string):

        """
        发送
        """
        self.ws.send(string.encode("utf-8"))

    def recv(self, length):

        """
        接收
        """
        return self.ws.recv(length).decode("utf-8")

    def connect_to_server(self):

        """
        连接到服务器
        :return:
        """
        self.log.add_log("WsClient: start connect to the ws-server-%s" % self.ws_url, 1)
        self.ws = socket.socket()
        self.ws.connect((self.ws_url, self.ws_port))

        # auth
        self.send("req:auth?account=%s&token=%s&userType=%s" % (self.ba.now_account, self.ba.account_token, self.setting["userType"]))
        recv = self.recv(1024)
        a = recv.split("?")
        command, param_raw = a[0], a[1]
        b = command.split(":")
        command_type, command = b[0], b[1]
        param = {}
        param_raw = param_raw.split("&")
        for i in param_raw:
            i_split = i.split("=")
            param[i_split[0]] = i_split[1]
        if command_type == "res":
            if param["code"] == "0":
                self.log.add_log("WsClient: auth success, websocket connection has established", 1)
                heartbeat_thread = threading.Thread(target=self.heartbeat_start, args=())
                heartbeat_thread.start()
                communicate_thread = threading.Thread(target=self.communicate, args=())
                communicate_thread.start()
            else:
                self.log.add_log("WsClient: auth not pass, fail to establish the connection", 3)

    def communicate(self):

        """
        開始交流（維持連接）
        :return
        """
        self.log.add_log("WsClient: start communicate with server-%s" % self.ws_url, 1)
        while True:
            # wait command
            recv = self.recv(1024)
            self.log.add_log("WsHandler: receive message from server, start handle", 1)
            # parse command
            try:
                a = recv.split("?")
                command, param_raw = a[0], a[1]
                b = command.split(":")
                command_type, command = b[0], b[1]
                param = {}
                param_raw = param_raw.split("&")
                try:
                    for i in param_raw:
                        i_split = i.split("=")
                        param[i_split[0]] = i_split[1]
                except IndexError:
                    self.log.add_log("WsHandler: param is empty", 1)
            except IndexError:
                self.send("res:res?code=1&msg=wrong format of request")
            else:
                self.last_heartbeat_time_stamp = self.log.get_time_stamp()
                if command_type == "req":
                    handle_func = self.recv_command
                elif command_type == "res":
                    handle_func = self.recv_response
                else:
                    a = "res:%s?code=1&msg=wrong format of request" % command
                    self.send(a)
                    return
                handle_thread = threading.Thread(target=handle_func, args=(command, param))
                handle_thread.start()

    def recv_command(self, command, param):

        """
        处理接受到的指令
        :param command: 指令
        :param param: 参数
        """
        self.log.add_log("WsClient: recv_command-%s" % command, 1)
        # command supported: pre_call call final_call result_publish
        if command == "heartbeat":
            self.send("res:heartbeat?code=0&msg=done")
        elif command == "candidate_online":
            self.main.event_candidate_online_handle(param["candidateCode"])
            self.send_response(command, {"code": 0, "msg": "success"})
        elif command == "candidate_offline":
            self.main.event_candidate_offline_handle()
            self.send_response(command, {"code": 0, "msg": "success"})
        elif command == "candidate_job_sat":
            self.main.event_candidate_job_sat_handle(param["appliedJobName"])
            self.send_response(command, {"code": 0, "msg": "success"})
        elif command == "final_end_interview":
            self.main.evnet_final_end_interview_handle()
            self.send_response(command, {"code": 0, "msg": "success"})

    def recv_response(self, command, response):

        """
        处理响应
        :param command: 响应的指令
        :param response: 返回
        """
        self.log.add_log("WsClient: recv_response-%s from server" % command, 1)
        try:
            self.wait_res_command[command](response)
        except KeyError:
            pass
            # normal handle
        else:
            self.log.add_log("WsClient: receive sent command-%s's response" % command, 1)
            if command == "heartbeat":
                if response["code"] == 0:
                    self.log.add_log("WsClient: heartbeat success", 0)

    def common_recv_response(self, response):

        """
        通用响应处理
        :param response: 响应
        """
        self.log.add_log("WsHandler: common_recv_response is now process response", 1)
        if response["code"] != "0":
            self.log.add_log("WsHandler: command execute not success, response is %s" % response["code"], 3)
        return

    def send_command(self, command, param, res_func=None):

        """
        发送指令
        :param command: 命令
        :param param: 参数
        :param res_func: 接受响应的函数
        :return
        """
        self.log.add_log("WsClient: send_command-%s to server" % command, 1)
        if res_func is None:
            res_func = self.common_recv_response

        param_str = ""
        for i in list(param.keys()):
            param_str = param_str + "%s=%s" % (i, param[i]) + "&"
        param_str = param_str[0:-1]

        send_str = "req:%s?%s" % (command, param_str)
        self.send(send_str)
        self.wait_res_command[command] = res_func

    def send_response(self, command, param):

        """
        发送响应
        :param command: 响应的指令
        :param param: 参数
        :return
        """
        self.log.add_log("WsClient: send_response for command-%s" % command, 1)
        param_str = ""
        for i in list(param.keys()):
            param_str = param_str + "%s=%s" % (i, param[i]) + "&"
        param_str = param_str[0:-1]

        send_str = "res:%s?%s" % (command, param_str)
        self.send(send_str)

    def heartbeat_start(self):

        """
        进行心跳
        :return
        """
        self.log.add_log("WsClient: start heartbeat now", 1)
        while True:
            self.send("req:heartbeat?")
            time.sleep(30)
