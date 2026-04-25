import re
import webbrowser
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import COPY, DND_FILES, TkinterDnD
except ImportError:  # pragma: no cover - source execution fallback only
    COPY = None
    DND_FILES = None
    TkinterDnD = None


CJK_RANGE = r"\u4e00-\u9fff"
APP_TITLE = "Remove Text Extra Spaces v3"
AUTHOR_NAME = "Arthur Tao"
AUTHOR_WEBSITE_URL = "https://taoyutsun.blogspot.com/"
AUTHOR_FACEBOOK_URL = "https://facebook.com/arthurtaoyutsun"
AUTHOR_REPO_URL = "https://github.com/taoyutsun/remove-text-extra-spaces"


@dataclass(frozen=True)
class CleanOptions:
    collapse_whitespace: bool = True
    remove_cjk_spaces: bool = True
    fix_fullwidth_punctuation: bool = True
    fix_ascii_punctuation: bool = True
    fix_ne_particle: bool = True
    preserve_paragraph_breaks: bool = False


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def clean_text_segment(text: str, options: CleanOptions) -> str:
    if options.collapse_whitespace:
        text = re.sub(r"\s+", " ", text)
    else:
        text = re.sub(r"[ \t\f\v]+", " ", text.replace("\n", " "))

    if options.remove_cjk_spaces:
        text = re.sub(fr"(?<=[{CJK_RANGE}]) (?=[{CJK_RANGE}])", "", text)

    if options.fix_fullwidth_punctuation:
        text = re.sub(r"\s+([。，？！])", r"\1", text)
        text = re.sub(r"([。，？！]) ", r"\1", text)

    if options.fix_ascii_punctuation:
        text = re.sub(r"(?<=[A-Za-z])([,!?])(?=[A-Za-z])", r"\1 ", text)
        text = re.sub(r"(?<=[A-Za-z])\.(?=[A-Za-z][a-z])", ". ", text)

    if options.fix_ne_particle:
        text = re.sub(fr"呢(?=[{CJK_RANGE}])", "呢，", text)

    return text.strip()


def clean_text_ultimate(text: str, options: CleanOptions | None = None) -> str:
    options = options or CleanOptions()
    text = normalize_newlines(text)

    if options.preserve_paragraph_breaks:
        paragraphs = re.split(r"\n\s*\n+", text)
        cleaned_paragraphs = [
            clean_text_segment(paragraph, options)
            for paragraph in paragraphs
            if paragraph.strip()
        ]
        return "\n\n".join(cleaned_paragraphs).strip()

    return clean_text_segment(text, options)


def read_text_with_fallbacks(file_path: Path) -> str:
    last_error = None

    for encoding in ("utf-8-sig", "utf-8", "cp950", "mbcs"):
        try:
            return file_path.read_text(encoding=encoding)
        except LookupError:
            continue
        except UnicodeDecodeError as exc:
            last_error = exc

    raise ValueError(f"無法讀取檔案編碼：{file_path}") from last_error


def build_output_path(file_path: Path) -> Path:
    return file_path.with_name(f"{file_path.stem}_cleaned{file_path.suffix}")


def process_file(file_path: str, options: CleanOptions | None = None) -> Path:
    input_path = Path(file_path)
    raw_text = read_text_with_fallbacks(input_path)
    cleaned_text = clean_text_ultimate(raw_text, options)

    output_path = build_output_path(input_path)
    output_path.write_text(cleaned_text, encoding="utf-8")
    return output_path


def build_options_from_vars(option_vars: dict[str, tk.BooleanVar]) -> CleanOptions:
    return CleanOptions(
        collapse_whitespace=option_vars["collapse_whitespace"].get(),
        remove_cjk_spaces=option_vars["remove_cjk_spaces"].get(),
        fix_fullwidth_punctuation=option_vars["fix_fullwidth_punctuation"].get(),
        fix_ascii_punctuation=option_vars["fix_ascii_punctuation"].get(),
        fix_ne_particle=option_vars["fix_ne_particle"].get(),
        preserve_paragraph_breaks=option_vars["preserve_paragraph_breaks"].get(),
    )


def iter_widget_tree(widget: tk.Misc):
    yield widget
    for child in widget.winfo_children():
        yield from iter_widget_tree(child)


def parse_drop_file_list(root: tk.Misc, raw_data: str) -> list[str]:
    raw_data = (raw_data or "").strip()
    if not raw_data:
        return []

    try:
        paths = root.tk.splitlist(raw_data)
    except tk.TclError:
        parts = re.findall(r"\{[^}]+\}|[^\s]+", raw_data)
        paths = [
            part[1:-1] if part.startswith("{") and part.endswith("}") else part
            for part in parts
        ]

    return [path for path in paths if path]


