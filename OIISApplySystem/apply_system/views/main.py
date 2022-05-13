from django.shortcuts import render, redirect, HttpResponse, Http404
from django.template.context_processors import csrf
import random
import json

from apply_system.database.mongodb import MongoDBManipulator
from apply_system.database.memcached import MemcachedManipulator
from apply_system.views.confirm_data import ConfirmData
from apply_system.views.reset_password import ResetPassword
from apply_system.views.apply_enterprise import ApplyEnterprise
from apply_system.views.meeting_assign_main import MeetingAssignMain

m_a_m = MeetingAssignMain()
reset_password = ResetPassword()
apply_enterprise = ApplyEnterprise()
confirm_data = ConfirmData()


def handle_main_page_request(request):

    return render(request, 'index.html')


def handle_desc_request(request):

    return render(request, 'desc.html')


def get_csrf(request):

    x = csrf(request)
    csrf_token = x['csrf_token']
    return HttpResponse('{} ; {}'.format(str(random.randint(0, 100)) + str(random.randint(0, 100)), csrf_token))


class Main:

    def __init__(self):

        self.setting = json.load(open(r"./apply_system/data/json/setting.json", "r", encoding="utf-8"))
        self.mongodb = MongoDBManipulator(self.setting["database"]["mongodb"]["addr"],
                                          self.setting["database"]["mongodb"]["port"],
                                          self.setting["database"]["mongodb"]["auth"][0],
                                          self.setting["database"]["mongodb"]["auth"][1])

        self.memcache = MemcachedManipulator(self.setting["database"]["memcached"]["addr"],
                                             self.setting["database"]["memcached"]["port"])

        self.urls = {
            "/login/": apply_enterprise.handle_login_request,
            "/logout/": apply_enterprise.handle_logout_request,
            "/reset_password/": reset_password.handle_request,
            "/apply_enterprise/": apply_enterprise.handle_apply_enterprise_request,
            "/get_remained_info/": apply_enterprise.handle_get_remained_info_request,
            "/desc/": handle_desc_request,
            "/confirm_data/": confirm_data.handle_confirm_data_request,
            "/get_confirm_data/": confirm_data.handle_get_confirm_data_request,
            "/": handle_main_page_request,
            "/meeting/": m_a_m.handle_request
        }

        self.white_ip_list = ["116.28.61.115", "61.142.103.101"]

    def handle_request(self, request):

        """
        处理所有请求并分发
        :param request:
        :return:
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 判断是否使用代理
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
        else:
            ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP

        print("analyze ip now: %s" % ip)

        if ip not in self.white_ip_list:
            recent_ips = self.memcache.get("recent_ips")
            banned_ips = self.memcache.get("banned_ips")
            if ip in banned_ips:
                raise Http404

            id_ = "r_t_%s" % ip.replace(".", "")
            if ip in recent_ips:
                request_times = self.memcache.get(id_)
                if request_times > 50:
                    recent_ips.remove(ip)
                    banned_ips.append(ip)
                    self.memcache.set("banned_ips", banned_ips)
                    raise Http404
                else:
                    self.memcache.increase(id_)
            else:
                self.memcache.set(id_, 1)
                recent_ips.append(ip)
                self.memcache.set("recent_ips", recent_ips)

            if len(recent_ips) > 150:
                recent_ips = recent_ips[100:]
                self.memcache.set("recent_ips", recent_ips)

        request_path = request.path
        print("-------***-------NEW REQUEST to %s--------***------" % request_path)
        return self.urls[request_path](request)

