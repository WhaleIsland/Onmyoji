# -*- coding:utf-8 -*-
import os
import sys
import threading
import tkinter as tk
import tkinter.scrolledtext as tks
import multiprocessing as mult

from tkinter import messagebox as mes
from Action import Mitama, insert_text

tasks = []

def ready_mitama(area):
    function = Mitama()

    mes.showinfo('提示', '请确认账号进入组队房间并且锁定阵容')
    th = threading.Thread(target=Mitama.run, args=(function, area))
    th.start()
    tasks.append(function)


def finish_mitama(area):
    global tasks

    for task in tasks:
        task.terminate()
    area.configure(state=tk.NORMAL)
    area.delete(1.0, tk.END)
    insert_text(area, '脚本已经终止')
    tasks = []


def twofold_call():
    global function


def resource_path(param):
    def resource_path(relative_path):
        base_path = getattr(
            sys, '_MEIPASS', os.path.dirname(
                os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)


class MainWidget:

    def __init__(self):
        self.app = tk.Tk()
        self.init_widget()

    def init_widget(self):
        self.app.geometry('600x371')
        self.app.resizable(0, 0)
        self.app.title('小纸人')
        self.app.iconbitmap('UI/favicon.ico')

        canvas = tk.Canvas(self.app, width=600, height=371, bd=0, highlightthickness=0)
        # background_img_file = resource_path("background.png")
        background_img_file = 'UI/background.png'
        background_img = tk.PhotoImage(file=background_img_file)
        canvas.create_image(300, 185, image=background_img)

        canvas.create_text(300, 75, text='日志', font=('方正北魏楷书_GBK', 18), fill='#f1e5af')
        log_area = tks.ScrolledText(canvas, width=40, height=10, font=('方正北魏楷书_GBK', 14), state=tk.DISABLED)
        canvas.create_window(470, 200, window=log_area)

        # start_mitama_file = resource_path('mitama.png')
        start_mitama_file = 'UI/mitama.png'
        start_mitama = tk.PhotoImage(file=start_mitama_file)
        start_btn = tk.Button(canvas, image=start_mitama, bd=-1, highlightthickness=0,
                              command=lambda: ready_mitama(log_area))
        canvas.create_window(119, 125, window=start_btn)

        # end_mitama_file = resource_path('mitama-end.png')
        end_mitama_file = 'UI/mitama-end.png'
        end_mitama = tk.PhotoImage(file=end_mitama_file)
        end_btn = tk.Button(canvas, image=end_mitama, bd=-1, highlightthickness=0,
                              command=lambda: finish_mitama(log_area))
        canvas.create_window(119, 195, window=end_btn)


        canvas.pack()
        self.app.mainloop()


if __name__ == '__main__':
    mult.freeze_support()
    app = MainWidget()