class RemoveTextExtraSpacesV3App:
    def __init__(self, root: tk.Misc) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1120x760")
        self.root.minsize(920, 640)

        self.selected_files: list[Path] = []
        self.option_vars = self._create_option_vars()
        self.status_var = tk.StringVar(
            value=(
                "可拖曳 .txt 檔到視窗加入清單，或切換到「直接貼文字」模式處理短內容。"
            )
        )
        self.drag_drop_enabled = False

        self._build_ui()
        if self._configure_drag_and_drop() == 0:
            self.status_var.set(
                "拖曳加入暫時不可用，請改用「新增檔案」。若從原始碼執行，請先安裝 tkinterdnd2。"
            )
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _create_option_vars(self) -> dict[str, tk.BooleanVar]:
        return {
            "collapse_whitespace": tk.BooleanVar(value=True),
            "remove_cjk_spaces": tk.BooleanVar(value=True),
            "fix_fullwidth_punctuation": tk.BooleanVar(value=True),
            "fix_ascii_punctuation": tk.BooleanVar(value=True),
            "fix_ne_particle": tk.BooleanVar(value=True),
            "preserve_paragraph_breaks": tk.BooleanVar(value=False),
        }

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, padding=(18, 18, 18, 10))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text=APP_TITLE,
            font=("Microsoft JhengHei UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="雙模式版本：支援 TXT 檔案批次清理，也支援直接貼入純文字即時整理。",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        body = ttk.Frame(self.root, padding=(18, 0, 18, 0))
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=5)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(body)
        notebook.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.file_tab = ttk.Frame(notebook, padding=12)
        text_tab = ttk.Frame(notebook, padding=12)
        notebook.add(self.file_tab, text="檔案模式")
        notebook.add(text_tab, text="直接貼文字")

        self._build_file_tab(self.file_tab)
        self._build_text_tab(text_tab)
        self._build_options_panel(body)

        footer = ttk.Frame(self.root, padding=(18, 10, 18, 18))
        footer.grid(row=2, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)

        ttk.Label(footer, textvariable=self.status_var).grid(
            row=0,
            column=0,
            sticky="w",
        )

    def _configure_drag_and_drop(self) -> int:
        if TkinterDnD is None or DND_FILES is None or not hasattr(
            self.root,
            "drop_target_register",
        ):
            return 0

        registered = 0
        for widget in iter_widget_tree(self.root):
            try:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<DropEnter>>", self._accept_drop)
                widget.dnd_bind("<<DropPosition>>", self._accept_drop)
                widget.dnd_bind("<<Drop>>", self._handle_file_drop)
                registered += 1
            except (AttributeError, tk.TclError):
                continue

        self.drag_drop_enabled = registered > 0
        return registered

    def _accept_drop(self, _event=None):
        return COPY

    def _handle_file_drop(self, event) -> str:
        file_paths = parse_drop_file_list(self.root, getattr(event, "data", ""))
        self.add_files(file_paths)
        return COPY or ""

    def _build_file_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(toolbar, text="新增檔案", command=self.choose_files).grid(
            row=0,
            column=0,
            padx=(0, 8),
        )
        ttk.Button(toolbar, text="移除選取", command=self.remove_selected).grid(
            row=0,
            column=1,
            padx=(0, 8),
        )
        ttk.Button(toolbar, text="清空列表", command=self.clear_files).grid(
            row=0,
            column=2,
            padx=(0, 8),
        )
        ttk.Button(toolbar, text="開始處理檔案", command=self.process_selected_files).grid(
            row=0,
            column=3,
        )

        file_frame = ttk.LabelFrame(
            parent,
            text="待處理的 TXT 檔案",
            padding=(10, 10, 10, 10),
        )
        file_frame.grid(row=1, column=0, sticky="nsew")
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(
            file_frame,
            selectmode=tk.EXTENDED,
            font=("Consolas", 10),
            activestyle="none",
        )
        self.file_listbox.grid(row=0, column=0, sticky="nsew")

        file_scrollbar = ttk.Scrollbar(
            file_frame,
            orient="vertical",
            command=self.file_listbox.yview,
        )
        file_scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)

    def _build_text_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        input_frame = ttk.LabelFrame(parent, text="原始文字", padding=10)
        input_frame.grid(row=0, column=0, sticky="nsew")
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        self.input_text = tk.Text(
            input_frame,
            wrap="word",
            font=("Microsoft JhengHei UI", 11),
            undo=True,
        )
        self.input_text.grid(row=0, column=0, sticky="nsew")

        input_scrollbar = ttk.Scrollbar(
            input_frame,
            orient="vertical",
            command=self.input_text.yview,
        )
        input_scrollbar.grid(row=0, column=1, sticky="ns")
        self.input_text.configure(yscrollcommand=input_scrollbar.set)

        actions = ttk.Frame(parent)
        actions.grid(row=1, column=0, sticky="ew", pady=10)

        ttk.Button(actions, text="清理文字", command=self.clean_pasted_text).grid(
            row=0,
            column=0,
            padx=(0, 8),
        )
        ttk.Button(actions, text="複製結果", command=self.copy_output_text).grid(
            row=0,
            column=1,
            padx=(0, 8),
        )
        ttk.Button(actions, text="儲存結果", command=self.save_output_text).grid(
            row=0,
            column=2,
            padx=(0, 8),
        )
        ttk.Button(actions, text="清空文字", command=self.clear_text_areas).grid(
            row=0,
            column=3,
        )

        output_frame = ttk.LabelFrame(parent, text="清理後文字", padding=10)
        output_frame.grid(row=2, column=0, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = tk.Text(
            output_frame,
            wrap="word",
            font=("Microsoft JhengHei UI", 11),
            state="disabled",
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")

        output_scrollbar = ttk.Scrollbar(
            output_frame,
            orient="vertical",
            command=self.output_text.yview,
        )
        output_scrollbar.grid(row=0, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=output_scrollbar.set)

    def _build_options_panel(self, parent: ttk.Frame) -> None:
        options_frame = ttk.LabelFrame(parent, text="清理選項", padding=12)
        options_frame.grid(row=0, column=1, sticky="nsew")
        options_frame.columnconfigure(0, weight=1)

        option_specs = [
            ("collapse_whitespace", "將連續空白壓成單一空格"),
            ("remove_cjk_spaces", "移除中文字與中文字之間的空格"),
            ("fix_fullwidth_punctuation", "修正全形標點前後的多餘空格"),
            ("fix_ascii_punctuation", "修正英文半形標點後缺少空格"),
            ("fix_ne_particle", "修正常見「呢他」為「呢，他」"),
            ("preserve_paragraph_breaks", "保留段落換行（以空白行區隔段落）"),
        ]

        for row_index, (key, label) in enumerate(option_specs):
            ttk.Checkbutton(
                options_frame,
                text=label,
                variable=self.option_vars[key],
            ).grid(row=row_index, column=0, sticky="w", pady=4)

        ttk.Label(
            options_frame,
            text=(
                "使用建議：\n"
                "檔案模式適合大量 TXT 批次處理。\n"
                "直接貼文字適合處理短段落、會議片段或臨時複製內容。"
            ),
            wraplength=260,
            justify="left",
        ).grid(row=len(option_specs), column=0, sticky="w", pady=(14, 0))

        ttk.Separator(options_frame, orient="horizontal").grid(
            row=len(option_specs) + 1,
            column=0,
            sticky="ew",
            pady=(16, 12),
        )

        author_frame = ttk.LabelFrame(options_frame, text="作者與版權", padding=10)
        author_frame.grid(
            row=len(option_specs) + 2,
            column=0,
            sticky="ew",
        )
        author_frame.columnconfigure(0, weight=1)

        ttk.Label(
            author_frame,
            text=(
                f"{APP_TITLE} 由 {AUTHOR_NAME} 設計與維護。"
                "歡迎使用與分享，並保留原作者與來源資訊。"
            ),
            wraplength=240,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            author_frame,
            text=f"作者：{AUTHOR_NAME}",
            font=("Microsoft JhengHei UI", 10, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        links_frame = ttk.Frame(author_frame)
        links_frame.grid(row=2, column=0, sticky="w", pady=(8, 0))

        self._create_link_label(links_frame, "亞瑟 ASK 部落格", AUTHOR_WEBSITE_URL).grid(
            row=0,
            column=0,
            sticky="w",
        )
        ttk.Label(links_frame, text=" | ").grid(row=0, column=1, sticky="w")
        self._create_link_label(links_frame, "Facebook", AUTHOR_FACEBOOK_URL).grid(
            row=0,
            column=2,
            sticky="w",
        )
        ttk.Label(links_frame, text=" | ").grid(row=0, column=3, sticky="w")
        self._create_link_label(links_frame, "檢視原始碼", AUTHOR_REPO_URL).grid(
            row=0,
            column=4,
            sticky="w",
        )

    def _create_link_label(
        self,
        parent: tk.Misc,
        text: str,
        url: str,
    ) -> tk.Label:
        label = tk.Label(
            parent,
            text=text,
            fg="#0a66c2",
            cursor="hand2",
            font=("Microsoft JhengHei UI", 9, "underline"),
            bg=self.root.cget("bg"),
        )
        label.bind("<Button-1>", lambda _event, target=url: self._open_external_url(target))
        return label

    def _open_external_url(self, url: str) -> None:
        try:
            webbrowser.open(url, new=2)
        except Exception:
            self.status_var.set(f"無法開啟連結：{url}")

    def choose_files(self) -> None:
        file_paths = filedialog.askopenfilenames(
            title="選擇文字檔案",
            filetypes=[("文字檔案", "*.txt")],
        )
        self.add_files(file_paths)

    def add_files(self, file_paths) -> None:
        new_files: list[Path] = []
        skipped_files = 0
        existing = {path.resolve() for path in self.selected_files}

        for raw_path in file_paths:
            path = Path(raw_path)

            if not path.exists() or path.suffix.lower() != ".txt":
                skipped_files += 1
                continue

            resolved = path.resolve()
            if resolved in existing:
                continue

            existing.add(resolved)
            new_files.append(resolved)

        if new_files:
            self.selected_files.extend(new_files)
            self.selected_files.sort()
            self.refresh_file_list()
            message = f"已加入 {len(new_files)} 個檔案。"
            if skipped_files:
                message += f" 另有 {skipped_files} 個非 TXT 或無效路徑已略過。"
            self.status_var.set(message)
            return

        if skipped_files:
            self.status_var.set("沒有加入新檔案，拖放內容不是有效的 TXT 檔案。")
        else:
            self.status_var.set("沒有新的 TXT 檔案可加入。")

    def refresh_file_list(self) -> None:
        self.file_listbox.delete(0, tk.END)
        for path in self.selected_files:
            self.file_listbox.insert(tk.END, str(path))

    def remove_selected(self) -> None:
        selected_indices = list(self.file_listbox.curselection())
        if not selected_indices:
            self.status_var.set("尚未選取要移除的檔案。")
            return

        for index in reversed(selected_indices):
            del self.selected_files[index]

        self.refresh_file_list()
        self.status_var.set(f"已移除 {len(selected_indices)} 個檔案。")

    def clear_files(self) -> None:
        if not self.selected_files:
            self.status_var.set("目前沒有待處理檔案。")
            return

        cleared_count = len(self.selected_files)
        self.selected_files.clear()
        self.refresh_file_list()
        self.status_var.set(f"已清空列表，共移除 {cleared_count} 個檔案。")

    def process_selected_files(self) -> None:
        if not self.selected_files:
            messagebox.showwarning("尚未選擇檔案", "請先加入至少一個 TXT 檔案。")
            return

        options = build_options_from_vars(self.option_vars)
        successes: list[Path] = []
        failures: list[str] = []

        for file_path in self.selected_files:
            try:
                output_path = process_file(str(file_path), options)
                successes.append(output_path)
            except Exception as exc:
                failures.append(f"{file_path.name}: {exc}")

        self.status_var.set(
            f"檔案處理完成：成功 {len(successes)} 個，失敗 {len(failures)} 個。"
        )

        if failures:
            failure_text = "\n".join(failures[:8])
            if len(failures) > 8:
                failure_text += "\n..."
            messagebox.showwarning(
                "部分檔案處理失敗",
                (
                    f"成功 {len(successes)} 個，失敗 {len(failures)} 個。\n\n"
                    f"失敗項目：\n{failure_text}"
                ),
            )
            return

        preview = "\n".join(str(path) for path in successes[:6])
        if len(successes) > 6:
            preview += "\n..."
        messagebox.showinfo(
            "檔案處理完成",
            f"已成功處理 {len(successes)} 個檔案。\n\n輸出檔案：\n{preview}",
        )

    def clean_pasted_text(self) -> None:
        raw_text = self.input_text.get("1.0", "end-1c")
        if not raw_text.strip():
            messagebox.showwarning("沒有可處理的文字", "請先貼上或輸入要清理的內容。")
            return

        options = build_options_from_vars(self.option_vars)
        cleaned = clean_text_ultimate(raw_text, options)

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", cleaned)
        self.output_text.configure(state="disabled")
        self.status_var.set("已完成貼上文字的清理。")

    def copy_output_text(self) -> None:
        cleaned_text = self.output_text.get("1.0", "end-1c")
        if not cleaned_text:
            self.status_var.set("目前沒有可複製的結果。")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(cleaned_text)
        self.status_var.set("清理後文字已複製到剪貼簿。")

    def save_output_text(self) -> None:
        cleaned_text = self.output_text.get("1.0", "end-1c")
        if not cleaned_text:
            messagebox.showwarning("沒有可儲存的結果", "請先完成文字清理。")
            return

        output_path = filedialog.asksaveasfilename(
            title="儲存清理後的文字",
            defaultextension=".txt",
            filetypes=[("文字檔案", "*.txt")],
        )
        if not output_path:
            return

        Path(output_path).write_text(cleaned_text, encoding="utf-8")
        self.status_var.set(f"已儲存清理後文字：{output_path}")

    def clear_text_areas(self) -> None:
        self.input_text.delete("1.0", tk.END)
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state="disabled")
        self.status_var.set("已清空輸入與輸出文字區。")

    def close(self) -> None:
        self.root.destroy()


def main() -> None:
    root = TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    RemoveTextExtraSpacesV3App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
