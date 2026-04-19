import os
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from datetime import datetime
import time
import re

# カラー設定
SAPPHIRE_BLUE = "#0066CC"
DARK_GRAY = "#1A1A1A"
TEXT_COLOR = "#E0E0E0"

class SimpleRenamer(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # ウィンドウ設定
        self.title("SimpleRenamer - Premium Edition")
        self.width = 950
        self.height = 750
        self.geometry(f"{self.width}x{self.height}")
        
        # ウィンドウを中央に配置
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.geometry(f"+{x}+{y}")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.file_list = []
        self.undo_history = [] # 形式: {"type": "rename", "data": [(old, new), ...]} or {"type": "time", "data": [(path, old_atime, old_mtime), ...]}

        self._setup_ui()

    def _setup_ui(self):
        # メインフレーム
        self.main_frame = ctk.CTkFrame(self, fg_color=DARK_GRAY)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ヘッダー
        self.header_label = ctk.CTkLabel(
            self.main_frame, 
            text="SimpleRenamer + TimeDropper", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=SAPPHIRE_BLUE
        )
        self.header_label.pack(pady=(10, 10))

        # タブビュー
        self.tab_view = ctk.CTkTabview(
            self.main_frame, 
            fg_color="#222222", 
            segmented_button_selected_color=SAPPHIRE_BLUE,
            segmented_button_selected_hover_color="#0055AA",
            command=self.update_preview
        )
        self.tab_view.pack(fill="x", padx=40, pady=(0, 10))
        
        self.tab_rename = self.tab_view.add("Rename (リネーム)")
        self.tab_time = self.tab_view.add("Timestamp (日時変更)")

        self._setup_rename_tab()
        self._setup_time_tab()

        # プレビューエリア（共通）
        self.list_frame = ctk.CTkFrame(self.main_frame, fg_color="#252525", corner_radius=10)
        self.list_frame.pack(fill="both", expand=True, padx=40, pady=10)

        # プレビュー見出し
        self.list_header = ctk.CTkFrame(self.list_frame, fg_color="#333333", height=30)
        self.list_header.pack(fill="x")
        self.list_header.pack_propagate(False)

        self.header_left = ctk.CTkLabel(self.list_header, text="  現在のファイル名", font=ctk.CTkFont(size=12, weight="bold"))
        self.header_left.pack(side="left")
        self.header_right = ctk.CTkLabel(self.list_header, text="変更後のプレビュー  ", font=ctk.CTkFont(size=12, weight="bold"))
        self.header_right.pack(side="right")

        # スクロール可能なテキストエリア
        self.preview_text = ctk.CTkTextbox(
            self.list_frame, 
            fg_color="transparent", 
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.preview_text.configure(state="disabled")

        # ドラッグ＆ドロップ設定
        self.preview_text.drop_target_register(DND_FILES)
        self.preview_text.dnd_bind('<<Drop>>', self.on_drop)

        # フッターボタン（共通）
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=40, pady=(5, 15))

        self.undo_btn = ctk.CTkButton(
            self.button_frame, 
            text="Undo (元に戻す)", 
            command=self.execute_undo,
            fg_color="#444444",
            hover_color="#555555",
            state="disabled"
        )
        self.undo_btn.pack(side="left", padx=10)

        self.clear_btn = ctk.CTkButton(
            self.button_frame, 
            text="クリア", 
            command=self.clear_list,
            fg_color="#444444",
            hover_color="#555555"
        )
        self.clear_btn.pack(side="left", padx=10)

        self.execute_btn = ctk.CTkButton(
            self.button_frame, 
            text="実行", 
            command=self.execute_action,
            fg_color=SAPPHIRE_BLUE,
            hover_color="#0055AA",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.execute_btn.pack(side="right", padx=10)

        # ステータスバー
        self.status_label = ctk.CTkLabel(self.main_frame, text="ファイルをここにドロップしてください", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="bottom", pady=5)

    def _setup_rename_tab(self):
        # 名前入力
        self.rename_input_frame = ctk.CTkFrame(self.tab_rename, fg_color="transparent")
        self.rename_input_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.rename_input_frame, text="新しい名前:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(0, 10))
        self.name_entry = ctk.CTkEntry(
            self.rename_input_frame, 
            placeholder_text="uzura", 
            height=45, 
            font=ctk.CTkFont(size=18, weight="bold"),
            border_color=SAPPHIRE_BLUE,
            fg_color="#2B2B2B"
        )
        self.name_entry.pack(side="left", fill="x", expand=True)
        self.name_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        # ソート順
        self.sort_frame = ctk.CTkFrame(self.tab_rename, fg_color="transparent")
        self.sort_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.sort_frame, text="ソート順:").pack(side="left", padx=(0, 10))
        self.sort_var = ctk.StringVar(value="time_asc")
        sort_options = [
            ("タイムスタンプ (旧→新)", "time_asc"),
            ("タイムスタンプ (新→旧)", "time_desc"),
            ("ファイル名 (昇順)", "name_asc"),
            ("ファイル名 (降順)", "name_desc"),
        ]
        for text, val in sort_options:
            ctk.CTkRadioButton(self.sort_frame, text=text, variable=self.sort_var, value=val, command=self.update_preview, fg_color=SAPPHIRE_BLUE).pack(side="left", padx=10)

        # 連番設定
        self.seq_frame = ctk.CTkFrame(self.tab_rename, fg_color="transparent")
        self.seq_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.seq_frame, text="開始番号:").pack(side="left", padx=(0, 5))
        self.start_num_entry = ctk.CTkEntry(self.seq_frame, width=60, placeholder_text="1")
        self.start_num_entry.insert(0, "1")
        self.start_num_entry.pack(side="left", padx=(0, 20))
        self.start_num_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        ctk.CTkLabel(self.seq_frame, text="桁数:").pack(side="left", padx=(0, 5))
        self.digits_entry = ctk.CTkEntry(self.seq_frame, width=40, placeholder_text="3")
        self.digits_entry.insert(0, "3")
        self.digits_entry.pack(side="left")
        self.digits_entry.bind("<KeyRelease>", lambda e: self.update_preview())

    def _setup_time_tab(self):
        # 日時入力
        self.time_input_frame = ctk.CTkFrame(self.tab_time, fg_color="transparent")
        self.time_input_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.time_input_frame, text="設定日時:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(0, 10))
        self.time_entry = ctk.CTkEntry(
            self.time_input_frame, 
            height=45, 
            font=ctk.CTkFont(size=18, weight="bold"),
            border_color=SAPPHIRE_BLUE,
            fg_color="#2B2B2B"
        )
        self.time_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.time_entry.pack(side="left", fill="x", expand=True)
        self.time_entry.bind("<KeyRelease>", lambda e: self.update_preview())

        ctk.CTkButton(
            self.time_input_frame, 
            text="現在時刻", 
            width=80, 
            command=self.set_now_time,
            fg_color="#444444"
        ).pack(side="left", padx=10)

        # オプション
        self.time_opt_frame = ctk.CTkFrame(self.tab_time, fg_color="transparent")
        self.time_opt_frame.pack(fill="x", padx=20, pady=5)

        self.time_inc_var = ctk.BooleanVar(value=False)
        self.time_inc_cb = ctk.CTkCheckBox(
            self.time_opt_frame, 
            text="1秒ずつずらして設定 (連番化)", 
            variable=self.time_inc_var,
            command=self.update_preview,
            fg_color=SAPPHIRE_BLUE
        )
        self.time_inc_cb.pack(side="left", padx=10)

    def set_now_time(self):
        self.time_entry.delete(0, "end")
        self.time_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.update_preview()

    def on_drop(self, event):
        files = re.findall(r'\{.*?\}|\S+', event.data)
        files = [f.strip('{}') for f in files]
        
        added_count = 0
        for f in files:
            if os.path.isfile(f) and f not in self.file_list:
                self.file_list.append(f)
                added_count += 1
        
        self.status_label.configure(text=f"{added_count} 個のファイルを追加しました")
        self.update_preview()

    def get_sorted_files(self):
        sort_mode = self.sort_var.get()
        if sort_mode == "time_desc":
            return sorted(self.file_list, key=os.path.getmtime, reverse=True)
        elif sort_mode == "time_asc":
            return sorted(self.file_list, key=os.path.getmtime)
        elif sort_mode == "name_asc":
            return sorted(self.file_list)
        elif sort_mode == "name_desc":
            return sorted(self.file_list, reverse=True)
        return self.file_list

    def update_preview(self, *args):
        if not self.file_list:
            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.configure(state="disabled")
            return

        mode = self.tab_view.get()
        sorted_files = self.get_sorted_files()
        
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        
        if "Rename" in mode:
            base_name = self.name_entry.get() or "uzura"
            try:
                start_num = int(self.start_num_entry.get() or "1")
                digits = int(self.digits_entry.get() or "3")
            except ValueError:
                self.preview_text.insert("end", " 開始番号と桁数は数値で入力してください\n")
                self.preview_text.configure(state="disabled")
                return

            for i, old_path in enumerate(sorted_files, start_num):
                ext = os.path.splitext(old_path)[1]
                new_name = f"{base_name}_{i:0{digits}d}{ext}"
                line = f" {os.path.basename(old_path):<40} → {new_name}\n"
                self.preview_text.insert("end", line)
        else:
            dt_str = self.time_entry.get()
            try:
                base_ts = time.mktime(time.strptime(dt_str, "%Y-%m-%d %H:%M:%S"))
                is_inc = self.time_inc_var.get()
                for i, old_path in enumerate(sorted_files, 0):
                    ts = base_ts + (i if is_inc else 0)
                    new_dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                    line = f" {os.path.basename(old_path):<40} → {new_dt}\n"
                    self.preview_text.insert("end", line)
            except:
                self.preview_text.insert("end", " 正しくない日時形式です (YYYY-MM-DD HH:MM:SS)\n")
        
        self.preview_text.configure(state="disabled")

    def execute_action(self):
        if not self.file_list:
            self.status_label.configure(text="ファイルが選択されていません", text_color="#FF4444")
            return
        
        mode = self.tab_view.get()
        if "Rename" in mode:
            self.execute_rename()
        else:
            self.execute_timestamp_change()

    def execute_rename(self):
        base_name = self.name_entry.get() or "uzura"
        try:
            start_num = int(self.start_num_entry.get() or "1")
            digits = int(self.digits_entry.get() or "3")
        except ValueError:
            self.status_label.configure(text="開始番号と桁数は数値で入力してください", text_color="#FF4444")
            return

        sorted_files = self.get_sorted_files()
        history = []
        try:
            for i, old_path in enumerate(sorted_files, start_num):
                ext = os.path.splitext(old_path)[1]
                dir_path = os.path.dirname(old_path)
                new_path = os.path.join(dir_path, f"{base_name}_{i:0{digits}d}{ext}")
                os.rename(old_path, new_path)
                history.append((old_path, new_path))
            
            self.undo_history.append({"type": "rename", "data": history})
            self.undo_btn.configure(state="normal")
            self.file_list = [h[1] for h in history]
            self.update_preview()
            self.status_label.configure(text=f"成功: {len(history)} 個のファイルをリネームしました", text_color="#00FFCC")
        except Exception as e:
            self.status_label.configure(text=f"エラー: {str(e)}", text_color="#FF4444")

    def execute_timestamp_change(self):
        dt_str = self.time_entry.get()
        try:
            base_ts = time.mktime(time.strptime(dt_str, "%Y-%m-%d %H:%M:%S"))
        except:
            self.status_label.configure(text="日時形式が不正です", text_color="#FF4444")
            return

        sorted_files = self.get_sorted_files()
        is_inc = self.time_inc_var.get()
        history = []
        try:
            for i, path in enumerate(sorted_files, 0):
                ts = base_ts + (i if is_inc else 0)
                # 現在のタイムスタンプを保存
                st = os.stat(path)
                history.append((path, st.st_atime, st.st_mtime))
                os.utime(path, (ts, ts))
            
            self.undo_history.append({"type": "time", "data": history})
            self.undo_btn.configure(state="normal")
            self.update_preview()
            self.status_label.configure(text=f"成功: {len(history)} 個の日時を更新しました", text_color="#00FFCC")
        except Exception as e:
            self.status_label.configure(text=f"エラー: {str(e)}", text_color="#FF4444")

    def execute_undo(self):
        if not self.undo_history:
            return
        
        last_action = self.undo_history.pop()
        try:
            if last_action["type"] == "rename":
                new_paths = []
                for old_p, new_p in last_action["data"]:
                    if os.path.exists(new_p):
                        os.rename(new_p, old_p)
                        new_paths.append(old_p)
                self.file_list = new_paths
            else: # time
                for path, old_atime, old_mtime in last_action["data"]:
                    if os.path.exists(path):
                        os.utime(path, (old_atime, old_mtime))
            
            if not self.undo_history:
                self.undo_btn.configure(state="disabled")
            
            self.update_preview()
            self.status_label.configure(text="直前の操作を取り消しました", text_color="yellow")
        except Exception as e:
            self.status_label.configure(text=f"Undoエラー: {str(e)}", text_color="#FF4444")

    def clear_list(self):
        self.file_list = []
        self.undo_history = []
        self.undo_btn.configure(state="disabled")
        self.update_preview()
        self.status_label.configure(text="リストをクリアしました")

if __name__ == "__main__":
    app = SimpleRenamer()
    app.mainloop()
