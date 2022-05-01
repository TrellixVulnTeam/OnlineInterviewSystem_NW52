# # coding=utf-8
# # main.py
# # author: Lan_zhijiang
# # mail: lanzhijiang@foxmail.com
# # date: 2022/04/24
# # description: interviewer client web browser module
#
# from cefpython3 import cefpython as cef
#
# from tkinter import *
# import threading
# import sys
#
#
# def embed_browser_thread(frame, size, url):
#
#     """
#     内嵌浏览器线程
#     :param frame: 父tk frame
#     :param size: 窗口大小
#     :param url: 访问网址
#     :return:
#     """
#     sys.excepthook = cef.ExceptHook
#     window_info = cef.WindowInfo(frame.winfo_id())
#     window_info.SetAsChild(frame.winfo_id(), size)
#     cef.Initialize()
#     cef.CreateBrowserSync(window_info, url=url)
#     cef.MessageLoop()
#
#
# if __name__ == '__main__':
#     root = Tk()
#     root.geometry("1100x800")
#
#     frame1 = Frame(root, bg='blue', width=800, height=800)
#     # frame1.pack(side=LEFT)
#     frame1.grid()
#
#     frame2 = Frame(root, bg='white', height=50)
#     # frame2.pack(side=LEFT)
#     frame2.grid()
#
#     size = [0, 0, 800, 800]
#     thread = threading.Thread(target=embed_browser_thread, args=(frame1, size, "https://meeting.hadream.ltd"))
#     thread.start()
#
#     root.mainloop()
#
#