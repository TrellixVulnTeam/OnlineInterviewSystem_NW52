# author: Lanzhijiang
# desc: upload enterprise info to mongodb

import json
from mongodb import MongoDBManipulator
# from memcached import MemcachedManipulator

# enterprise_info_template = json.load(open("./enterprise_info_template.json", "r", encoding="utf-8"))
# enterprise_info = json.load(open("./enterprise.json", "r", encoding="utf-8"))

mongodb = MongoDBManipulator("172.16.0.9", 27017, "mongouser", "Tx20233428@")
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

enterprise_codes = list(range(1, 112))
empty_enterprise_code = [59, 60, 61, 70, 81, 82]
info = []

for code in enterprise_codes:
    if code in empty_enterprise_code:
        continue
    info.append({
        "_id": int(code),
        "applied": [],
        "enterpriseCode": str(code),
        "computerCode": -1
    })

mongodb.add_many_documents("interview", "apply", info)

# print(list(mongodb.get_document("interview", "apply", {"_id": 23}, 1)))

# memcache = MemcachedManipulator("172.16.0.15", 9101)

# user_info_tem = [
#     {"_id":  0, "account":  ""},
#     {"_id":  1, "password":  ""},
#     {"_id":  2, "class": ""},
#     {"_id":  3, "userType":  "candidate"},
#     {"_id":  4, "nickname": "1ad466c7fee94d8dc0156aba4a11306a"},
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



