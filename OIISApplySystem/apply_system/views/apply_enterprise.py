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


class ApplyEnterpriseForm(forms.Form):
    enterprise_code = forms.CharField(label="单位编号",
                                      error_messages={"required": "单位编号不能为空！"})


class LoginForm(forms.Form):
    login_account = forms.CharField(label="登录账号",
                                    error_messages={"required": "账号不能为空！"})
    login_password = forms.CharField(label="登录密码",
                                     error_messages={"required": "密码不能为空！"})


class ApplyEnterprise:

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
                    return redirect("/apply_enterprise/")
                else:
                    return render(request, 'login.html', {"form": form})
            else:
                # not login, load login page
                return render(request, 'login.html', {"form": form})
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
                except IndexError:
                    return render(request, 'result.html', {"message": '登录失败！！！账号或密码错误。建议检验一下是否已经重置密码。如果实在无法解决，联系lanzhijiang@foxmail.com，详细描述情况'})
                if password == server_password:
                    # login success
                    self.mongodb.update_many_documents("candidate", account, {"_id": 7}, {"isOnline": True})

                    token = self.encryption.md5(str(int(time.time())) + account)
                    last_login_time_stamp = str(int(time.time()))

                    self.mongodb.update_many_documents("candidate", account, {"_id": 6}, {"lastLoginTimeStamp": last_login_time_stamp})
                    self.mongodb.update_many_documents("candidate", account, {"_id": 5}, {"token": token})

                    rep = redirect("/apply_enterprise/")
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

    def handle_logout_request(self, request):

        """
        处理登出请求 /logout
        :param request:
        :return:
        """
        is_login = request.COOKIES.get("is_login")
        if is_login:
            account_login = request.COOKIES.get("account")
            rep = redirect("/")
            rep.delete_cookie("is_login")
            rep.delete_cookie("account")
            rep.delete_cookie("token")

            self.mongodb.update_many_documents("candidate", account_login, {"_id": 5}, {"token": None})
            self.mongodb.update_many_documents("candidate", account_login, {"_id": 7}, {"isOnline": False})
            return rep
        else:
            return render(request, 'result.html', {"message": "错误！你还没有登录！"})

    def logout(self, account):

        """
        登出
        :return:
        """
        self.mongodb.update_many_documents("candidate", account, {"_id": 5}, {"token": None})
        self.mongodb.update_many_documents("candidate", account, {"_id": 7}, {"isOnline": False})

    def handle_apply_enterprise_request(self, request):

        """
        处理报名单位的请求 /apply_enterprise
        :return:
        """
        if request.method == "GET":
            # 则是请求页面

            utc_time = time.strftime("%d-%H-%M", time.gmtime(time.time())).split("-")
            now_time = [int(utc_time[0]), int(utc_time[1])+8, int(utc_time[2])]
            # msg = "终极报名已经开始！可以填报了！"
            # return render(request, 'apply_enterprise.html', {"message": msg, "apply_result": "还没有提交", "form": ApplyEnterpriseForm()})
            if now_time[0] <= 1 and now_time[1] >= 9 and now_time[1] >= 00:
                # it is the time
                msg = "终极报名进行中..."
                a_e_form = ApplyEnterpriseForm()
                return render(request, 'apply_enterprise.html', {"message": msg, "apply_result": "等待提交", "form": a_e_form})
            else:
                # it is not the time
                msg = "系统已经关闭！"
                return render(request, 'result.html', {"message": msg})
        else:
            # 则是提交表单
            a_e_form = ApplyEnterpriseForm(request.POST)
            if a_e_form.is_valid():

                account = request.COOKIES.get("account")
                token = request.COOKIES.get("token")
                print("---------- receive apply from %s ----------" % account)
                if account is None or account == "":
                    return render(request, 'apply_enterprise.html', {"apply_result": "你还没有登录！！！回首页登录", "form": a_e_form})
                token_on_server = self.mongodb.parse_document_result(self.mongodb.get_document("candidate", account, {"_id": 5}, 1),
                                                                     ["token"])[0]["token"]  # get token
                if token == token_on_server:
                    # server say your token is correct, allowed to make apply
                    # update candidate-applied interview-apply-enterprise memcache-desc
                    applied_enterprise_order = a_e_form.cleaned_data["enterprise_code"]
                    applied_enterprise_order = int(applied_enterprise_order)
                    empty_enterprise_code = [59, 60, 61, 70, 81, 82]
                    if applied_enterprise_order in empty_enterprise_code or applied_enterprise_order > 111:
                        a_e_form = ApplyEnterpriseForm()
                        return render(request, 'apply_enterprise.html', {"apply_result": "错误的/不可用的单位编号", "form": a_e_form})

                    now_remained = self.mongodb.parse_document_result(
                        self.mongodb.get_document("interview", "temp", {"_id": applied_enterprise_order}, 1),
                        ["data"])[0]["data"]
                    print("---------- %s remain: %s ----------" % (applied_enterprise_order, now_remained))
                    if type(now_remained) == int:
                        if now_remained > 0:
                            # able to apply
                            # 先占据数据库，后面不行再返还
                            self.mongodb.update_many_documents("interview", "temp", {"_id": applied_enterprise_order}, {"data": now_remained-1})
                            # 从个人的角度校验是否已经申报过了
                            applied_enterprise_server = self.mongodb.parse_document_result(self.mongodb.get_document("candidate", account, {"_id": 8}, 1),
                                                                                           ["appliedEnterprise"])[0]["appliedEnterprise"]

                            # if applied_enterprise_server == "0" or applied_enterprise_server == 0:
                            # 没有申报过（个人角度）
                            # 从企业角度校验是否已经申报过了
                            enterprise_applied = self.mongodb.parse_document_result(
                                self.mongodb.get_document("interview", "apply", {"_id": applied_enterprise_order}, 1),
                                ["applied"])[0]["applied"]
                            #
                            # if account not in enterprise_applied:
                            #     enterprise_applied.append(account)
                            # else:
                            #     print("---------- fail to apply, already have one, from enterprise_perspective ----------")
                            #     # self.memcache.increase(applied_enterprise_order)
                            #     a = self.mongodb.parse_document_result(
                            #         self.mongodb.get_document("interview", "temp",
                            #                                   {"id_": applied_enterprise_order}, 1),
                            #         ["data"])[0]["data"]
                            #     self.mongodb.update_many_documents("interview", "temp", {"_id": applied_enterprise_order}, {"data": a+1})
                            #     return render(request, 'apply_enterprise.html', {"apply_result": "错误码：al_2。您已经申报过一次了，不能再进行申报", "form": a_e_form})

                            # 更新candidate数据库
                            self.mongodb.update_many_documents("candidate", account, {"_id": 8}, {"appliedEnterprise": applied_enterprise_order})
                            # 删除原有interview-apply数据
                            raw_applied_data = self.mongodb.parse_document_result(
                                self.mongodb.get_document("interview", "apply", {"_id": applied_enterprise_server}, 1),
                                ["applied"])[0]["applied"]
                            try:
                                raw_applied_data.remove(account)
                            except ValueError:
                                pass
                            old_apply_remained = self.mongodb.parse_document_result(
                                self.mongodb.get_document("interview", "temp", {"_id": applied_enterprise_server}, 1),
                                ["data"])[0]["data"]
                            self.mongodb.update_many_documents("interview", "temp", {"_id": applied_enterprise_order},
                                                               {"data": old_apply_remained + 1})
                            self.mongodb.update_many_documents("interview", "apply", {"_id": applied_enterprise_server}, {"applied": raw_applied_data})
                            # 更新interview-apply数据库
                            enterprise_applied.append(account)
                            self.mongodb.update_many_documents("interview", "apply", {"_id": applied_enterprise_order}, {"applied": enterprise_applied})

                            # 更新全局状态
                            whole_status = self.mongodb.parse_document_result(
                                self.mongodb.get_document("interview", "temp", {"_id": 0}, 1),
                                ["whole_status"])[0]["whole_status"]
                            whole_status[applied_enterprise_order] -= 1
                            self.mongodb.update_many_documents("interview", "temp", {"_id": 0}, {"whole_status": whole_status})
                            print("---------- apply success, %s applied %s ----------" % (account, applied_enterprise_order))

                            self.logout(account)
                            return render(request, "final_page.html", {"message": "恭喜您，%s。您申报的单位-%s成功通过！" % (account, applied_enterprise_order)})
                        # else:
                        #     print("---------- fail to apply, already have one, from personnal_perspective ----------")
                        #     # self.memcache.increase(applied_enterprise_order)
                        #     newest_remained = self.mongodb.parse_document_result(
                        #         self.mongodb.get_document("interview", "temp", {"_id": applied_enterprise_order}, 1),
                        #                                   ["data"])[0]["data"]
                        #     self.mongodb.update_many_documents("interview", "temp",
                        #                                        {"_id": applied_enterprise_order},
                        #                                        {"data": newest_remained + 1})
                        #     a_e_form = ApplyEnterpriseForm()
                        #     return render(request, 'apply_enterprise.html', {"apply_result": "错误码：al_1。您已经申报过一次了，不能再进行申报", "form": a_e_form})
                        else:
                            # unable to apply
                            print("---------- fail to apply, sold out ----------")
                            # self.memcache.increase(applied_enterprise_order)
                            a = self.mongodb.parse_document_result(
                                self.mongodb.get_document("interview", "temp",
                                                          {"_id": applied_enterprise_order}, 1),
                                ["data"])[0]["data"]
                            self.mongodb.update_many_documents("interview", "temp",
                                                               {"_id": applied_enterprise_order}, {"data": a + 1})
                            a_e_form = ApplyEnterpriseForm()
                            return render(request, 'apply_enterprise.html', {"apply_result": "遗憾！%s的单位名额剩余为0或者该单位不存在，请另外选择" % applied_enterprise_order, "form": a_e_form})
                    else:
                        # unable to apply
                        print("---------- fail to apply, sold out or not exist ----------")
                        a_e_form = ApplyEnterpriseForm()
                        return render(request, 'apply_enterprise.html',
                                      {"apply_result": "遗憾！%s的单位名额剩余为0，请另外选择" % applied_enterprise_order, "form": a_e_form})
                else:
                    print("---------- wrong token ----------")
                    a_e_form = ApplyEnterpriseForm()
                    return render(request, 'apply_enterprise.html', {"apply_result": "token不正确，请重新登录", "form": a_e_form})
            else:
                print("---------- invalid data ----------")
                a_e_form = ApplyEnterpriseForm()
                return render(request, 'apply_enterprise.html', {"apply_result": "无效的数据", "form": a_e_form})

    def get_remained_info(self):

        """
        获取剩余名额信息
        :return:
        """
        # remained_info = self.memcache.get("whole_status")
        remained_info = self.mongodb.parse_document_result(self.mongodb.get_document("interview", "temp", {"_id": 0}, 1),
                                                           ["whole_status"])[0]["whole_status"]
        if remained_info is None:
            return "<p>数据库出现错误，无法正常加载数据，请稍后重试</p>"

        empty_enterprise_code = [59, 60, 61, 70, 81, 82]
        data = []
        now_fill_code_id = 1
        now_fill_code_remained = 1
        for column in range(0, 12):
            column += 1
            data.append([])
            fill_remained = False
            fill_id = False
            if column % 2 == 0:
                # 填写名额的
                fill_remained = True
            else:
                # 填写单位编号的
                fill_id = True
            for row in range(0, 19):
                if fill_id:
                    try:
                        data[column - 1].append(now_fill_code_id)
                        now_fill_code_id += 1
                    except IndexError:
                        data[column - 1].append("单位不存在")
                        now_fill_code_id += 1
                elif fill_remained:
                    # print(now_fill_code_remained, remained_info[now_fill_code_remained])
                    if now_fill_code_remained in empty_enterprise_code:
                        data[column - 1].append(0)
                        now_fill_code_remained += 1
                    else:
                        try:
                            value = remained_info[now_fill_code_remained]
                            data[column - 1].append(value)
                            now_fill_code_remained += 1
                        except IndexError:
                            data[column - 1].append(0)
                            now_fill_code_remained += 1

        row_blocks = """
        <tr><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th><th>编号</th><th>剩余名额</th></tr>
        """
        for row in range(0, 19):
            column_blocks = ""
            for c_i in range(0, 12):
                column = data[c_i]
                if c_i % 2 == 0:
                    column_blocks = column_blocks + "<td><b>%s</b></td>" % column[row]
                else:
                    if 4 < column[row] <= 8:
                        color = "red"
                    elif column[row] <= 4:
                        color = "darkred"
                    elif 8 < column[row] <= 14:
                        color = "lightblue"
                    else:
                        color = "lightgreen"
                    column_blocks = column_blocks + "<td><font color='%s'>%s</font></td>" % (color, column[row])

            row_blocks = row_blocks + "<tr>" + column_blocks + "</tr>"

        return row_blocks

    def handle_get_remained_info_request(self, request):

        """
        处理获取剩余名额信息的请求
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
                remained_info = self.get_remained_info()
                return HttpResponse(remained_info)
            else:
                return HttpResponse("permission denied")
        else:
            return HttpResponse("wrong request method")
