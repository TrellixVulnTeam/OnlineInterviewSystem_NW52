# pick volunteer

import xlrd
import json
import random

file_name = "./data/志愿者.xls"
# sheet = xlrd.open_workbook(file_name).sheet_by_index(0)
class_1 = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 15, 16, 17, 18]
class_2 = [7, 8, 9, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]

# sheet.cell_value(row_c, 0)
# result = {
#     "1": [],
#     "2": []
# }
#
# for c_i in range(1, 11):
#     if len(str(c_i)) == 1:
#         c_i_str = "0%s" % c_i
#     else:
#         c_i_str = str(c_i)
#     for r_i in range(1, 32):
#         if len(str(r_i)) == 1:
#             r_i_str = "0%s" % r_i
#         else:
#             r_i_str = str(r_i)
#
#         log = r_i_str + c_i_str
#         name = sheet.cell_value(r_i, c_i)
#         if name != "":
#             if r_i in class_1:
#                 result["1"].append({"name": name, "log": log})
#             else:
#                 result["2"].append({"name": name, "log": log})
#
# json.dump(result, open("./data/json/volunteer_list.json", "w", encoding="utf-8"))

volunteer_list = json.load(open("./data/json/volunteer_list.json", "r", encoding="utf-8"))
pick_p = "2"
list_ = volunteer_list[pick_p]
pick_num = 56
have_picked = []
result = []

for i in range(0, pick_num):

    while True:
        j = random.randint(0, len(list_)-1)
        if j not in have_picked:
            have_picked.append(j)
            result.append(list_[j])
            break

p_r = ""
for i in result:
    p_r = p_r + " " + i["name"]

print(result)
print(p_r)