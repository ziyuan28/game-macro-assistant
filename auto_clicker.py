import os
import json
import ctypes
import time
import random
import threading
import keyboard
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

# ==========================================
# --- 设置现代 UI 主题 ---
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ==========================================
# --- Windows Ctypes 底层硬件输入 ---
# ==========================================
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_short), ("wParamH", ctypes.c_ushort)]
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_) 
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def release_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def mouse_click(button="LEFT"):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    flags_down = 0x0002 if button == "LEFT" else 0x0008
    flags_up = 0x0004 if button == "LEFT" else 0x0010
    ii_.mi = MouseInput(0, 0, 0, flags_down, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_) 
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    time.sleep(random.uniform(0.05, 0.12)) 
    ii_.mi = MouseInput(0, 0, 0, flags_up, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

SCAN_CODES = {
    '1':0x02, '2':0x03, '3':0x04, '4':0x05, '5':0x06, '6':0x07,
    'Q':0x10, 'W':0x11, 'E':0x12, 'R':0x13, 'T':0x14,
    'A':0x1E, 'S':0x1F, 'D':0x20, 'F':0x21, 'G':0x22,
    'Z':0x2C, 'X':0x2D, 'C':0x2E, 'V':0x2F,
    'SPACE':0x39, 'SHIFT':0x2A, 'CTRL':0x1D, 'ALT':0x38, 'TAB':0x0F
}

# ==========================================
# --- 数据管理 ---
# ==========================================
DATA_FILE = "my_macros.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {
        "挂机回血": "按键 4\n等待 24",
        "自动连招": "按键 Q\n等待 0.5\n左键\n等待 0.5\n右键"
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

scripts_data = load_data()
is_running = False

# ==========================================
# --- 纯中文白话文解析引擎 ---
# ==========================================
def parse_and_execute(script_text):
    global is_running
    lines = [line.strip().upper() for line in script_text.strip().split('\n') if line.strip()]
    
    while is_running:
        for line in lines:
            if not is_running: break
            parts = line.split()
            if not parts: continue
            cmd = parts[0]
            
            if cmd == '等待' and len(parts) >= 2:
                try:
                    base_wait = float(parts[1])
                    actual_wait = base_wait + random.uniform(-base_wait*0.05, base_wait*0.05)
                    steps = int(actual_wait / 0.1)
                    for _ in range(steps):
                        if not is_running: break
                        time.sleep(0.1)
                except: pass
            
            elif cmd == '左键':
                mouse_click("LEFT")
            elif cmd == '右键':
                mouse_click("RIGHT")
                
            elif cmd in ['按键', '长按', '松开'] and len(parts) >= 2:
                arg = parts[1]
                if arg in SCAN_CODES:
                    code = SCAN_CODES[arg]
                    if cmd == '长按': press_key(code)
                    elif cmd == '松开': release_key(code)
                    elif cmd == '按键':
                        press_key(code)
                        time.sleep(random.uniform(0.05, 0.15)) 
                        release_key(code)

# ==========================================
# --- UI 界面逻辑 ---
# ==========================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # 【水印 1】：窗口标题栏水印
        self.title("自动化小助手")
        self.geometry("750x520")
        self.attributes('-topmost', True)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 左侧菜单栏 ---
        self.left_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self.left_frame, text="📁 我的脚本库", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.script_listbox = tk.Listbox(self.left_frame, bg="#2b2b2b", fg="white", font=("Microsoft YaHei", 11), selectbackground="#1f538d", borderwidth=0, highlightthickness=0)
        self.script_listbox.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.script_listbox.bind('<<ListboxSelect>>', self.on_select_script)
        
        self.btn_new = ctk.CTkButton(self.left_frame, text="➕ 新建", command=self.new_script)
        self.btn_new.grid(row=3, column=0, padx=20, pady=(0, 10))
        
        self.btn_delete = ctk.CTkButton(self.left_frame, text="🗑️ 删除", fg_color="#8a2e2e", hover_color="#a83232", command=self.delete_script)
        self.btn_delete.grid(row=4, column=0, padx=20, pady=(0, 20))

        # --- 右侧编辑区 ---
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.right_frame.grid_rowconfigure(3, weight=1)

        self.name_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.name_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(self.name_frame, text="脚本名称:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.entry_name = ctk.CTkEntry(self.name_frame, width=250, font=ctk.CTkFont(size=14))
        self.entry_name.pack(side="left")
        
        self.btn_save = ctk.CTkButton(self.name_frame, text="💾 保存脚本", width=100, command=self.save_script)
        self.btn_save.pack(side="right")

        self.toolbar = ctk.CTkFrame(self.right_frame, height=40)
        self.toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkButton(self.toolbar, text="⏱️ 插入等待", width=80, fg_color="#3a7ebf", command=lambda: self.insert_text("等待 1.0\n")).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(self.toolbar, text="⌨️ 插入按键", width=80, fg_color="#3a7ebf", command=lambda: self.insert_text("按键 F\n")).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(self.toolbar, text="🖱️ 鼠标左键", width=80, fg_color="#3a7ebf", command=lambda: self.insert_text("左键\n")).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(self.toolbar, text="🖱️ 鼠标右键", width=80, fg_color="#3a7ebf", command=lambda: self.insert_text("右键\n")).pack(side="left", padx=5, pady=5)
        
        tips = "支持语法: 按键 X | 等待 X | 左键 | 右键 | 长按 X | 松开 X"
        ctk.CTkLabel(self.right_frame, text=tips, text_color="gray").grid(row=2, column=0, sticky="w")

        self.textbox = ctk.CTkTextbox(self.right_frame, font=ctk.CTkFont(family="Consolas", size=14))
        self.textbox.grid(row=3, column=0, sticky="nsew")

        # 4. 底部状态栏与作者水印
        self.status_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.status_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="○ 状态: 已停止 (F11 开启 / F12 停止)", font=ctk.CTkFont(size=15, weight="bold"), text_color="#dce4ee")
        self.status_label.pack(side="left")

       
        keyboard.add_hotkey('f11', self.start_running)
        keyboard.add_hotkey('f12', self.stop_running)
        self.refresh_list()
        if scripts_data:
            self.script_listbox.selection_set(0)
            self.on_select_script(None)

    def insert_text(self, text):
        self.textbox.insert(tk.INSERT, text)
        
    def refresh_list(self):
        self.script_listbox.delete(0, tk.END)
        for name in scripts_data.keys():
            self.script_listbox.insert(tk.END, name)

    def on_select_script(self, event):
        selection = self.script_listbox.curselection()
        if selection:
            name = self.script_listbox.get(selection[0])
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, name)
            self.textbox.delete("1.0", tk.END)
            self.textbox.insert("1.0", scripts_data[name])

    def new_script(self):
        self.script_listbox.selection_clear(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.textbox.delete("1.0", tk.END)
        self.entry_name.focus()

    def save_script(self):
        name = self.entry_name.get().strip()
        code = self.textbox.get("1.0", tk.END).strip()
        if not name:
            messagebox.showwarning("提示", "起个响亮的名字吧！")
            return
        scripts_data[name] = code
        save_data(scripts_data)
        self.refresh_list()
        idx = list(scripts_data.keys()).index(name)
        self.script_listbox.selection_clear(0, tk.END)
        self.script_listbox.selection_set(idx)

    def delete_script(self):
        name = self.entry_name.get().strip()
        if name in scripts_data and messagebox.askyesno("确认", f"删除 [{name}]？"):
            del scripts_data[name]
            save_data(scripts_data)
            self.refresh_list()
            self.new_script()

    def start_running(self):
        global is_running
        if not is_running:
            is_running = True
            self.status_label.configure(text="● 状态: 运行中... (按 F12 停止)", text_color="#2ecc71")
            code = self.textbox.get("1.0", tk.END)
            threading.Thread(target=parse_and_execute, args=(code,), daemon=True).start()

    def stop_running(self):
        global is_running
        is_running = False
        self.status_label.configure(text="○ 状态: 已停止 (F11 开启)", text_color="#dce4ee")

if __name__ == "__main__":
    app = App()
    app.mainloop()