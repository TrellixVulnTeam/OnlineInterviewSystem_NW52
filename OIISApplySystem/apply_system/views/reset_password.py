# desc: the view file of func:reset_password
# author: Lanzhijiang
import json
import time

from django.shortcuts import render
from django import forms
from django.shortcuts import redirect
from django.core.exceptions import ValidationError

from apply_system.views.encryption import Encryption
from apply_system.database.mongodb import MongoDBManipulator
from apply_system.database.memcached import MemcachedManipulator


class RPForm(forms.Form):

    account = forms.CharField(label="账号",
                              error_messages={"required": "账号不能为空！"})
    new_password = forms.CharField(label="新密码",
                                   error_messages={"required": "密码不能为空！"})
    repeat_password = forms.CharField(label="重复密码")


class ResetPassword:

    def __init__(self):

        self.setting = json.load(open(r"./apply_system/data/json/setting.json", "r", encoding="utf-8"))

        self.encryption = Encryption()
        self.mongodb = MongoDBManipulator(self.setting["database"]["mongodb"]["addr"],
                                          self.setting["database"]["mongodb"]["port"],
                                          self.setting["database"]["mongodb"]["auth"][0],
                                          self.setting["database"]["mongodb"]["auth"][1])

        self.memcache = MemcachedManipulator(self.setting["database"]["memcached"]["addr"],
                                             self.setting["database"]["memcached"]["port"])

    def reset(self, account, new_password, repeat_password):

        """
        重置密码
        :param account
        :param new_password:
        :param repeat_password:
        :return:
        """
        if new_password == "" or new_password is None:
            return False
        new_password, repeat_password = self.encryption.md5(new_password), self.encryption.md5(repeat_password)
        if self.mongodb.is_collection_exist("candidate", account):
            # 账户存在
            resat_users = self.memcache.get("resat_users")
            if account not in resat_users:
                password = self.encryption.md5(new_password)
                if self.mongodb.update_many_documents("candidate", account, {"_id": 1}, {"password": password}):
                    resat_users.append(account)
                    self.memcache.set("resat_users", resat_users)
                    return True
                else:
                    return False
            else:
                return False
        else:
            if len(account) == 5:
                if account.isdigit():
                    class_ = account[0:2]
                    code = account[2:4]
                    class_1 = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18]
                    class_2 = [7, 8, 9, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
                    if int(class_) in class_1:
                        p = 1
                    elif int(class_) in class_2:
                        p = 2
                    else:
                        return False

                    user_info_tem = [
                        {"_id": 0, "account": ""},
                        {"_id": 1, "password": ""},
                        {"_id": 2, "class": ""},
                        {"_id": 3, "userType": "candidate"},
                        {"_id": 4, "nickname": ""},
                        {"_id": 5, "token": None},
                        {"_id": 6, "lastLoginTimeStamp": None},
                        {"_id": 7, "isOnline": False},
                        {"_id": 8, "appliedEnterprise": 0},
                        {"_id": 9, "interviewInfo": {}}
                    ]
                    f_code = class_+code+str(p)
                    user_info_tem[0]["account"] = f_code
                    self.mongodb.add_many_documents("candidate", f_code, user_info_tem)
                    password = self.encryption.md5(new_password)
                    if self.mongodb.update_many_documents("candidate", account, {"_id": 1}, {"password": password}):
                        resat_users = self.memcache.get("resat_users")
                        resat_users.append(account)
                        self.memcache.set("resat_users", resat_users)

                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False

    def handle_request(self, request):

        """
        加载页面
        :param request:
        :return:
        """
        if request.method == "GET":
            # utc_time = time.strftime("%d-%H-%M", time.gmtime(time.time())).split("-")
            # now_time = [int(utc_time[0]), int(utc_time[1]) + 8, int(utc_time[2])]
            # print(now_time)
            # if now_time[0] >= 16 and now_time[1] >= 21 and now_time[1] >= 00:
            #     # it is the time to close
            #     msg = "「重置密码」已经下线！20:15可以登录终极报名系统，21:00时终极报名正式开始"
            #     return render(request, 'result.html', {"message": msg})
            # else:
            # it is not the time to close
            context = {
                "form": RPForm()
            }
            return render(request, 'reset_password.html', context)
        else:
            form = RPForm(request.POST)
            if form.is_valid():
                account, new_password, repeat_password = form.cleaned_data["account"], form.cleaned_data["new_password"], form.cleaned_data["repeat_password"]
                if new_password == repeat_password:
                    if self.reset(account, new_password, repeat_password):
                        # 重置成功
                        print("%s reset password success" % account)
                        return render(request, "result.html", {"message": "成功"})
                    else:
                        print("%s reset password fail" % account)
                        return render(request, "result.html", {"message": "失败。请确认提交的账号正确。且这不是你第二次进行重置。如果重复发生错误，请上报：lanzhijiang@foxmail.com"})
                else:
                    print("%s reset password fail" % account)
                    return render(request, "result.html", {"message": "请确认密码和重复密码一致"})
            else:
                errors = form.errors
                return render(request, "result.html", {"message": "失败。%s" % str(errors)})

