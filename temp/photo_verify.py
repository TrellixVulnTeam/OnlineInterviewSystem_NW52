# author: Lanzhijiang
# desc: 1 verify face 2 upload to database


from aip import AipFace
import os
import json
import base64
import shutil

import threading

# configuration of baidu aip face
APP_ID = '25984709'
API_KEY = 'YKOH4fw61niH0fhPxNLDnSHR'
SECRET_KEY = 'NiK4q5xtSGCrxTqErG2jKTLUg1XTLufH'


def read_img(img):
    """
    读取图片数据
    :return
    """
    try:
        file = open(img, "rb")
        return_data = file.read()
        file.close()
        return_data = str(base64.b64encode(return_data), "utf-8")
        return return_data
    except FileNotFoundError:
        return None


# step1: upload face
# user_id_list = json.load(open("./data/json/user_name_code_mapping.json", "r", encoding="utf-8"))
# pic_dir = "E:/2023各班照片/"
# all_pics_list = os.listdir(pic_dir)
# sub_dirs = {}
# for i in all_pics_list:
#     print(i)
#     if ".xls" in i or ".xlsx" in i:
#         all_pics_list.remove(i)
#     else:
#         a = os.listdir(pic_dir + i)
#         sub_dirs[i] = a
#
# # group_id = "all"
#
# for dir_name in all_pics_list:
#     print("now upload dir-%s" % dir_name)
#
#     for pic_name in sub_dirs[dir_name]:
#         print("now upload pic-%s" % pic_name)
#         pic_path = pic_dir + dir_name + "/" + pic_name
#         image = read_img(pic_path)
#         if image is None:
#             print(pic_path + " skip")
#             continue
#         try:
#             user_id = user_id_list[pic_name.replace(".jpg", "").replace(".png", "").replace(".JPG", "").replace(".PNG", "")]
#             group_id = "c" + str(int(user_id[0:2]))
#         except KeyError:
#             print("  person not exist now, skip")
#             continue
#         print("  user_id-%s to group_id-%s" % (user_id, group_id))
#         res = face_client.addUser(image, "BASE64", group_id, user_id)
#         try:
#             a = res["error_code"]
#             b = res["error_message"]
#         except KeyError:
#             pass
#         else:
#             print("  upload failed, code-%s, message-%s" % (a, b))
#         print("upload end")


def thread_search(order):

    pic_dir = "E:/个人照片/个人照片-原始数据/%s/" % order
    skip = []
    all_pics_list = os.listdir(pic_dir)

    face_client = AipFace(APP_ID, API_KEY, SECRET_KEY)

    for pic_name in all_pics_list:

        print("now search file-%s" % pic_name)
        file_type = pic_name[-5:]
        pic_path = pic_dir + pic_name

        if ".jpg" in file_type or ".png" in file_type or ".jpeg" in file_type:
            image = read_img(pic_path)
            if image is None:
                print("  file not exist, skip")
                continue
            res = face_client.search(image, "BASE64", "all")

            error_code = res["error_code"]
            error_msg = res["error_msg"]

            if error_code == 0:
                user_id = res["result"]["user_list"][0]["user_id"]
                score = res["result"]["user_list"][0]["score"]
                if score >= 70:
                    try:
                        name, file_type = os.path.splitext(pic_name)
                        os.rename(pic_path, "E:/个人照片/个人照片-审核通过/" + user_id + file_type)
                        print("  verify success, user_id-%s" % user_id)
                    except FileExistsError:
                        skip.append({"id": user_id, "file": pic_name})
                        print("  rename conflict, skip")
                        try:
                            shutil.move(pic_path, "E:/个人照片/个人照片-审核过/" + pic_name)
                        except FileNotFoundError:
                            pass
                        continue
                    except FileNotFoundError:
                        print("  file not exist, skip")
                        continue
                else:
                    print("  score low-%s, not pass-%s" % (score, user_id))
            else:
                print("  search failed, code-%s, message-%s" % (error_code, error_msg))
        else:
            shutil.move(pic_path, "E:/个人照片/个人照片-审核过/" + pic_name)
            print("  type-%s not support" % file_type)
            continue

        try:
            shutil.move(pic_path, "E:/个人照片/个人照片-审核过/" + pic_name)
        except FileNotFoundError:
            pass
        print("  search done")

    json.dump(skip, open("./data/json/photo_verify_skipped_1.json", "w", encoding="utf-8"))


thread_search_1 = threading.Thread(target=thread_search, args=("1",))
thread_search_2 = threading.Thread(target=thread_search, args=("2",))
thread_search_3 = threading.Thread(target=thread_search, args=("3",))
thread_search_1.start()
thread_search_2.start()
thread_search_3.start()

# pic_dir = "E:/个人照片/个人照片-审核通过/"
# all_pics_list = os.listdir(pic_dir)
# # for i in all_pics_list:
# #     user_id = i.replace(".jpg", "").replace(".jpeg", "")
# #     if user_id not in had:
# #         had.append(user_id)
# #         continue
# #     else:
# #         shutil.move(pic_dir + i, pic_dir + "重复/" + i)
#
# face_client = AipFace(APP_ID, API_KEY, SECRET_KEY)
# high_beauty = []
# skip = []
# for pic_name in all_pics_list:
#     print("now process: %s" % pic_name)
#     pic_path = pic_dir + pic_name
#     image = read_img(pic_path)
#     res = face_client.detect(image, "BASE64", options={"face_field": "beauty,gender"})
#
#     error_code = res["error_code"]
#     error_msg = res["error_msg"]
#
#     if error_code == 0:
#         user_id = pic_name.replace(".jpg", "").replace(".jpeg", "").replace(".png", "")
#         beauty_score = res["result"]["face_list"][0]["beauty"]
#         gender = res["result"]["face_list"][0]["gender"]["type"]
#         if beauty_score > 65.0:
#             if gender == "male":
#                 print(" handsome!!! %s" % user_id)
#             high_beauty.append({user_id: beauty_score})
#     else:
#         print("  detect failed, code-%s, message-%s" % (error_code, error_msg))
#
# json.dump(high_beauty, open("./data/json/highbeauty_list.json", "w", encoding="utf-8"))

