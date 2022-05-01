# author: Lanzhijiang
# desc: upload enterprise info to mongodb

import json
from mongodb import MongoDBManipulator
from encryption import Encryption

# from memcached import MemcachedManipulator

# enterprise_info_template = json.load(open("./enterprise_info_template.json", "r", encoding="utf-8"))
# enterprise_info = json.load(open("./enterprise.json", "r", encoding="utf-8"))

mongodb = MongoDBManipulator("172.16.0.6", 27017, "mongouser", "Tx20233428@")
encryption = Encryption()
import time

# interview_apply_info = [{"_id": 0, "interviewCount": 0}]


# for e_i in enterprise_info:
#     account = str(e_i["_id"])
#     user_info = enterprise_info_template
#     user_info[0]["code"] = account
#     user_info[1]["name"] = e_i["name"]
#     user_info[2]["interviewerCount"] = e_i["interviewerCount"]
#     user_info[3]["jobs"] = e_i["jobs"]
#     user_info[4]["interviewer"] = e_i["interviewer"]
#     mongodb.add_many_documents("enterprise", account, user_info)
#     interview_apply_info.append(
#         {
#             "_id": int(account),
#             "applied": []
#         }
#     )
#     print("update %s's info complete" % account)

# enterprise_codes = list(range(1, 112))
empty_enterprise_code = [59, 60, 61, 70, 81, 82]
# info = []
#
# for code in enterprise_codes:
#     if code in empty_enterprise_code:
#         continue
#     info.append({
#         "_id": int(code),
#         "applied": [],
#         "enterpriseCode": str(code),
#         "computerCode": -1
#     })
#
# mongodb.add_many_documents("interview", "apply", info)

# print(list(mongodb.get_document("interview", "apply", {"_id": 23}, 1)))

# memcache = MemcachedManipulator("172.16.0.15", 9101)

# user_info_tem = [
#     {"_id":  0, "account":  ""},
#     {"_id":  1, "password":  "1ad466c7fee94d8dc0156aba4a11306a"},
#     {"_id":  2, "class": ""},
#     {"_id":  3, "userType":  "candidate"},
#     {"_id":  4, "nickname": ""},
#     {"_id":  5, "token":  None},
#     {"_id":  6, "lastLoginTimeStamp": None},
#     {"_id":  7, "isOnline": False},
#     {"_id":  8, "appliedEnterprise": 0},
#     {"_id":  9, "interviewInfo": {}}
# ]
#
# class_1 = [1,2,3,4,5,6,10,11,12,13,14,15,16,17,18]
# class_2 = [7,8,9,19,20,21,22,23,24,25,26,27,28,29,30,31]
#
# for c in range(1, 32):
#     time.sleep(5)
#     print("now class: %s" % c)
#     if c in class_1:
#         p = 1
#     else:
#         p = 2
#
#     c = str(c)
#     user_info_tem[2]["class"] = c
#     if len(c) == 1:
#         c = "0%s" % c
#
#     for code in range(0, 60):
#         time.sleep(2)
#         code = str(code)
#         if len(code) == 1:
#             code = "0%s" % code
#
#         f_code = c + code + str(p)
#         if f_code == "09482":
#             continue
#         print("  now_load_f_code: %s" % f_code)
#         user_info_tem[0]["account"] = f_code
#         mongodb.add_many_documents("candidate", f_code, user_info_tem)

# a = [-1]
# for i in range(0, 112):
#     a.append(16)
# memcache.set("whole_status_1", a)
#
# for i in enterprise_info:
#     id = str(i["_id"])
#     memcache.set(id, 16)
#     print("set %s" % id)
# print(memcache.get_multi(["1", "2", "3"]))

# create now document

