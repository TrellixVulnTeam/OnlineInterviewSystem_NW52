import json

candidate_name_mapping = json.load(open("./data/json/candidate_name_code_mapping.json", "r", encoding="utf-8"))
apply_info_all = json.load(open("./data/json/interview_apply_info_all.json", "r", encoding="utf-8"))

apply_candidate_list = []
new_apply_info = apply_info_all

for i in list(apply_info_all.keys()):
    for candidate in apply_info_all[i]:
        if candidate in apply_candidate_list:
            # new_apply_info[i].remove(candidate)
            print(candidate)
        apply_candidate_list.append(candidate)

# json.dump(new_apply_info, open("./data/json/interview_apply_info_all_fixed.json", "w", encoding="utf-8"))


