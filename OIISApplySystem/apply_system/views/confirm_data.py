# author: Lanzhijiang
import json

from django.shortcuts import render, redirect, HttpResponse
from django import forms
from django.core.exceptions import ValidationError
import json
import time
from datetime import timezone

from apply_system.views.encryption import Encryption
from apply_system.database.mongodb import MongoDBManipulator
from apply_system.database.memcached import MemcachedManipulator


class LoginForm(forms.Form):
    login_account = forms.CharField(label="登录账号",
                                    error_messages={"required": "账号不能为空！"})
    login_password = forms.CharField(label="登录密码",
                                     error_messages={"required": "密码不能为空！"})


class ConfirmData:

    def __init__(self):

        self.setting = json.load(open(r"./apply_system/data/json/setting.json", "r", encoding="utf-8"))

        self.encryption = Encryption()
        self.mongodb = MongoDBManipulator(self.setting["database"]["mongodb"]["addr"],
                                          self.setting["database"]["mongodb"]["port"],
                                          self.setting["database"]["mongodb"]["auth"][0],
                                          self.setting["database"]["mongodb"]["auth"][1])

        self.memcache = MemcachedManipulator(self.setting["database"]["memcached"]["addr"],
                                             self.setting["database"]["memcached"]["port"])

    def handle_login_request(self, request):

        """
        处理登录请求 /login
        :return:
        """
        form = LoginForm()
        if request.method == "GET":
            is_login = request.COOKIES.get('is_login')
            if is_login:
                # has logged in, verify login info
                account = request.COOKIES.get("account")
                token = request.COOKIES.get("token")
                token_on_server = self.mongodb.parse_document_result(
                    self.mongodb.get_document("candidate", account, {"_id": 5}, 1),
                    ["token"])[0]["token"]  # get token
                is_login_on_server = self.mongodb.parse_document_result(
                    self.mongodb.get_document("candidate", account, {"_id": 7}, 1),
                    ["isOnline"])[0]["isOnline"]  # get isOnline
                if token == token_on_server and is_login_on_server:
                    # server say you logged in and token correct
                    return True
                else:
                    return render(request, 'c_d_login.html', {"form": form})
            else:
                # not login, load login page
                return render(request, 'c_d_login.html', {"form": form})
        else:
            # 进行登录请求
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                account, password = login_form.cleaned_data["login_account"], login_form.cleaned_data["login_password"]
                password = self.encryption.md5(self.encryption.md5(password))

                print("---------- %s try to login -----------" % account)
                try:
                    server_password = self.mongodb.parse_document_result(self.mongodb.get_document("candidate", account, {"_id": 1}, 1),
                                                                         ["password"])[0]["password"]
                except (KeyError, IndexError):
                    return render(request, 'result.html', {"message": '登录失败！！！账号或密码错误。建议检验一下是否已经重置密码。如果实在无法解决，联系lanzhijiang@foxmail.com，详细描述情况'})
                if password == server_password:
                    # login success
                    print("---------- %s login success -----------" % account)
                    self.mongodb.update_many_documents("candidate", account, {"_id": 7}, {"isOnline": True})

                    token = self.encryption.md5(str(int(time.time())) + account)
                    last_login_time_stamp = str(int(time.time()))

                    self.mongodb.update_many_documents("candidate", account, {"_id": 6}, {"lastLoginTimeStamp": last_login_time_stamp})
                    self.mongodb.update_many_documents("candidate", account, {"_id": 5}, {"token": token})

                    rep = redirect("/confirm_data/")
                    rep.set_cookie("account", account)
                    rep.set_cookie("token", token)
                    rep.set_cookie("is_login", True)
                    return rep
                else:
                    print("---------- %s login failed -----------" % account)
                    return render(request, 'result.html', {"message": '登录失败！！！账号或者密码错误。建议检验一下是否已经重置密码。如果实在无法解决，联系lanzhijiang@foxmail.com，详细描述情况'})
            else:
                print("---------- login failed, wrong data -----------")
                raise ValidationError("错误的数据！")

    def handle_confirm_data_request(self, request):

        """
        处理确认信息的请求 /confirm_data
        :return:
        """
        if request.method == "GET":
            # 则是请求页面
            msg = "快,快确认吧"
            is_login = request.COOKIES.get('is_login')
            if not is_login:
                l = self.handle_login_request(request)
                if l is True:
                    return render(request, 'confirm_data.html', {"message": msg})
                else:
                    return l
            else:
                return render(request, 'confirm_data.html', {"message": msg})
        else:
            return self.handle_login_request(request)

    def get_confirm_data(self, class_name):

        """
        获取确认信息
        :return:
        """
        confirm_info = []
        # load confirm info from database
        class_1 = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        class_2 = [7, 8, 9, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
        if int(class_name) in class_1:
            p = "1"
        else:
            p = "2"

        for log in range(1, 60):
            if len(str(log)) == 1:
                log_str = "0%s" % str(log)
            else:
                log_str = str(log)

            code = class_name + log_str + p
            try:
                info = self.mongodb.parse_document_result(
                    self.mongodb.get_document("interview", "confirming", {"_id": code}, 1),
                    ["_id", "name", "class", "appliedEnterprise"]
                )
                info = info[0]
            except IndexError:
                continue

            if info["appliedEnterprise"] is None:
                info["appliedEnterprise"] = "<font color='red'>无</font>"
            else:
                info["appliedEnterprise"] = "<font color='lightgreen'>%s</font>" % info["appliedEnterprise"]
            confirm_info.append(info)

        if not confirm_info:
            return "<p>数据库出现错误，无法正常加载数据，请稍后重试</p>"

        # convert info to sheet
        data = [[], [], [], [], [], [], [], []]
        keys_mapping = ["name", "_id", "class", "appliedEnterprise"]
        for i in confirm_info:
            for c_i in range(0, 4):
                data[c_i].append(i[keys_mapping[c_i]])

        row_blocks = """
        <tr><th>姓名</th><th>个人编号</th><th>班级</th><th>应聘单位</th>
        """

        for row in range(0, 60):
            column_blocks = ""
            for c_i in range(0, 4):
                column = data[c_i]
                try:
                    if c_i == 0:
                        column_blocks = column_blocks + "<td><b>%s</b></td>" % column[row]
                    else:
                        column_blocks = column_blocks + "<td>%s</td>" % column[row]
                except IndexError:
                    continue

            row_blocks = row_blocks + "<tr>" + column_blocks + "</tr>"

        return row_blocks

    def handle_get_confirm_data_request(self, request):

        """
        处理获取个人信息列表的请求
        :param request:
        :return:
        """
        if request.method == "GET":
            account = request.GET.get("account")
            token = request.GET.get("token")
            token_on_server = self.mongodb.parse_document_result(
                self.mongodb.get_document("candidate", account, {"_id": 5}, 1),
                ["token"])[0]["token"]  # get token
            if token == token_on_server:
                # server say you logged in and token correct
                class_name = account[0:2]
                remained_info = self.get_confirm_data(class_name)
                return HttpResponse(remained_info)
            else:
                return HttpResponse("permission denied")
        else:
            return HttpResponse("wrong request method")
