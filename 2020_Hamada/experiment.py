# coding: utf-8

import random
import json
import datetime
import tkinter
from tkinter import messagebox
from os import makedirs
from os.path import splitext, isfile

import argparse
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outd", default="rslts")
    parser.add_argument("--tmpd", default="tmp")
    parser.add_argument("--id2conditions", default="./id2conditions.json")
    parser.add_argument("--experimenter_height", type=int, default=250)
    parser.add_argument("--experimenter_width", type=int, default=600)
    parser.add_argument("--graph_height", type=int, default=600)
    parser.add_argument("--graph_width", type=int, default=500)
    parser.add_argument("--graph_color_now", default="red")
    parser.add_argument("--graph_color_old", default="green")
    parser.add_argument("--graph_color_other", default="blue")
    parser.add_argument("--other_score_range", type=float, nargs=2, default=[0.75, 0.85])
    parser.add_argument("--seed", type=int, default=123)
    return parser.parse_args()


class App(tkinter.Frame):
    def __init__(self, root, args):
        # super(App, self).__init__()
        super().__init__(root)
        self.pack()
        with open(args.id2conditions) as fd:
            self.id2conditions = json.load(fd)
        self.args = args

        self.results = {"subject-ID": None, "date": str(datetime.datetime.now()), "practice": [], "a1b1": [], "a1b2": [], "a2b1": [], "a2b2": []}

        self.root = root
        self.root.title("For Experimenter")
        self.root.geometry("%dx%d" %(args.experimenter_width, args.experimenter_height))

        # 被験者IDの管理
        label_ID = tkinter.Label(text="被験者ID")
        label_ID.place(x=0, y=0)
        self.entry_ID = tkinter.Entry(width=5)
        self.entry_ID.place(x=80, y=0)

        # 状況確認
        self.n_condition = ""
        self.conditions = [""]
        self.condition = tkinter.StringVar()
        self.condition.set("被験者IDを入力して，【set】を押す")
        label_condtion = tkinter.Label(textvariable=self.condition)
        label_condtion.place(x=200, y=0)

        self.newWindow = tkinter.Toplevel(self.root)
        self.graph = Graph(self.newWindow, args)

        self.main()
        self.draw_buttons()

    def main(self):
        # 1試行目の結果
        label_0_1 = tkinter.Label(text="スコア")
        label_0_1.place(x=100, y=60)
        label_0_2 = tkinter.Label(text="平均タイピング数")
        label_0_2.place(x=160, y=60)
        label_0_3 = tkinter.Label(text="ミスタイプ数")
        label_0_3.place(x=270, y=60)

        ## タスク1回目の結果
        label_0 = tkinter.Label(text="タスク1回目")
        label_0.place(x=0, y=80)
        self.entry_1_1 = tkinter.Entry(width=5)
        self.entry_1_1.place(x=100, y=80)
        self.entry_1_2 = tkinter.Entry(width=5)
        self.entry_1_2.place(x=160, y=80)
        self.entry_1_3 = tkinter.Entry(width=5)
        self.entry_1_3.place(x=270, y=80)

        ## タスク2回目の結果
        label_2_1 = tkinter.Label(text="タスク2回目")
        label_2_1.place(x=0, y=110)
        self.entry_2_1 = tkinter.Entry(width=5)
        self.entry_2_1.place(x=100, y=110)
        self.entry_2_2 = tkinter.Entry(width=5)
        self.entry_2_2.place(x=160, y=110)
        self.entry_2_3 = tkinter.Entry(width=5)
        self.entry_2_3.place(x=270, y=110)

        ## タスク3回目の結果
        label_2_1 = tkinter.Label(text="タスク3回目")
        label_2_1.place(x=0, y=140)
        self.entry_3_1 = tkinter.Entry(width=5)
        self.entry_3_1.place(x=100, y=140)
        self.entry_3_2 = tkinter.Entry(width=5)
        self.entry_3_2.place(x=160, y=140)
        self.entry_3_3 = tkinter.Entry(width=5)
        self.entry_3_3.place(x=270, y=140)

    def draw_buttons(self):
        self.button_0 = tkinter.Button(text="set", width=4, command=self.button_0)
        self.button_0.place(x=150, y=0)
        self.button_1 = tkinter.Button(text="グラフを表示する", width=12, command=self.button_1, state=tkinter.DISABLED)
        self.button_1.place(x=350, y=110)
        self.button_2 = tkinter.Button(text="グラフを初期化", width=12, command=self.button_2, state=tkinter.DISABLED)
        self.button_2.place(x=450, y=110)
        self.button_3 = tkinter.Button(text="次の条件へ", width=12, command=self.button_3, state=tkinter.DISABLED)
        self.button_3.place(x=350, y=140)
        self.button_4 = tkinter.Button(text="Graphを再配置", width=12, command=self.button_4)
        self.button_4.place(x=450, y=140)
        self.button_5 = tkinter.Button(text="保存して終了", width=14, command=self.button_5, state=tkinter.DISABLED)
        self.button_5.place(x=200, y=200)

    def button_0(self):
        ID = int(self.entry_ID.get())
        if 1<=ID<=24:
            pass
        elif ID==0:
            messagebox.showinfo("Information", "プレ実験を開始します")
        elif ID<1:
            messagebox.showerror("Error", "被験者IDは0以上の整数値である必要があります\nただし0はプレ実験用のダミーIDです")
            return 0
        else:
            ID = ID % 24
            if ID==0:
                ID = 24
        self.results["subject-ID"] = str(ID)
        self.conditions = ["practice"]
        self.conditions.extend(self.id2conditions[str(ID)])
        self.n_condition = 0
        self.condition.set("%s条件目（%s）" %(self.n_condition, self.conditions[self.n_condition]))
        self.button_0["state"] = tkinter.DISABLED
        self.button_1["state"] = tkinter.NORMAL
        self.button_2["state"] = tkinter.NORMAL
        self.button_3["state"] = tkinter.NORMAL

    def button_1(self):
        score_now = int(self.entry_2_1.get())
        score_old = int(self.entry_1_1.get())
        self.graph.draw_graph(score_now, score_old, self.conditions[self.n_condition])

    def button_2(self):
        self.graph.graph_init()

    def button_3(self):
        self.results[self.conditions[self.n_condition]] = [\
            self.entry_1_1.get(), self.entry_1_2.get(), self.entry_1_3.get(), \
            self.entry_2_1.get(), self.entry_2_2.get(), self.entry_2_3.get(), \
            self.entry_3_1.get(), self.entry_3_2.get(), self.entry_3_3.get(), \
        ]
        try:
            self.results[self.conditions[self.n_condition]] = list(map(int, self.results[self.conditions[self.n_condition]]))
        except ValueError:
            messagebox.showwarning("Warning", "全てのスコアが入力されていません．\n全てのスコアを入力してもう一度ボタンを押してください．")
            return 1
        self.entry_1_1.delete(0, tkinter.END)
        self.entry_1_2.delete(0, tkinter.END)
        self.entry_1_3.delete(0, tkinter.END)
        self.entry_2_1.delete(0, tkinter.END)
        self.entry_2_2.delete(0, tkinter.END)
        self.entry_2_3.delete(0, tkinter.END)
        self.entry_3_1.delete(0, tkinter.END)
        self.entry_3_2.delete(0, tkinter.END)
        self.entry_3_3.delete(0, tkinter.END)
        self.n_condition += 1
        if self.n_condition<=4:
            self.condition.set("%s条件目（%s）" %(self.n_condition, self.conditions[self.n_condition]))
        else:
            self.condition.set("終了してください")
            self.button_1["state"] = tkinter.DISABLED
            self.button_2["state"] = tkinter.DISABLED
            self.button_3["state"] = tkinter.DISABLED
            self.button_5["state"]=tkinter.NORMAL
        outf = "%s/%s.json" %(args.tmpd, self.results["subject-ID"].zfill(3))
        save_file(outf, self.results)
        self.graph.graph_init()
        return 0

    def button_4(self):
        self.newWindow = tkinter.Toplevel(self.root)
        self.graph = Graph(self.newWindow, self.args)

    def button_5(self):
        outf = "%s/%s.json" %(args.outd, self.results["subject-ID"].zfill(3))
        save_file(outf, self.results)
        exit()

