
import json
from mongodb import MongoDBManipulator

empty_enterprise_code = [59, 60, 61, 70, 81, 82]
mongodb = MongoDBManipulator("172.16.0.6", 27017, "mongouser", "Tx20233428@")

# change interview_info
candidate_name_code_mapping = json.load(open("./data/json/candidate_name_code_mapping.json", "r", encoding="utf-8"))
candidate_basic_info = json.load(open("./data/json/candidate_basic_info.json", "r", encoding="utf-8"))
candidate_com_mapping = json.load(open("./data/json/candidate_com_mapping.json", "r", encoding="utf-8"))

for name in list(candidate_name_code_mapping.keys()):
    interview_info_template = {
        "resume": "",
        "photo": "",
        "selfIntroduction": "",
        "appliedJob": 0,
        "firstWish": 0,
        "secondWish": 0,
        "interviewComCode": ""
    }
    user_info_template = [
        {"_id": 0, "account": ""},
        {"_id": 1, "password": "b9e79361b4040a3f3a71668163d2f058"},
        {"_id": 2, "class": ""},
        {"_id": 3, "userType": "candidate"},
        {"_id": 4, "nickname": ""},
        {"_id": 5, "token": None},
        {"_id": 6, "lastLoginTimeStamp": None},
        {"_id": 7, "isOnline": False},
        {"_id": 8, "appliedEnterprise": 0},
        {"_id": 9, "interviewInfo": interview_info_template}
    ]

    code = candidate_name_code_mapping[name]
    print("  now process-%s" % code)

    user_info = list(mongodb.get_document("candidate", code, mode=0))

    print("  modify account-%s's info" % code)
    interview_info_template["appliedEnterprise"] = user_info[8]["appliedEnterprise"]
    try:
        interview_info_template["selfIntroduction"] = candidate_basic_info[code]["selfIntroduction"]
        interview_info_template["firstWish"] = candidate_basic_info[code]["firstWish"]
        interview_info_template["secondWish"] = candidate_basic_info[code]["secondWish"]
        interview_info_template["interviewComCode"] = candidate_com_mapping[code]
    except KeyError:
        print("  user-%s does not upload basic info or not applied yet" % code)
    interview_info_template["photo"] = "%s.jpg" % code
    mongodb.update_many_documents("candidate", code, {"_id": 9}, {"interviewInfo": interview_info_template})
    mongodb.update_many_documents("candidate", code, {"_id": 2}, {"class": code[0:2]})
    mongodb.update_many_documents("candidate", code, {"_id": 4}, {"nickname": name})




