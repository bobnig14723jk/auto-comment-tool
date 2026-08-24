import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyautogui
import pyperclip
import threading
import time
import random
from datetime import datetime, timedelta

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


class CommentAutoSender:

    def __init__(self, root):
        self.root = root
        self.root.title("自动评论发布工具")
        self.root.geometry("620x760")
        self.root.resizable(False, False)

        self.bg_color = '#FFF5EB'
        self.primary_color = '#FF8C00'
        self.accent_color = '#FFA500'
        self.dark_text = '#333333'

        self.root.configure(bg=self.bg_color)

        self.input_x = tk.StringVar(value="0")
        self.input_y = tk.StringVar(value="0")
        self.send_x = tk.StringVar(value="0")
        self.send_y = tk.StringVar(value="0")
        self.send_time = tk.StringVar(value="")
        self.interval = tk.StringVar(value="5")
        self.interval_random = tk.BooleanVar(value=False)
        self.interval_min = tk.StringVar(value="20")
        self.interval_max = tk.StringVar(value="50")
        self.click_min = tk.StringVar(value="0.2")
        self.click_max = tk.StringVar(value="0.5")
        self.run_mode = tk.StringVar(value="loop")
        self.repeat = tk.StringVar(value="10")
        self.duration = tk.StringVar(value="60")
        self.running = False
        self.picking_target = None

        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self.root, bg=self.primary_color, height=52)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="自动评论发布工具",
                 font=("微软雅黑", 16, "bold"),
                 bg=self.primary_color, fg='white').pack(pady=12)

        # 滚动容器
        scroll_container = tk.Frame(self.root, bg=self.bg_color)
        scroll_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(scroll_container, bg=self.bg_color,
                                highlightthickness=0)
        self.scrollbar = tk.Scrollbar(scroll_container, orient="vertical",
                                      command=self.canvas.yview, width=24)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content = tk.Frame(self.canvas, bg=self.bg_color)
        self.canvas_window = self.canvas.create_window((0, 0), window=content,
                                                       anchor="nw")

        content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # --- 话术 ---
        comment_frame = tk.LabelFrame(content, text=" 话术设置（每行一条，按顺序循环发送） ",
                                     font=("微软雅黑", 10, "bold"),
                                     bg=self.bg_color, fg=self.dark_text)
        comment_frame.pack(fill=tk.X, pady=(0, 8))

        # 话术工具栏
        tool_row = tk.Frame(comment_frame, bg=self.bg_color)
        tool_row.pack(fill=tk.X, padx=10, pady=(8, 3))
        self.comment_count_label = tk.Label(tool_row, text="共 0 条话术",
                                            bg=self.bg_color, fg='#FF4500',
                                            font=("微软雅黑", 9, "bold"))
        self.comment_count_label.pack(side=tk.LEFT)
        tk.Label(tool_row, text="（回车换行添加下一条）",
                 bg=self.bg_color, font=("微软雅黑", 8), fg='#888888').pack(side=tk.LEFT, padx=(5, 0))

        # 话术编辑区 - 带行号背景的文本框
        text_container = tk.Frame(comment_frame, bg='white',
                                 highlightbackground='#CCCCCC',
                                 highlightthickness=1)
        text_container.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.line_numbers = tk.Text(text_container, width=4, padx=6, pady=4,
                                    bg='#F0F0F0', fg='#999999',
                                    font=("微软雅黑", 10),
                                    state=tk.DISABLED, relief=tk.FLAT,
                                    takefocus=0, spacing1=0, spacing3=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.comment_text = tk.Text(text_container, height=6,
                                    font=("微软雅黑", 10),
                                    wrap=tk.WORD, relief=tk.FLAT,
                                    padx=8, pady=4, bg='white',
                                    spacing1=0, spacing3=0)
        self.comment_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.comment_text.bind('<KeyRelease>', self._update_line_numbers)
        self.comment_text.bind('<MouseWheel>', self._on_mousewheel)
        self.comment_text.bind('<Button-1>', lambda e: self._update_line_numbers())
        self.comment_text.bind('<Configure>', lambda e: self._update_line_numbers())
        self.line_numbers.bind('<MouseWheel>', self._on_mousewheel)

        # 初始化行号
        self._update_line_numbers()

        # --- 坐标 ---
        coord_frame = tk.LabelFrame(content, text=" 坐标设置 ",
                                   font=("微软雅黑", 10, "bold"),
                                   bg=self.bg_color, fg=self.dark_text)
        coord_frame.pack(fill=tk.X, pady=(0, 8))

        input_row = tk.Frame(coord_frame, bg=self.bg_color)
        input_row.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(input_row, text="评论输入框：", width=12,
                 bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)
        tk.Entry(input_row, textvariable=self.input_x, width=6,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=(0, 3))
        tk.Label(input_row, text="X", bg=self.bg_color).pack(side=tk.LEFT)
        tk.Entry(input_row, textvariable=self.input_y, width=6,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=(3, 10))
        tk.Label(input_row, text="Y", bg=self.bg_color).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(input_row, text="拾取坐标", command=lambda: self._pick_coordinate('input'),
                  bg=self.accent_color, fg='white', font=("微软雅黑", 8, "bold"),
                  relief=tk.RAISED, padx=8, cursor="hand2").pack(side=tk.LEFT)

        send_row = tk.Frame(coord_frame, bg=self.bg_color)
        send_row.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(send_row, text="发送按钮：", width=12,
                 bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)
        tk.Entry(send_row, textvariable=self.send_x, width=6,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=(0, 3))
        tk.Label(send_row, text="X", bg=self.bg_color).pack(side=tk.LEFT)
        tk.Entry(send_row, textvariable=self.send_y, width=6,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=(3, 10))
        tk.Label(send_row, text="Y", bg=self.bg_color).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(send_row, text="拾取坐标", command=lambda: self._pick_coordinate('send'),
                  bg=self.accent_color, fg='white', font=("微软雅黑", 8, "bold"),
                  relief=tk.RAISED, padx=8, cursor="hand2").pack(side=tk.LEFT)

        test_row = tk.Frame(coord_frame, bg=self.bg_color)
        test_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Button(test_row, text="测试点击输入框", command=self._test_input_click,
                  bg='#4CAF50', fg='white', font=("微软雅黑", 9),
                  relief=tk.RAISED, padx=10, cursor="hand2").pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(test_row, text="测试点击发送", command=self._test_send_click,
                  bg='#4CAF50', fg='white', font=("微软雅黑", 9),
                  relief=tk.RAISED, padx=10, cursor="hand2").pack(side=tk.LEFT)

        # --- 时间 ---
        time_frame = tk.LabelFrame(content, text=" 时间设置 ",
                                  font=("微软雅黑", 10, "bold"),
                                  bg=self.bg_color, fg=self.dark_text)
        time_frame.pack(fill=tk.X, pady=(0, 8))

        time_row = tk.Frame(time_frame, bg=self.bg_color)
        time_row.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(time_row, text="开始时间：", width=12,
                 bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)
        tk.Entry(time_row, textvariable=self.send_time, width=22,
                 font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(time_row, text="留空=立即执行",
                 bg=self.bg_color, font=("微软雅黑", 8), fg='#888888').pack(side=tk.LEFT)

        quick_row = tk.Frame(time_frame, bg=self.bg_color)
        quick_row.pack(fill=tk.X, padx=10, pady=(0, 5))
        for label, mins in [("立即", 0), ("1分钟", 1), ("5分钟", 5), ("10分钟", 10), ("30分钟", 30)]:
            tk.Button(quick_row, text=label,
                      command=lambda m=mins: self._set_quick_time(m),
                      bg=self.accent_color, fg='white', font=("微软雅黑", 8),
                      relief=tk.RAISED, padx=8, cursor="hand2").pack(side=tk.LEFT, padx=(0, 5))

        param_row = tk.Frame(time_frame, bg=self.bg_color)
        param_row.pack(fill=tk.X, padx=10, pady=(0, 5))
        tk.Label(param_row, text="发送间隔(秒)：", width=13,
                 bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)
        tk.Entry(param_row, textvariable=self.interval, width=6,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=(0, 20))

        # --- 防风控设置 ---
        anti_frame = tk.LabelFrame(content, text=" 防风控设置 ",
                                   font=("微软雅黑", 10, "bold"),
                                   bg=self.bg_color, fg=self.dark_text)
        anti_frame.pack(fill=tk.X, pady=(0, 8))

        # 发送间隔随机
        intv_row = tk.Frame(anti_frame, bg=self.bg_color)
        intv_row.pack(fill=tk.X, padx=10, pady=5)
        tk.Checkbutton(intv_row, text="随机发送间隔", variable=self.interval_random,
                       bg=self.bg_color, font=("微软雅黑", 9),
                       activebackground=self.bg_color).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(intv_row, text="最小", bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)
        tk.Entry(intv_row, textvariable=self.interval_min, width=5,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=3)
        tk.Label(intv_row, text="秒 ~", bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)
        tk.Entry(intv_row, textvariable=self.interval_max, width=5,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=3)
        tk.Label(intv_row, text="秒", bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)

        # 点击延迟随机
        click_row = tk.Frame(anti_frame, bg=self.bg_color)
        click_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Label(click_row, text="点击延迟随机：", width=12,
                 bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)
        tk.Entry(click_row, textvariable=self.click_min, width=5,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=3)
        tk.Label(click_row, text="秒 ~", bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)
        tk.Entry(click_row, textvariable=self.click_max, width=5,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=3)
        tk.Label(click_row, text="秒（每次点击前随机等待）",
                 bg=self.bg_color, font=("微软雅黑", 8), fg='#888888').pack(side=tk.LEFT, padx=(5, 0))

        # --- 运行模式 ---
        mode_frame = tk.LabelFrame(content, text=" 运行模式 ",
                                  font=("微软雅黑", 10, "bold"),
                                  bg=self.bg_color, fg=self.dark_text)
        mode_frame.pack(fill=tk.X, pady=(0, 8))

        mode_row = tk.Frame(mode_frame, bg=self.bg_color)
        mode_row.pack(fill=tk.X, padx=10, pady=5)
        tk.Radiobutton(mode_row, text="持续循环（手动停止）", variable=self.run_mode,
                       value="loop", bg=self.bg_color, font=("微软雅黑", 9),
                       activebackground=self.bg_color).pack(side=tk.LEFT, padx=(0, 15))
        tk.Radiobutton(mode_row, text="指定次数", variable=self.run_mode,
                       value="count", bg=self.bg_color, font=("微软雅黑", 9),
                       activebackground=self.bg_color).pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(mode_row, textvariable=self.repeat, width=6,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(mode_row, text="轮", bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)

        dur_row = tk.Frame(mode_frame, bg=self.bg_color)
        dur_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Label(dur_row, text="运行时长(分钟)：", width=14,
                 bg=self.bg_color, font=("微软雅黑", 9)).pack(side=tk.LEFT)
        tk.Entry(dur_row, textvariable=self.duration, width=6,
                 font=("微软雅黑", 9), justify=tk.CENTER).pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(dur_row, text="（0=不限时，到时间自动停止）",
                 bg=self.bg_color, font=("微软雅黑", 8), fg='#888888').pack(side=tk.LEFT)

        quick_dur_row = tk.Frame(mode_frame, bg=self.bg_color)
        quick_dur_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        tk.Label(quick_dur_row, text="快捷设置：", bg=self.bg_color,
                 font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=(0, 5))
        for label, mins in [("30分钟", 30), ("1小时", 60), ("2小时", 120), ("不限时", 0)]:
            tk.Button(quick_dur_row, text=label,
                      command=lambda m=mins: self.duration.set(str(m)),
                      bg=self.accent_color, fg='white', font=("微软雅黑", 8),
                      relief=tk.RAISED, padx=6, cursor="hand2").pack(side=tk.LEFT, padx=(0, 5))

        # --- 控制按钮 ---
        ctrl_frame = tk.Frame(content, bg=self.bg_color)
        ctrl_frame.pack(fill=tk.X, pady=(0, 8))
        self.start_btn = tk.Button(ctrl_frame, text="开始执行", command=self._start_sending,
                                  bg='#FF4500', fg='white', font=("微软雅黑", 13, "bold"),
                                  relief=tk.RAISED, padx=25, pady=6, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.stop_btn = tk.Button(ctrl_frame, text="停止", command=self._stop_sending,
                                 bg='#888888', fg='white', font=("微软雅黑", 13, "bold"),
                                 relief=tk.RAISED, padx=25, pady=6, state=tk.DISABLED,
                                 cursor="hand2")
        self.stop_btn.pack(side=tk.LEFT)

        # --- 状态 ---
        status_frame = tk.LabelFrame(content, text=" 运行状态 ",
                                    font=("微软雅黑", 10, "bold"),
                                    bg=self.bg_color, fg=self.dark_text)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10,
                                                     font=("Consolas", 9),
                                                     bg='#1E1E1E', fg='#4CAF50',
                                                     wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(content,
                 text="使用说明：1.填写话术  2.拾取坐标  3.设置时间和运行模式  4.点击开始\n"
                      "紧急停止：将鼠标快速移到屏幕左上角(0,0)即可触发安全停止",
                 bg=self.bg_color, font=("微软雅黑", 8), fg='#888888',
                 justify=tk.LEFT).pack(pady=(0, 5))

    def _update_line_numbers(self, event=None):
        try:
            text = self.comment_text.get("1.0", tk.END)
            lines = text.split('\n')
            # 统计非空行数（实际话术数）
            non_empty = len([l for l in lines if l.strip()])
            total_lines = len(lines) - 1 if lines and lines[-1] == '' else len(lines)
            if total_lines < 6:
                total_lines = 6

            self.line_numbers.config(state=tk.NORMAL)
            self.line_numbers.delete("1.0", tk.END)
            for i in range(1, total_lines + 1):
                self.line_numbers.insert(tk.END, f" {i}\n")
            self.line_numbers.config(state=tk.DISABLED)

            # 同步滚动位置
            try:
                pos = self.comment_text.yview()[0]
                self.line_numbers.yview_moveto(pos)
            except Exception:
                pass

            self.comment_count_label.config(text=f"共 {non_empty} 条话术")
        except Exception:
            pass

    def _on_mousewheel(self, event):
        self.root.after(10, self._update_line_numbers)

    def _on_content_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_canvas_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.status_text.see(tk.END)

    def _pick_coordinate(self, target):
        if self.picking_target:
            return
        self.picking_target = target
        label = "输入框" if target == "input" else "发送按钮"
        self._log(f"3秒后捕捉{label}坐标，请将鼠标移到目标位置...")

        def _capture():
            for i in range(3, 0, -1):
                self._log(f"  {i}秒...")
                time.sleep(1)
            x, y = pyautogui.position()
            if target == "input":
                self.input_x.set(str(x))
                self.input_y.set(str(y))
            else:
                self.send_x.set(str(x))
                self.send_y.set(str(y))
            self._log(f"已捕捉{label}坐标：({x}, {y})")
            self.picking_target = None

        threading.Thread(target=_capture, daemon=True).start()

    def _test_input_click(self):
        try:
            x, y = int(self.input_x.get()), int(self.input_y.get())
        except ValueError:
            messagebox.showwarning("提示", "坐标格式不正确！")
            return
        if x == 0 and y == 0:
            messagebox.showwarning("提示", "请先拾取输入框坐标！")
            return
        self._log(f"测试点击输入框：({x}, {y})")
        orig_x, orig_y = pyautogui.position()
        pyautogui.click(x, y)
        time.sleep(0.3)
        pyautogui.moveTo(orig_x, orig_y)

    def _test_send_click(self):
        try:
            x, y = int(self.send_x.get()), int(self.send_y.get())
        except ValueError:
            messagebox.showwarning("提示", "坐标格式不正确！")
            return
        if x == 0 and y == 0:
            messagebox.showwarning("提示", "请先拾取发送按钮坐标！")
            return
        self._log(f"测试点击发送按钮：({x}, {y})")
        orig_x, orig_y = pyautogui.position()
        pyautogui.click(x, y)
        time.sleep(0.3)
        pyautogui.moveTo(orig_x, orig_y)

    def _set_quick_time(self, minutes):
        if minutes == 0:
            self.send_time.set("")
        else:
            target = datetime.now() + timedelta(minutes=minutes)
            self.send_time.set(target.strftime("%Y-%m-%d %H:%M:%S"))

    def _start_sending(self):
        comments_raw = self.comment_text.get("1.0", tk.END).strip()
        if not comments_raw:
            messagebox.showwarning("提示", "请输入评论话术！")
            return
        comments = [c.strip() for c in comments_raw.split('\n') if c.strip()]
        if not comments:
            messagebox.showwarning("提示", "请输入评论话术！")
            return

        try:
            input_x, input_y = int(self.input_x.get()), int(self.input_y.get())
            send_x, send_y = int(self.send_x.get()), int(self.send_y.get())
        except ValueError:
            messagebox.showwarning("提示", "坐标格式不正确！")
            return

        if input_x == 0 and input_y == 0:
            messagebox.showwarning("提示", "请设置输入框坐标！")
            return
        if send_x == 0 and send_y == 0:
            messagebox.showwarning("提示", "请设置发送按钮坐标！")
            return

        try:
            interval = float(self.interval.get())
        except ValueError:
            messagebox.showwarning("提示", "发送间隔必须为数字！")
            return

        use_random_interval = self.interval_random.get()
        interval_min_val = 0
        interval_max_val = 0
        if use_random_interval:
            try:
                interval_min_val = float(self.interval_min.get())
                interval_max_val = float(self.interval_max.get())
                if interval_min_val < 0 or interval_max_val < 0:
                    raise ValueError
                if interval_min_val > interval_max_val:
                    interval_min_val, interval_max_val = interval_max_val, interval_min_val
            except ValueError:
                messagebox.showwarning("提示", "随机间隔必须为有效的数字（秒）！")
                return

        try:
            click_min_val = float(self.click_min.get())
            click_max_val = float(self.click_max.get())
            if click_min_val < 0 or click_max_val < 0:
                raise ValueError
            if click_min_val > click_max_val:
                click_min_val, click_max_val = click_max_val, click_min_val
        except ValueError:
            messagebox.showwarning("提示", "点击延迟必须为有效的数字（秒）！")
            return

        mode = self.run_mode.get()
        repeat = 0
        if mode == "count":
            try:
                repeat = int(self.repeat.get())
            except ValueError:
                messagebox.showwarning("提示", "重复次数必须为数字！")
                return
            if repeat < 1:
                messagebox.showwarning("提示", "重复次数至少为1！")
                return

        try:
            duration = float(self.duration.get())
        except ValueError:
            messagebox.showwarning("提示", "运行时长必须为数字！")
            return

        send_time_str = self.send_time.get().strip()
        send_time = None
        if send_time_str:
            try:
                send_time = datetime.strptime(send_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showwarning("提示", "时间格式不正确！\n格式：YYYY-MM-DD HH:MM:SS")
                return

        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        threading.Thread(target=self._send_loop,
                         args=(comments, send_time, interval, mode, repeat, duration,
                               input_x, input_y, send_x, send_y,
                               use_random_interval, interval_min_val, interval_max_val,
                               click_min_val, click_max_val),
                         daemon=True).start()

    def _send_loop(self, comments, send_time, interval, mode, repeat, duration,
                   input_x, input_y, send_x, send_y,
                   use_random_interval, interval_min_val, interval_max_val,
                   click_min_val, click_max_val):
        if send_time:
            now = datetime.now()
            wait_seconds = (send_time - now).total_seconds()
            if wait_seconds > 0:
                self._log(f"等待执行... 目标时间：{send_time.strftime('%Y-%m-%d %H:%M:%S')}")
                while wait_seconds > 0 and self.running:
                    mins, secs = divmod(int(wait_seconds), 60)
                    self._log(f"  倒计时：{mins:02d}:{secs:02d}")
                    time.sleep(min(5, wait_seconds))
                    wait_seconds -= 5
            if not self.running:
                self._log("已取消执行")
                self._reset_buttons()
                return

        end_time = None
        if duration > 0:
            end_time = datetime.now() + timedelta(minutes=duration)
            self._log(f"===== 开始执行（运行 {duration} 分钟，到 {end_time.strftime('%H:%M:%S')} 自动停止）=====")
        else:
            self._log("===== 开始执行（持续循环，手动停止）=====")

        count = 0
        round_num = 0

        while self.running:
            if end_time and datetime.now() >= end_time:
                self._log("===== 运行时长已到，自动停止 =====")
                break

            round_num += 1
            if mode == "count" and round_num > repeat:
                self._log(f"===== {repeat} 轮全部执行完成 =====")
                break

            for comment in comments:
                if not self.running:
                    break
                if end_time and datetime.now() >= end_time:
                    break

                count += 1
                display = comment if len(comment) <= 30 else comment[:30] + "..."
                self._log(f"第{round_num}轮 第{count}条：{display}")

                try:
                    orig_x, orig_y = pyautogui.position()

                    # 随机点击延迟（防风控）
                    click_delay1 = random.uniform(click_min_val, click_max_val)
                    time.sleep(click_delay1)
                    pyautogui.click(input_x, input_y)
                    time.sleep(0.5)

                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.2)
                    pyperclip.copy(comment)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.5)

                    # 发送按钮随机延迟
                    click_delay2 = random.uniform(click_min_val, click_max_val)
                    time.sleep(click_delay2)
                    pyautogui.click(send_x, send_y)
                    time.sleep(0.5)

                    pyautogui.moveTo(orig_x, orig_y)

                    self._log(f"  已发送：{display}")
                except Exception as e:
                    self._log(f"  发送失败：{str(e)}")

                if self.running and (not end_time or datetime.now() < end_time):
                    if mode == "count" and round_num >= repeat and comment == comments[-1]:
                        break
                    # 计算本次等待间隔
                    if use_random_interval:
                        wait_interval = random.uniform(interval_min_val, interval_max_val)
                    else:
                        wait_interval = interval
                    self._log(f"  等待 {wait_interval:.1f} 秒...")
                    slept = 0.0
                    while slept < wait_interval and self.running:
                        if end_time and datetime.now() >= end_time:
                            break
                        time.sleep(min(1.0, wait_interval - slept))
                        slept += 1.0

        self.running = False
        self._log(f"===== 执行结束，共发送 {count} 条 =====")
        self._reset_buttons()

    def _reset_buttons(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def _stop_sending(self):
        self.running = False
        self._log("正在停止...")
        self._reset_buttons()

    def on_closing(self):
        self.running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = CommentAutoSender(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