def save_file(outf, d, overwrite_check=True, indent=2):
    cnt = 1
    _outf = outf
    while overwrite_check:
        if isfile(outf):
            outf = "%s.%d.json" %(splitext(_outf)[0], cnt)
            cnt += 1
        else:
            overwrite_check = False
    with open(outf, "w") as fd:
        json.dump(d, fd, indent=indent)


class Graph(tkinter.Frame):
    def __init__(self, root, args):
        super().__init__(root)
        self.root = root
        self.pack()
        self.root.title("Graph")
        self.root.geometry("%dx%d" %(args.graph_width, args.graph_height))
        self.canvas = tkinter.Canvas(self.root, width=args.graph_width, height=args.graph_height)
        self.args = args

    def graph_init(self):
        self.canvas.delete("all")

    def draw_graph(self, score_now, score_old, condition):
        """
        A: 他者比較（a1 見せる，a2 見せない）
        B: 過去比較（b1 見せる，b2 見せない）
        """
        mag = random.uniform(*self.args.other_score_range)
        score_other = int(round(score_now * mag))
        if condition=="practice":
            pass
        else:
            if condition.find("a1")>=0:
                pass
            elif condition.find("a2")>=0:
                score_other = -1
            if condition.find("b1")>=0:
                pass
            elif condition.find("b2")>=0:
                score_old = -1
            if score_other==-1 and score_old==-1:
                score_now = 0
        
        # create_rectangle(x1, y1, x2, y2)
        values = []
        for v in (score_now, score_old, score_other):
            if v>=0:
                values.append(v)
        vmax, vmin = max(values), min(values)
        a = (400 - 100) / (vmin - vmax)
        b = 400 - (vmin * a)

        if score_now>=0:
            top_1 = int(a * score_now + b)
            self.canvas.create_rectangle(0, top_1, 100, 500, fill=self.args.graph_color_now)
            self.canvas.create_text(50, 550, text="あなたの\n今回の成績", font=("Helvetica", 12, "bold"))
            self.canvas.create_text(50, top_1-10, text=str(score_now), font=("Helvetica", 12, "bold"))
        if score_old>=0:
            top_2 = int(a * score_old + b)
            self.canvas.create_rectangle(150, top_2, 250, 500, fill=self.args.graph_color_old)
            self.canvas.create_text(200, 550, text="あなたの\n過去の成績", font=("Helvetica", 12, "bold"))
            self.canvas.create_text(200, top_2-10, text=str(score_old), font=("Helvetica", 12, "bold"))        
        if score_other>=0:
            top_3 = int(a * score_other + b)
            self.canvas.create_rectangle(300, top_3, 400, 500, fill=self.args.graph_color_other)
            self.canvas.create_text(350, 550, text="他の人の\n今回の成績", font=("Helvetica", 12, "bold"))
            self.canvas.create_text(350, top_3-10, text=str(score_other), font=("Helvetica", 12, "bold"))        
            self.canvas.pack()


def main(args):
    root = tkinter.Tk()
    app = App(root, args)
    app.mainloop()

if __name__=="__main__":
    args = get_args()
    random.seed(args.seed)
    makedirs(args.outd, exist_ok=True)
    makedirs(args.tmpd, exist_ok=True)
    main(args)
