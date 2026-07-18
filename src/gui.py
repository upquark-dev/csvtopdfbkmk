import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading

from src.converter import validate_csv, csv_to_bookmark_xml, ValidationError


class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("CSV 转福昕书签 XML")
        self.window.geometry("640x480")
        self.window.minsize(560, 400)

        self.csv_path = tk.StringVar()
        self.rows_var = tk.IntVar(value=1)
        self.max_level = 0
        self.last_valid_path = None
        self.rows_buttons = []
        self.rows_grid = None

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.window, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(main, text="CSV 转福昕书签 XML", font=("", 16, "bold"))
        title.pack(anchor=tk.W, pady=(0, 16))

        file_frame = ttk.LabelFrame(main, text="选择 CSV 文件", padding=8)
        file_frame.pack(fill=tk.X, pady=(0, 12))

        row1 = ttk.Frame(file_frame)
        row1.pack(fill=tk.X)
        self.entry = ttk.Entry(row1, textvariable=self.csv_path, state="readonly")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row1, text="浏览...", command=self._browse).pack(
            side=tk.RIGHT, padx=(8, 0)
        )

        self.rows_frame = ttk.LabelFrame(main, text="生成深度级别", padding=8)
        self.rows_frame.pack(fill=tk.X, pady=(0, 12))
        self._rebuild_rows_buttons(0)

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(btn_frame, text="生成导出 XML", command=self._export).pack(
            side=tk.LEFT
        )

        status_frame = ttk.LabelFrame(main, text="状态信息", padding=8)
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.status_text = tk.Text(
            status_frame,
            wrap=tk.WORD,
            height=8,
            state="disabled",
            font=("Consolas", 10),
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self._append_status("就绪，请选择 CSV 文件")

    def _rebuild_rows_buttons(self, max_level):
        for btn in self.rows_buttons:
            btn.destroy()
        self.rows_buttons.clear()

        if self.rows_grid:
            self.rows_grid.destroy()
            self.rows_grid = None

        self.max_level = max_level
        if max_level < 1:
            return

        self.rows_var.set(max_level)
        self.rows_grid = ttk.Frame(self.rows_frame)
        self.rows_grid.pack(fill=tk.X)

        for i in range(1, max_level + 1):
            btn = ttk.Radiobutton(
                self.rows_grid,
                text=f"{i}级",
                variable=self.rows_var,
                value=i,
            )
            btn.pack(side=tk.LEFT, padx=(0, 12), pady=2)
            self.rows_buttons.append(btn)

    def _browse(self):
        path = filedialog.askopenfilename(
            title="选择 CSV 文件",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
        )
        if not path:
            return
        self.csv_path.set(path)
        self.last_valid_path = None
        self._rebuild_rows_buttons(0)
        self._append_status(f"已选择文件: {path}")
        self._validate()

    def _validate(self):
        path = self.csv_path.get()
        if not path:
            return
        try:
            rows = validate_csv(path)
            max_level = max(int(r["级别"]) for r in rows)
            self.last_valid_path = path
            self._rebuild_rows_buttons(max_level)
            self._append_status(
                f"✓ 验证通过：共 {len(rows)} 条书签，最大层级 {max_level}"
            )
        except ValidationError as e:
            self.last_valid_path = None
            self._rebuild_rows_buttons(0)
            self._append_status(f"✗ {e}")
            messagebox.showerror("数据不符合要求", str(e))

    def _export(self):
        path = self.csv_path.get()
        if not path:
            messagebox.showwarning("提示", "请先选择 CSV 文件")
            return
        if self.last_valid_path != path:
            messagebox.showwarning("提示", "请先导入有效的 CSV 文件")
            return
        if self.max_level < 1:
            messagebox.showwarning("提示", "文件验证未通过，请检查 CSV 格式")
            return

        rows_val = self.rows_var.get()
        base, _ = os.path.splitext(os.path.basename(path))
        default_name = f"{base}_{rows_val}级.xml"

        save_path = filedialog.asksaveasfilename(
            title="导出 XML 文件",
            defaultextension=".xml",
            initialfile=default_name,
            filetypes=[("XML 文件", "*.xml"), ("所有文件", "*.*")],
        )
        if not save_path:
            return

        def do_export():
            self._set_buttons_state(tk.DISABLED)
            try:
                csv_to_bookmark_xml(path, save_path, rows=rows_val)
                size = os.path.getsize(save_path)
                self._append_status(f"✓ 导出成功：{save_path} （{size} 字节）")

                def ask_open():
                    if messagebox.askyesno(
                        "导出完成",
                        f"XML 已保存至：\n{save_path}\n\n是否打开所在文件夹？",
                    ):
                        os.startfile(os.path.dirname(save_path))

                self.window.after(0, ask_open)
            except Exception as e:
                self._append_status(f"✗ 导出失败：{e}")
                messagebox.showerror("导出失败", str(e))
            finally:
                self._set_buttons_state(tk.NORMAL)

        threading.Thread(target=do_export, daemon=True).start()

    def _set_buttons_state(self, state):
        for widget in (self.entry,):
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass
        for child in self.window.winfo_children():
            self._set_btn_state_recursive(child, state)

    def _set_btn_state_recursive(self, widget, state):
        if isinstance(widget, (ttk.Button, ttk.Radiobutton)):
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass
        for child in widget.winfo_children():
            self._set_btn_state_recursive(child, state)

    def _append_status(self, msg):
        self.status_text.configure(state="normal")
        self.status_text.insert(tk.END, msg + "\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state="disabled")

    def run(self):
        self.window.mainloop()