# com_interviewer_mapping_list = {}
# candidate_com_mapping_list = {}
# result = []
# for i in range(1, 112):
#     if i in empty_enterprise_code:
#         continue
#
#     print("now process enterprise-%s" % i)
#     if len(str(i)) == 1:
#         i_str = "0%s" % i
#     else:
#         i_str = str(i)
#
#     now_docu = {
#         "_id": "com%s" % i,
#         "bindInterviewer": str(i_str) + "01",
#         "bindEnterprise": i,
#         "nowInterview": {},
#         "interviewQueue": {
#             "wait": {},
#             "done": {}
#         },
#         "status": "offline",
#         "meetingPlatform": "tencent",
#         "meetingUrlList": {
#             "dingtalk": "",
#             "tencent": "",
#             "jitsi": "https://meeting.hadream.ltd/%s" % i
#         }
#     }
#     com_interviewer_mapping_list[str(i_str) + "01"] = "com%s" % i
#
#     enterprise_apply_list = mongodb.parse_document_result(
#         mongodb.get_document("interview", "apply", {"_id": i}, 1),
#         ["applied"]
#     )[0]["applied"]
#
#     for j in enterprise_apply_list:
#         interview_object = {
#             "interviewPhase": 0,
#             "candidateCode": "",
#             "interviewerCode": "",
#             "enterpriseCode": 0,
#             "appliedJob": 0,
#             "status": "wait",
#             "result": None,
#             "feedback": None
#         }
#         print("  now add candidate-%s to wait list" % j)
#         interview_object["interviewPhase"] = int(j[-1])
#         interview_object["candidateCode"] = j
#         interview_object["interviewerCode"] = str(i_str) + "01"
#         interview_object["enterpriseCode"] = i
#         candidate_com_mapping_list[j] = "com%s" % i
#         now_docu["interviewQueue"]["wait"][j] = interview_object
#
#     result.append(now_docu)
#
# mongodb.add_many_documents("interview", "now", result)
# json.dump(com_interviewer_mapping_list, open("./data/json/interviewer_com_mapping.json", "w", encoding="utf-8"))
# json.dump(candidate_com_mapping_list, open("./data/json/candidate_com_mapping.json", "w", encoding="utf-8"))

# interviewer_com_mapping = json.load(open("./data/json/interviewer_com_mapping.json", "r", encoding="utf-8"))
#
# enterprise_code_list = mongodb.get_collection_names_list("enterprise")
# for code in enterprise_code_list:
#     print("now process-%s" % code)
#     interviewer_list = mongodb.parse_document_result(
#         mongodb.get_document("enterprise", str(code), {"_id": 4}, 1),
#         ["interviewer"]
#     )[0]["interviewer"]
#
#     if not interviewer_list:
#         print("  e-%s have no interviewer!" % code)
#     else:
#         if len(str(code)) == 1:
#             code_str = "0%s" % code
#         else:
#             code_str = str(code)
#         for interviewer_code in range(0, len(interviewer_list)):
#             interviewer_info = interviewer_list[interviewer_code]
#             interviewer_code += 1
#             if len(str(interviewer_code)) == 1:
#                 interviewer_code_str = "0%s" % interviewer_code
#             else:
#                 interviewer_code_str = str(interviewer_code)
#             try:
#                 mapping_com_code = interviewer_com_mapping[code_str + interviewer_code_str]
#             except KeyError:
#                 mapping_com_code = "com0"
#             interviewer_info_tem = [
#                 {"_id": 0, "account": code_str + interviewer_code_str},
#                 {"_id": 1, "password": encryption.md5(encryption.md5(interviewer_info["phone"]))},
#                 {"_id": 2, "userType": "interviewer"},
#                 {"_id": 3, "nickname": interviewer_info["name"]},
#                 {"_id": 4, "token":  None},
#                 {"_id": 5, "lastLoginTimeStamp": None},
#                 {"_id": 6, "isOnline": False},
#                 {"_id": 7, "belongedEnterprise": code},
#                 {"_id": 8, "mappingComCode": mapping_com_code}
#             ]
#             mongodb.add_collection("interviewer", code_str + interviewer_code_str)
#             mongodb.add_many_documents("interviewer", code_str + interviewer_code_str, interviewer_info_tem)

