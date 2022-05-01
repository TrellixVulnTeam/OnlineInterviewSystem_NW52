
import random
import json
from mongodb import MongoDBManipulator

mongodb = MongoDBManipulator("172.16.0.6", 27017, "mongouser", "Tx20233428@")


# interview_apply_info = json.load(open("./data/json/interview_apply_info_all.json", "r", encoding="utf-8"))
# has_not_applied_candidate = json.load(open("./data/json/candidate_apply_enterprise_not_applied.json", "r", encoding="utf-8"))
#
# for i in list(interview_apply_info.keys()):
#     print(" now process enterprise-%s, has been applied-%s" % (i, len(interview_apply_info[i])))
#     has_applied_count = len(interview_apply_info[i])
#
#     if 17 <= has_applied_count < 21:
#         print("  normal, skip")
#     elif 22 <= has_applied_count:
#         print("  overload, process")
#         a = interview_apply_info[i][23:]
#         for j in a:
#             has_not_applied_candidate.append(j)
#             interview_apply_info[i].remove(j)
#
# for i in list(interview_apply_info.keys()):
#     has_applied_count = len(interview_apply_info[i])
#     if has_applied_count < 17:
#         print("  not enough, add to somewhere else")
#         lost = 16 - has_applied_count
#         for j in range(0, lost):
#             pick_j = random.randint(0, len(has_not_applied_candidate))
#             try:
#                 print("  random pick %s" % has_not_applied_candidate[pick_j])
#                 interview_apply_info[i].append(has_not_applied_candidate[pick_j])
#                 has_not_applied_candidate.remove(has_not_applied_candidate[pick_j])
#             except IndexError:
#                 print("  error! no left not applied candidate")
#                 continue
#
# json.dump(interview_apply_info, open("./data/json/interview_apply_info_re_assigned.json", "w", encoding="utf-8"))

interview_apply_info = json.load(open("./data/json/interview_apply_info_all.json", "r", encoding="utf-8"))
for i in list(interview_apply_info.keys()):
    print(" now process enterprise-%s, has been applied-%s" % (i, len(interview_apply_info[i])))
    candidate_list = interview_apply_info[i]
    processed = []
    for j in candidate_list:
        if j[-1] == "1":
            processed.insert(0, j)
        elif j[-1] == "2":
            processed.insert(-1, j)

    interview_apply_info[i] = processed

print(interview_apply_info)

interview_apply_info = json.load(open("./data/json/interview_apply_info_re_assigned.json", "r", encoding="utf-8"))
#
# for e_i in list(interview_apply_info.keys()):
#
#     print("now process enterprise-%s" % e_i)
#
#     for candidate_id in interview_apply_info[e_i]:
#         if not mongodb.update_many_documents("candidate", candidate_id, {"_id": 8}, {"appliedEnterprise": int(e_i)}):
#             print("  update %s's appliedEnterprise failed" % candidate_id)
#
#     mongodb.update_many_documents("interview", "apply", {"_id": int(e_i)}, {"applied": interview_apply_info[e_i]})

# now_remain_list = list(mongodb.get_document("interview", "temp", mode=0))
# candidate_ids = mongodb.get_collection_names_list("candidate")
#
# for candidate_id in candidate_ids:
#
#     print("process candidate-%s" % candidate_id)
#     a_e = mongodb.parse_document_result(
#         mongodb.get_document("candidate", candidate_id, {"_id": 8}, 1),
#         ["appliedEnterprise"]
#     )[0]["appliedEnterprise"]
#
#     if a_e == 0 or a_e == "0":
#         while True:
#             pick_a_e = random.randint(1, 112)
#             if now_remain_list[pick_a_e]["data"] > 0:
#                 now_remain_list[pick_a_e]["data"] -= 1
#                 enterprise_applied = mongodb.parse_document_result(
#                     mongodb.get_document("interview", "apply", {"_id": pick_a_e}, 1),
#                     ["applied"])[0]["applied"]
#                 mongodb.update_many_documents("candidate", candidate_id, {"_id": 8}, {"appliedEnterprise": pick_a_e})
#                 enterprise_applied.append(candidate_id)
#                 mongodb.update_many_documents("interview", "apply", {"_id": pick_a_e}, {"applied": enterprise_applied})
#                 break
#
# mongodb.update_many_documents("interview", "temp", {"data": 1}, now_remain_list)
