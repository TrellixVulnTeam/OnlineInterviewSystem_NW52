# bind all data together
# 2022/4/19
import os

# 坏的！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！1

from mongodb import MongoDBManipulator
import json
import time

# basic data
empty_enterprise_code = [59, 60, 61, 70, 81, 82]
mongodb = MongoDBManipulator("172.16.0.6", 27017, "mongouser", "Tx20233428@")

candidate_name_code_mapping = json.load(open("./data/json/candidate_name_code_mapping.json", "r", encoding="utf-8"))
candidate_apply_enterprise_mapping = json.load(open("./data/json/interview_apply_info_all.json.json", "r", encoding="utf-8"))
candidate_basic_info = json.load(open("./data/json/candidate_basic_info.json", "r", encoding="utf-8"))

result = []


for name in list(candidate_name_code_mapping.keys()):
    print("process %s" % name)
    try:
        code = candidate_name_code_mapping[name]
    except KeyError:
        code = None

    try:
        applied_enterprise = candidate_apply_enterprise_mapping[code]
    except KeyError:
        applied_enterprise = None

    try:
        basic_info = candidate_basic_info[code]
    except KeyError:
        basic_info = None
    #
    # if code + ".jpg" in candidate_imgs or code + ".png" in candidate_imgs or "%s.jpeg" % code in candidate_imgs:
    #     customize_img = True
    # else:
    #     customize_img = False

    result.append({
        "_id": code,
        "name": name,
        "class": str(int(code[0:2])),
        "appliedEnterprise": applied_enterprise,
        # "uploadBasicInfo": basic_info,
        # "customizeImg": customize_img
    })


json.dump(result, open("./data/json/confirming_data.json", "w", encoding="utf-8"))
mongodb.add_many_documents("interview", "confirming", result)




