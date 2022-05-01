# export and verify the data of apply enterprise

from mongodb import MongoDBManipulator
import json

mongodb = MongoDBManipulator("172.16.0.10", 27017, "mongouser", "Tx20233428@")

# verify
candidate_list = mongodb.get_collection_names_list("candidate")
interview_apply_list = list(range(1, 112))
empty_enterprise_code = [59, 60, 61, 70, 81, 82]
limit_list = [-1, 31, 32, 32, 31, 31, 32, 31, 32, 32, 32, 32, 32, 32, 32, 31, 32, 31, 32, 32, 32, 32, 32, 36, 32, 32,
              32, 32, 32, 32, 31, 32, 32, 31, 32, 32, 32, 32, 31, 32, 31, 31, 37, 34, 32, 32, 32, 32, 32, 32, 32, 32,
              32, 32, 31, 32, 32, 32, 31, 15, 15, 15, 34, 32, 32, 32, 33, 32, 36, 32, 15, 32, 31, 32, 32, 31, 32, 32,
              32, 32, 32, 15, 15, 32, 32, 32, 32, 32, 32, 36, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
              32, 37, 32, 32, 32, 32, 32, 32, 15]
left_list = [-1]
reassign_list = json.load(open("./data/json/interview_apply_info_re_assigned2.json", "r", encoding="utf-8"))
now_remain_list = list(mongodb.get_document("interview", "temp", mode=0))

# for i in range(1, 112):
#     if i in empty_enterprise_code:
#         left_list.append(0)
#         continue
#
#     print("  process enterprise-%s" % i)
#     if i in [105, 23, 47]:
#         left_list.append(0)
#         continue
#
#     if i in [13, 87, 71, 72, 4, 10]:
#         left_list.append(0)
#         continue
#
#     if now_remain_list[i]["data"] < 0:
#         left_list.append(0)
#         continue
#
#     data = limit_list[i] - len(reassign_list[str(i)])
#     left_list.append(data)
#     mongodb.update_many_documents("interview", "temp", {"_id": i}, {"data": data})
#
# mongodb.update_many_documents("interview", "temp", {"_id": 0}, {"whole_status": left_list})

over_load = {}
interview_apply_info_all = {}
for interview_apply_id in interview_apply_list:
    if interview_apply_id in empty_enterprise_code:
        continue
    print("now get interview_apply-%s" % interview_apply_id)
    interview_apply_applied_list = mongodb.parse_document_result(
        mongodb.get_document("interview", "apply", {"_id": interview_apply_id}, 1),
        ["applied"]
    )[0]["applied"]

    interview_apply_info_all[str(interview_apply_id)] = interview_apply_applied_list
    if len(interview_apply_applied_list) > limit_list[interview_apply_id]:
        over_load[interview_apply_id] = len(interview_apply_applied_list)

json.dump(interview_apply_info_all, open("data/json/interview_apply_info_all.json", "w", encoding="utf-8"))
json.dump(over_load, open("data/json/interview_apply_over_load.json", "w", encoding="utf-8"))

wrong_data = []
mapping_list = {}
not_applied = []

for candidate_id in candidate_list:
    print("now verify candidate-%s" % candidate_id)
    candidate_applied_enterprise_code = mongodb.parse_document_result(
        mongodb.get_document("candidate", candidate_id, {"_id": 8}, 1),
        ["appliedEnterprise"]
    )[0]["appliedEnterprise"]

    if candidate_applied_enterprise_code == 0:
        not_applied.append(candidate_id)
        continue

    try:
        if candidate_id not in interview_apply_info_all[str(candidate_applied_enterprise_code)]:
            wrong_data.append(candidate_id)
            print("  try to fix")
            interview_apply_info_all[str(candidate_applied_enterprise_code)].append(candidate_id)
            mongodb.update_many_documents("interview", "apply", {"_id": candidate_applied_enterprise_code}, {"applied": interview_apply_info_all[str(candidate_applied_enterprise_code)]})
        else:
            mapping_list[candidate_id] = candidate_applied_enterprise_code
    except KeyError:
        continue

json.dump(mapping_list, open("./data/json/candidate_apply_enterprise_mapping.json", "w", encoding="utf-8"))
json.dump(wrong_data, open("./data/json/candidate_apply_enterprise_wrong.json", "w", encoding="utf-8"))
json.dump(not_applied, open("./data/json/candidate_apply_enterprise_not_applied.json", "w", encoding="utf-8"))

# process can't come's
# not_come_to = [
#     "06211", "18491", "14081", "16431", "03481", "02541", "13181", "17311", "17031", "20552", "26212", "22462", "21072",
#     "08072", "25022", "18411",
#     "01011", "02011", "03011", "02401", "17491", "03561", "05111", "22242", "28182", "21182", "26432", "25062", "23432",
#     "26132", "29452", "04061",
#     "15201", "06261", "11311", "13361", "12081", "12461", "13381", "28092", "09182", "19222", "19502", "07332", "28252",
#     "28132", "19512", "29492"
# ]
#
# for candidate in not_come_to:
#     mongodb.update_many_documents("candidate", candidate, {"_id": 8}, {"appliedEnterprise": 0})
#     print("  update %s's appliedEnterprise to 0" % candidate)
