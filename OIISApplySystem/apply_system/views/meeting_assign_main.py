from django.shortcuts import render, redirect
from django import forms
from django.http import HttpResponseRedirect
import json
from apply_system.database.mongodb import MongoDBManipulator


class ApplyEnterpriseForm(forms.Form):
    enterprise_id = forms.CharField(label="单位编号",
                                    error_messages={"required": "单位编号不能为空！"})


class MeetingAssignMain:

    def __init__(self):

        self.setting = json.load(open(r"./apply_system/data/json/setting.json", "r", encoding="utf-8"))

        self.mongodb = MongoDBManipulator(self.setting["database"]["mongodb"]["addr"],
                                          self.setting["database"]["mongodb"]["port"],
                                          self.setting["database"]["mongodb"]["auth"][0],
                                          self.setting["database"]["mongodb"]["auth"][1])

    def handle_request(self, request):

        """
        处理请求
            返回一个render meeting_assign.html 输入其编号，然后查找并跳转
        """
        if request.method == "GET":
            # 返回render
            a_e_form = ApplyEnterpriseForm()
            return render(request, 'meeting_assign.html', {"msg": "", "form": a_e_form})
        else:
            # 返回redirect
            a_e_form = ApplyEnterpriseForm(request.POST)
            if a_e_form.is_valid():
                e_i = a_e_form.cleaned_data["enterprise_id"]
                a = self.mongodb.parse_document_result(
                    self.mongodb.get_document("interview", "now", {"_id": "com%s" % e_i}, 1),
                    ["meetingPlatform", "meetingUrlList", "status"]
                )[0]

                target = a["meetingUrlList"][a["meetingPlatform"]]
                if target == "" or target is None:
                    target = a["meetingUrlList"]["jitsi"]
                print("  now using %s, redirect to %s " % (a["meetingPlatform"], target))
                if a["status"] == "one_online":
                    status = "both_online"
                else:
                    status = "one_online"
                self.mongodb.update_many_documents("interview", "now", {"_id": "com%s" % e_i}, {"status": status})
                return HttpResponseRedirect(target)
                # rep = redirect(target)
                # rep.set_cookie("enterpriseId", e_i)
                # return redirect(redirect_target)
                # return render(request, "meeting_assign.html", {"result": target})
            else:
                return render(request, "meeting_assign.html", {"msg": "错误的数据，请重新提交"})