# for i in range(1, 111):
#
#     c_i = "com%s" % i
#     now_info = mongodb.get_document("interview", "now", {"_id": c_i}, 1)
#     if not now_info:
#         continue
#     now_info = now_info[0]
#
#     now_info["meetingRoomCode"] = None
#     mongodb.update_many_documents("interview", "now", {"_id": c_i}, now_info)

# for i in range(1, 32):
#
#     class_code = "class%s" % i
#     user_info_template = [
#         {"_id": 0, "account": class_code},
#         {"_id": 1, "password": "b9e79361b4040a3f3a71668163d2f058"},
#         {"_id": 3, "userType": "class"},
#         {"_id": 4, "nickname": "高二%s班" % i},
#         {"_id": 5, "token": None},
#         {"_id": 6, "lastLoginTimeStamp": None},
#         {"_id": 7, "isOnline": False}
#     ]
#     mongodb.add_collection("class", class_code)
#     mongodb.add_many_documents("class", class_code, user_info_template)


# upload reassign applied info
#
# reassign_list = json.load(open("./data/json/interview_apply_info_re_assigned2.json", "r", encoding="utf-8"))
#
# for enterprise_id in list(reassign_list.keys()):
#
#     print("process %s" % enterprise_id)
#
#     mongodb.update_many_documents("interview", "apply", {"_id": int(enterprise_id)}, {"applied": reassign_list[enterprise_id]})
#     for candidate in reassign_list[enterprise_id]:
#         print("  candidate-%s" % candidate)
#         mongodb.update_many_documents("candidate", candidate, {"_id": 8}, {"appliedEnterprise": int(enterprise_id)})


# update now's wait list
# reassign_list = json.load(open("./data/json/interview_apply_info_re_assigned2.json", "r", encoding="utf-8"))
reassign_list = mongodb.parse_document_result(
    mongodb.get_document("interview", "apply", mode=0),
    ["applied", "_id"]
)

candidate_com_mapping_list = {}

for i in range(0, len(reassign_list)):

    enterprise_id = str(reassign_list[i]["_id"])
    print("  process com%s" % enterprise_id)
    com_code = "com%s" % enterprise_id
    reassign_one_list = reassign_list[i]["applied"]
    if len(enterprise_id) == 1:
        enterprise_id_str = "0%s" % enterprise_id
    else:
        enterprise_id_str = enterprise_id

    interview_queue = {"wait": {}, "done": {}}
    for candidate_id in reassign_one_list:
        interview_object = {"interviewPhase": int(candidate_id[-1]), "candidateCode": candidate_id,
                            "interviewerCode": enterprise_id_str + "01", "enterpriseCode": int(enterprise_id),
                            "appliedJob": 0, "status": "wait", "result": None, "feedback": None}
        candidate_com_mapping_list[candidate_id] = com_code
        interview_queue["wait"][candidate_id] = interview_object

    mongodb.update_many_documents("interview", "now", {"_id": com_code}, {"interviewQueue": interview_queue})

json.dump(candidate_com_mapping_list, open("./data/json/interviewer_com_mapping.json", "w", encoding="utf-8"))

# result = {
#     "106": [], "107": [], "108": [], "109": [], "110": [], "111": []
# }
#
# for candidate in list(mongodb.get_collection_names_list("candidate")):
#     applied_enterprise = list(mongodb.get_document("candidate", candidate, {"_id": 8}, 1))[0]["appliedEnterprise"]
#     if applied_enterprise in [106, 107, 108, 109, 110, 111]:
#         result[str(applied_enterprise)].append(candidate)
#
# print(result)

# apply_info_all = json.load(open("./data/json/interview_apply_info_all_fixed.json", "r", encoding="utf-8"))
#
# for i in list(apply_info_all.keys()):
#
#     enterprise_id = int(i)
#     applied = apply_info_all[i]
#     mongodb.update_many_documents("interview", "apply", {"_id": enterprise_id}, {"applied": applied})
