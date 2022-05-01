# coding=utf-8
# author: Lan_zhijiang
# description 主逻辑
# date: 2022/4/21

import threading
import time

from user_manage.user_manager import UserManager
from database.mongodb import MongoDBManipulator


class OIISBackendMain:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting
        self.ws_conn_list = self.ba.ws_conn_list

        # self.mongodb_manipulator = self.ba.mongodb_manipulator
        self.mongodb_manipulator = MongoDBManipulator(self.log, self.setting)
        self.user_manager = UserManager(self.ba)

        self.pre_called_list = MongoDataList(list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "pre_called_list"}))[0]["list"],
                                             self.mongodb_manipulator, ("interview", "calling", "pre_called_list"))
        self.called_list = MongoDataList(list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "called_list"}, 1))[0]["list"],
                                         self.mongodb_manipulator, ("interview", "calling", "called_list"))

        self.pre_call_queue = MongoDataList(list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "pre_call_queue"}, 1))[0]["list"],
                                            self.mongodb_manipulator, ("interview", "calling", "pre_call_queue"))
        self.call_queue = MongoDataList(list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "call_queue"}, 1))[0]["list"],
                                        self.mongodb_manipulator, ("interview", "calling", "call_queue"))

        self.special_call_list = MongoDataList(list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "special_call_list"}, 1))[0]["list"],
                                               self.mongodb_manipulator, ("interview", "calling", "special_call_list"))

        self.waiting_room_status = {}

        call_list_count_thread = threading.Thread(target=self.call_list_count, args=())
        call_list_count_thread.start()

    def get_enterprise_info(self, enterprise_code):

        """
        获取企业信息
        :param enterprise_code: 企业编号
        :return res, err
        """
        self.log.add_log("OIISBackendMain: try to get enterprise-%s's info" % enterprise_code, 1)
        enterprise_info_raw = list(self.mongodb_manipulator.get_document("enterprise", str(enterprise_code), mode=0))
        result = {}
        if not enterprise_info_raw:
            return result, "enterprise-%s does not exist" % enterprise_code
        else:
            result["name"] = enterprise_info_raw[1]["name"]
            result["jobs"] = enterprise_info_raw[3]["jobs"]
            result["interviewer"] = enterprise_info_raw[4]["interviewer"]
            return result, "success"

    def get_candidate_info(self, candidate_code):

        """
        获取面试者信息
        :param candidate_code: 企业编号
        :return res, err
        """
        self.log.add_log("OIISBackendMain: try to get candidate-%s's info" % candidate_code, 1)
        candidate_info_raw = list(self.mongodb_manipulator.get_document("candidate", candidate_code, mode=0))
        result = {}
        if not candidate_info_raw:
            return result, "candidate-%s does not exist" % candidate_code
        else:
            result["class"] = candidate_info_raw[2]["class"]
            result["name"] = candidate_info_raw[4]["nickname"]
            result["selfIntroduction"] = candidate_info_raw[9]["interviewInfo"]["selfIntroduction"]
            result["firstWish"] = candidate_info_raw[9]["interviewInfo"]["firstWish"]
            result["secondWish"] = candidate_info_raw[9]["interviewInfo"]["secondWish"]
            result["interviewComCode"] = candidate_info_raw[9]["interviewInfo"]["interviewComCode"]
            result["appliedEnterprise"] = candidate_info_raw[9]["interviewInfo"]["appliedEnterprise"]
            result["photo"] = candidate_info_raw[9]["interviewInfo"]["photo"]
            result["resume"] = candidate_info_raw[9]["interviewInfo"]["resume"]
            return result, "success"

    def get_com_info(self, com_code):

        """
        获取面试终端的信息
        :param com_code
        :return dict, str(res, err)
        """
        self.log.add_log("OIISBackendMain: try to get com-%s's info" % com_code, 1)
        com_info_raw = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))
        if not com_info_raw:
            self.log.add_log("OIISBackendMain: empty com info", 3)
            return {}, "com-%s does not exist" % com_code
        else:
            self.log.add_log("OIISBackendMain: get com info success", 1)
            return com_info_raw[0], "success"

    def set_apply_job(self, job_id, candidate_code, com_code):

        """
        设置面试岗位编号
        :param job_id: 岗位id
        :param com_code: 面试终端编号
        :param candidate_code: 面试者code
        :return
        """
        self.log.add_log("OIISBackendMain: set apply_job-%s for candidate-%s" % (job_id, candidate_code), 1)
        job_id = int(job_id)
        com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
        interview_queue = com_info["interviewQueue"]
        try:
            interview_queue["wait"][candidate_code]["appliedJob"] = job_id
        except KeyError:
            self.log.add_log("OIISBackendMain: candidate-%s had already in_interview or done", 2)
            return False
        enterprise_code = str(com_info["bindEnterprise"])
        interviewer_code = str(com_info["bindInterviewer"])

        if self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, com_info):
            candidate_interview_info = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("candidate", candidate_code, {"_id": 9}, 1),
                ["interviewInfo"]
            )[0]["interviewInfo"]

            candidate_interview_info["appliedJob"] = job_id
            self.mongodb_manipulator.update_many_documents("candidate", candidate_code, {"_id": 9}, {"interviewInfo": candidate_interview_info})

            job_name = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("enterprise", enterprise_code, {"_id": 3}, 1),
                ["jobs"]
            )[0]["jobs"][str(job_id)]
            try:
                self.ws_conn_list["interviewer"][interviewer_code].send_command("candidate_job_sat", {"appliedJobName": job_name})
            except KeyError:
                self.log.add_log("OIISBackendMain: interviewer-%s's socket connection was off!!!", 3)
                return False, "failed"

            self.log.add_log("OIISBackendMain: set apply job success", 1)
            return True, "success"
        else:
            self.log.add_log("OIISBackendMain: set apply job failed, database error", 3)
            return False, "database error"

    def interviewer_start_interview(self, candidate_code, com_code):

        """
        面试官端开始面试
        :param candidate_code: 面试者编号
        :param com_code: 面试终端编号
        """
        self.log.add_log("OIISBackendMain: interviewer upload event:interviewer_start_interview, com_code-%s" % com_code, 1)

        try:
            com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
        except IndexError:
            self.log.add_log("OIISBackendMain: com_code not exist, database error or wrong com_code-%s" % com_code, 3)
            return False, "com_code not exist, database error or wrong com_code-%s" % com_code
        else:
            try:
                interview_queue = com_info["interviewQueue"]
                status = com_info["status"]
                if status != "ready":
                    self.log.add_log("OIISBackendMain: the com-%s's status not allowed start_interview, can't start interview" % com_code, 3)
                    return False, "status not allowed start_interview, fail"

                candidate_interview_object = interview_queue["wait"][candidate_code]
                candidate_interview_object["status"] = "in_interview"
                del interview_queue["wait"][candidate_code]

                com_info["nowInterview"] = {candidate_code: candidate_interview_object}
                com_info["status"] = "in_interview"
                com_info["interviewQueue"] = interview_queue
            except KeyError:
                self.log.add_log("OIISBackendMain: candidate-%s is not exist in the wait_list, confirming your com_code and your interview status", 3)
                return False, "confirming your com_code and your interview_status"
            else:
                # start interview
                if self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, com_info):
                    self.ws_conn_list["interviewer"][com_info["bindInterviewer"]].start_count(com_code)
                    return True, "success"
                else:
                    self.log.add_log("OIISBackendMain: database error, can't move candidate into nowInterviewQueue" % candidate_code, 3)
                    return False, "database error"

    def interviewer_end_interview(self, candidate_code, com_code):

        """
        面试者端结束面试
        -> candidate client -> end_interview
        -> move interview_object to 'done'
        ->
        :param com_code: 面试终端
        :param candidate_code: 面试者编号
        """
        self.log.add_log("OIISBackendMain: interviewer upload event:interviewer_end_interview, handle", 1)

        try:
            com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
        except IndexError:
            self.log.add_log("OIISBackendMain: com_code not exist, database error or wrong com_code-%s" % com_code, 3)
            return False, "com_code not exist, database error or wrong com_code-%s" % com_code
        else:
            try:
                now_interview = com_info["nowInterview"]
                interview_queue = com_info["interviewQueue"]
                status = com_info["status"]
                if status != "in_interview":
                    self.log.add_log("OIISBackendMain: the com-%s's status not allowed end_interview, can't end interview" % com_code, 3)
                    return False, "status not allowed end_interview, fail"
                try:
                    b = now_interview[candidate_code]
                except KeyError:
                    self.log.add_log("OIISBackendMain: candidate-%s does not in interview data error", 3)
                    return False, "candidate is not under interview"

                candidate_interview_object = now_interview[candidate_code]
                candidate_interview_object["status"] = "done"
                interview_queue["done"][candidate_code] = candidate_interview_object

                com_info["nowInterview"] = {}
                com_info["status"] = "interviewer_online"
                com_info["interviewQueue"] = interview_queue
            except KeyError:
                self.log.add_log("OIISBackendMain: candidate-%s is not exist in the wait_list, confirming your com_code and your interview status", 3)
                return False, "confirming your com_code and your interview_status"
            else:
                # end interview
                if self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, com_info):
                    return True, "success"
                else:
                    self.log.add_log("OIISBackendMain: database error, can't empty the nowInterview" % candidate_code, 3)
                    return False, "database error"

    def candidate_is_interview_started(self, candidate_code, com_code):

        """
        面试者：查询面试是否开始
        :param candidate_code: 面试者账号
        :param com_code: 面试终端编号
        :logic
            check com_info-now is now's candidateCode == account
        """
        self.log.add_log("OIISBackendMain: process: is_interview_started, candidate-%s" % candidate_code, 1)
        try:
            com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
        except IndexError:
            self.log.add_log("OIISBackendMain: com_code not exist, database error or wrong com_code-%s" % com_code, 3)
            return False, "com_code not exist, database error or wrong com_code-%s" % com_code
        else:
            now_interview = com_info["nowInterview"]
            try:
                a = now_interview[candidate_code]
            except KeyError:
                self.log.add_log("OIISBackendMain: in com-%s, candidate-%s does not start interview" % (com_code, candidate_code), 1)
                return True, "success"
            else:
                self.log.add_log("OIISBackendMain: in com-%s, candidate-%s has started interview" % (com_code, candidate_code), 1)
                return True, "success"

    def candidate_is_interview_end(self, candidate_code, com_code):

        """
        面试者：查询面试是否结束
        :param candidate_code: 面试者
        :param com_code: 面试终端编号
        :logic
            please see candidate_is_interview_started as reference
        """
        self.log.add_log("OIISBackendMain: process: candidate_is_interview_end, candidate-%s" % candidate_code, 1)
        try:
            com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
        except IndexError:
            self.log.add_log("OIISBackendMain: com_code not exist, database error or wrong com_code-%s" % com_code, 3)
            return False, "com_code not exist, database error or wrong com_code-%s" % com_code
        else:
            interview_queue_done = com_info["interviewQueue"]["done"]
            try:
                a = interview_queue_done[candidate_code]
            except KeyError:
                self.log.add_log("OIISBackendMain: in com-%s, candidate-%s 's interview has end" % (com_code, candidate_code), 1)
                return True, "success"
            else:
                self.log.add_log("OIISBackendMain: in com-%s, candidate-%s 's interview has not end yet or started yet" % (com_code, candidate_code), 1)
                return True, "success"

    def call_list_count(self):

        """
        叫号列表计时
        :return
        """
        self.log.add_log("OIISBackendMain: call_list_count start", 1)
        end = False
        while end:
            time.sleep(4)
            for c in list(self.pre_call_queue.keys()):
                if self.call_queue[c][0] == -1:
                    end = True
                    break
                self.pre_call_queue[c][0] += 4
                if self.pre_call_queue[c][0] > 20:
                    for i in self.pre_call_queue[c][1:]:
                        self.pre_call(i)
                        self.pre_call_queue[c][0] = 0
            for c in list(self.call_queue.keys()):
                if self.call_queue[c][0] == -1:
                    end = True
                    break
                self.call_queue[c][0] += 4
                if self.call_queue[c][0] > 20:
                    for i in self.call_queue[c][1:]:
                        self.call(i)
                        self.call_queue[c][0] = 0

    # def call_init(self):
    #
    #     """
    #     叫号初始化(叫三批人过来)  废弃！丰山优先填补
    #     等待a_client指令
    #     :return
    #     """
    #     self.log.add_log("OIISBackendMain: run call_init", 1)
    #
    #     # enterprise_list = self.mongodb_manipulator.get_collection_names_list("enterprise")
    #     # enterprise_applied_all = list(self.mongodb_manipulator.get_document("interview", "apply", mode=0))
    #     enterprise_ids = self.mongodb_manipulator.get_collection_names_list("enterprise")
    #     calling_list = []
    #     now_interview_phase = self.ba.get_interview_phase()
    #     # 第一轮
    #     for enterprise_id in enterprise_ids:
    #         com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": "com%s" % enterprise_id}, 1))[0]
    #         self.log.add_log("OIISBackendMain: looking for %s's com wait list" % com_info["bindEnterprise"], 0)
    #         next_candidate_code = None
    #         for i in list(com_info["interviewQueue"]["wait"].keys()):
    #             if i[-1] == str(now_interview_phase):
    #                 next_candidate_code = i
    #         if next_candidate_code is None:
    #             for i in list(com_info["interviewQueue"]["wait"].keys()):
    #                 next_candidate_code = i
    #
    #         if next_candidate_code is None:
    #             self.log.add_log("OIISBackendMain: error! no more candidates to call", 3)
    #             return
    #
    #         self.log.add_log("OIISBackendMain: now add %s into init call list" % next_candidate_code, 0)
    #         self.call(next_candidate_code)
    #         calling_list.append(next_candidate_code)
    #
    #     time.sleep(260)
    #     self.log.add_log("OIISBackendMain: init formal call execute now", 1)
    #     for i in calling_list:
    #         self.log.add_log("OIISBackendMain: calling-%s" % i, 0)
    #         self.call(i)

    def pre_call(self, candidate_code):

        """
        预叫号
        :param candidate_code: 面试者编号
        加入队列，当到达一定数量/一定时间内则一同下方
        """
        self.log.add_log("OIISBackendMain: add %s into pre_call_queue" % candidate_code, 1)

        class_belong = str(int(candidate_code[0:2]))
        if class_belong in ["28", "29", "30", "31"]:
            return
        try:
            self.pre_call_queue[class_belong].append(candidate_code)
        except KeyError:
            self.pre_call_queue[class_belong] = [0]
            self.pre_call_queue[class_belong].append(candidate_code)
            self.pre_called_list[class_belong] = []
        else:
            self.pre_call_queue[class_belong].append(candidate_code)
            if len(self.pre_call_queue[class_belong]) >= 5 or self.pre_call_queue[class_belong][0] > 60:
                call_list = []
                for i in self.pre_call_queue[class_belong]:
                    if type(i) == int:
                        continue
                    block = {"candidateCode": i}
                    candidate_info = self.mongodb_manipulator.parse_document_result(
                        self.mongodb_manipulator.get_document("candidate", i, mode=0),
                        ["nickname", "appliedEnterprise", "interviewInfo"]
                    )
                    block["name"] = candidate_info[0]["nickname"]
                    block["comCode"] = candidate_info[2]["interviewInfo"]["interviewComCode"]
                    block["appliedEnterprise"] = candidate_info[1]["appliedEnterprise"]

                    call_list.append(block)
                    self.pre_call_queue[class_belong].remove(i)
                    self.pre_called_list[class_belong].append(i)
                try:
                    self.ws_conn_list["class"]["class%s" % class_belong].send_command("pre_call",
                                                                                      {"callList": call_list})
                    self.pre_called_list[class_belong][-1].append("success!!!")
                    self.log.add_log("OIISBackendMain: pre_call class-%s success" % class_belong, 1)
                except KeyError:
                    self.pre_called_list[class_belong][-1].append("failed!!!")
                    self.log.add_log("OIISBackendMain: pre_call failed, class-%s offline!!!" % class_belong, 3)

    def call(self, candidate_code):

        """
        正式叫号
        :param candidate_code: 面试者编号
        """
        self.log.add_log("OIISBackendMain: add %s into formal call queue" % candidate_code, 1)

        class_belong = str(int(candidate_code[0:2]))
        if class_belong in ["28", "29", "30", "31"]:
            return
        try:
            if candidate_code not in self.call_queue[class_belong]:
                self.log.add_log("OIISBackendMain: real add", 1)
                self.call_queue[class_belong].append(candidate_code)
                self.call_queue.update_to_database()
        except KeyError:
            self.call_queue[class_belong] = [0]
            self.call_queue[class_belong].append(candidate_code)
            self.call_queue.update_to_database()
            self.called_list[class_belong] = []
            self.called_list.update_to_database()
        else:
            if len(self.call_queue[class_belong]) >= 6 or self.call_queue[class_belong][0] > 15:
                call_list = []
                for i in self.call_queue[class_belong]:
                    if type(i) == int:
                        continue

                    if i in self.special_call_list:
                        self.log.add_log("OIISBackendMain: it's time for %s to interview!!!" % i, 2)
                        special_call_arrived = list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "special_call_arrived"}, 1))[0]["list"]
                        special_call_arrived.append(i)
                        self.mongodb_manipulator.update_many_documents("interview", "calling", {"_id": "special_call_arrived"}, {"list": special_call_arrived})
                        continue
                        # self.ws_conn_list["a_client"]["root"].send_command("special_call", {"candidateCode": i})

                    block = {"candidateCode": i}
                    candidate_info = list(self.mongodb_manipulator.get_document("candidate", i, mode=0))
                    block["name"] = candidate_info[4]["nickname"]
                    a_e = candidate_info[8]["appliedEnterprise"]
                    block["appliedEnterprise"] = a_e
                    block["comCode"] = "com%s" % a_e

                    call_list.append(block)

                    self.call_queue[class_belong].remove(i)
                    self.call_queue.update_to_database()
                    # self.ws_conn_list["a_client"]["root"].send_command("call_start", {"callList": call_list})
                try:
                    self.called_list[class_belong].append({"list": call_list})
                except KeyError:
                    self.called_list[class_belong] = []
                    self.called_list[class_belong].append({"list": call_list})

                self.called_list.update_to_database()
                try:
                    self.ws_conn_list["class"]["class%s" % class_belong].send_command("call", {"callList": call_list})
                    self.log.add_log("OIISBackendMain: call class-%s success" % class_belong, 1)
                    self.called_list[class_belong][-1]["res"] = "success"
                except KeyError:
                    self.called_list[class_belong][-1]["res"] = "failed"
                    self.log.add_log("OIISBackendMain: call failed, class-%s offline!!!" % class_belong, 3)

                self.called_list.update_to_database()

    def l3_waiting_start_handle(self, com_code, candidate_code):

        """
        三级缓存室-开始等待
            记录时间，结束计时
        :param com_code: 终端号码
        :param candidate_code: 当前等待的面试者编号
        """
        self.log.add_log("OIISBackendMain: start handle l3_waiting_start", 1)
        self.waiting_room_status[com_code] = "in_waiting"
        # self.ws_conn_list["a_client"]["root"].send_command("wrc_start_wait", {"comCode": com_code})

        try:
            com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
        except IndexError:
            self.log.add_log("OIISBackendMain: fail to get com-%s's info" % com_code, 3)
            return False, "database error"
        else:
            class_belong = str(int(candidate_code[0:2]))
            self.call_queue[class_belong][-1] = -1
            try:
                com_info["nowInterview"][candidate_code] = com_info["interviewQueue"]["wait"][candidate_code]
            except KeyError:
                self.log.add_log("OIISBackendMain: fail to read com-%s info, key error, candidate-%s" % (com_code, candidate_code), 1)
                self.called_list[str(int(candidate_code[0:2]))][-1]["res"] = "failed!!!"

            del com_info["interviewQueue"]["wait"][candidate_code]
            self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"interviewQueue": com_info["interviewQueue"], "nowInterview": com_info["nowInterview"]})
            return True, "success"

    def l3_waiting_end_handle(self, com_code, candidate_code):

        """
        三级缓存室-结束等待
            叫号下一个
        :param com_code: 终端号码
        :param candidate_code: 面试者编号
        """
        self.log.add_log("OIISBackendMain: start handle l3_waiting_end, from com-%s" % com_code, 1)
        self.waiting_room_status[com_code] = "wait_for_next"

        next_candidate_code = self.pick_next_candidate(com_code)
        if next_candidate_code is not None:
            self.call(next_candidate_code)
            com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
            try:
                com_info["nowInterview"][next_candidate_code] = com_info["interviewQueue"]["wait"][next_candidate_code]
            except KeyError:
                self.log.add_log("OIISBackendMain: fail to read com-%s info, key error, candidate-%s" % (com_code, next_candidate_code))
                self.called_list[str(int(next_candidate_code[0:2]))][-1]["res"] = "failed!!!"

            com_info["interviewQueue"]["done"][candidate_code] = com_info["nowInterview"][candidate_code]
            del com_info["nowInterview"][candidate_code]
            self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"interviewQueue": com_info["interviewQueue"], "nowInterview": com_info["nowInterview"]})
            self.ws_conn_list["waiting_room"][com_code].send_response("waiting_end", {"nextCandidateCode": next_candidate_code})
        else:
            self.ws_conn_list["waiting_room"][com_code].send_command("final_end_interview", {})

    def l3_overtime_for_next_to_come_handle(self, com_code, candidate_code):

        """
        三级缓冲室-超时
        """
        self.log.add_log("OIISBackendMain: l3 waiting room-%s wait_for_next to come" % com_code, 1)

        raw_overtime_list = list(self.mongodb_manipulator.get_document("interview", "calling", {"_id": "overtime_list"}, 1))[0]["list"]
        class_belong = str(int(candidate_code[0:2]))
        try:
            raw_overtime_list[class_belong].append([candidate_code, com_code.replace("com", "")])
        except KeyError:
            raw_overtime_list[class_belong] = []
            raw_overtime_list[class_belong].append([candidate_code, com_code.replace("com", "")])
        self.mongodb_manipulator.update_many_documents("interview", "calling", {"_id": "overtime_list"}, {"list": raw_overtime_list})

    def l3_init_waiting_handle(self, com_code):

        """
        三级缓冲室-初始化叫号
        """
        self.log.add_log("OIISBackendMain: l3 waiting room-%s init waiting" % com_code, 1)

        next_candidate_code = self.pick_next_candidate(com_code)
        if next_candidate_code is not None:
            self.call(next_candidate_code)
            com_info = list(self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1))[0]
            com_info["nowInterview"][next_candidate_code] = com_info["interviewQueue"]["wait"][next_candidate_code]
            del com_info["nowInterview"][next_candidate_code]
            self.mongodb_manipulator.update_many_documents("interview", "now", {"_id": com_code}, {"interviewQueue": com_info["interviewQueue"], "nowInterview": com_info["nowInterview"]})
            try:
                self.ws_conn_list["waiting_room"][com_code].send_response("init_waiting", {"nextCandidateCode": next_candidate_code})
            except KeyError:
                self.log.add_log("OIISBackendMain: com-%s has lost conn!!!" % com_code, 3)
        else:
            self.ws_conn_list["waiting_room"][com_code].send_command("final_end_interview", {})

    def add_special_call(self, candidate_code):

        """
        添加特殊叫号名单
        :param candidate_code: 面试者编号
        :return
        """
        self.log.add_log("OIISBackendMain: add special call for candidate-%s" % candidate_code, 1)

        self.special_call_list.append(candidate_code)

    def pick_next_candidate(self, com_code):

        """
        选取下一个面试者

        """
        try:
            in_queue_candidate_list = self.mongodb_manipulator.parse_document_result(
                self.mongodb_manipulator.get_document("interview", "now", {"_id": com_code}, 1),
                ["interviewQueue"]
            )[0]["interviewQueue"]["wait"]
        except IndexError:
            self.log.add_log("OIISBackendMain: com-%s does" % com_code, 3)
            return

        if not in_queue_candidate_list:
            self.log.add_log("OIISBackendMain: no more candidates, all has been done", 1)
            return None

        now_interview_phase = self.ba.get_interview_phase()
        next_candidate_code = None
        for i in list(in_queue_candidate_list.keys()):
            j = in_queue_candidate_list[i]
            if j["interviewPhase"] == now_interview_phase:
                next_candidate_code = j["candidateCode"]
            if next_candidate_code is None:
                next_candidate_code = j["candidateCode"]
            else:
                break

            if int(next_candidate_code[0:2]) in [28, 29, 30, 31]:
                continue

        return next_candidate_code


class MongoDataList:

    def __init__(self, raw_list, mongodb, db_param):

        self.main_list = raw_list
        self.mongodb = mongodb
        self.db_name = db_param[0]
        self.coll_name = db_param[1]
        self._id = db_param[2]

    def __len__(self):

        return len(self.main_list)

    def append(self, value):

        self.main_list.append(value)
        self.update_to_database()

    def extend(self, value):

        self.main_list.extend(value)
        self.update_to_database()

    def insert(self, value):

        self.main_list.insert(value)
        self.update_to_database()

    def __str__(self):

        return str(self.main_list)

    def __get__(self, key):

        try:
            return self.main_list[key]
        except KeyError:
            return None

    def __getitem__(self, key):

        return self.main_list[key]

    def __setitem__(self, key, value):

        self.main_list[key] = value
        self.update_to_database()

    def __delitem__(self, key):

        del self.main_list[key]
        self.update_to_database()

    def items(self):

        return self.main_list.items()

    def keys(self):

        return self.main_list.keys()

    def update_to_database(self):

        self.mongodb.update_many_documents(self.db_name, self.coll_name, {"_id": self._id}, {"list": self.main_list})
