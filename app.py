from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from zoneinfo import ZoneInfo, available_timezones


APP_NAME = "UTC Time Converter"
APP_VERSION = "1.1.0"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MODE_DATETIME = "日期时间"
MODE_TIMESTAMP_SECONDS = "Unix 时间戳（秒）"
MODE_TIMESTAMP_MILLISECONDS = "Unix 时间戳（毫秒）"
INPUT_MODES = [MODE_DATETIME, MODE_TIMESTAMP_SECONDS, MODE_TIMESTAMP_MILLISECONDS]

COMMON_TIMEZONES = [
    "UTC",
    "Asia/Shanghai",
    "Asia/Tokyo",
    "Asia/Singapore",
    "Asia/Kolkata",
    "Europe/London",
    "Europe/Berlin",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "Australia/Sydney",
]


def get_timezone_list() -> list[str]:
    all_timezones = sorted(available_timezones())
    ordered = []
    for name in COMMON_TIMEZONES + all_timezones:
        if name not in ordered:
            ordered.append(name)
    return ordered


@dataclass
class ConversionResult:
    source_text: str
    target_text: str
    source_zone: str
    target_zone: str
    source_timestamp_seconds: str
    source_timestamp_milliseconds: str
    target_timestamp_seconds: str
    target_timestamp_milliseconds: str


def format_timestamp(dt: datetime, milliseconds: bool = False) -> str:
    timestamp = dt.astimezone(UTC).timestamp()
    if milliseconds:
        return str(int(round(timestamp * 1000)))
    return str(int(round(timestamp)))


def parse_input_datetime(input_text: str, source_zone: str, input_mode: str) -> datetime:
    if input_mode == MODE_DATETIME:
        try:
            naive = datetime.strptime(input_text, DATETIME_FORMAT)
        except ValueError as exc:
            raise ValueError("时间格式无效，请使用 YYYY-MM-DD HH:MM:SS。") from exc
        return naive.replace(tzinfo=ZoneInfo(source_zone))

    if input_mode == MODE_TIMESTAMP_SECONDS:
        try:
            seconds = int(input_text)
        except ValueError as exc:
            raise ValueError("秒级时间戳必须是整数。") from exc
        return datetime.fromtimestamp(seconds, tz=UTC)

    if input_mode == MODE_TIMESTAMP_MILLISECONDS:
        try:
            milliseconds = int(input_text)
        except ValueError as exc:
            raise ValueError("毫秒级时间戳必须是整数。") from exc
        return datetime.fromtimestamp(milliseconds / 1000, tz=UTC)

    raise ValueError(f"不支持的输入模式：{input_mode}")


def format_output_datetime(target_dt: datetime, output_mode: str) -> str:
    if output_mode == MODE_DATETIME:
        return f"{target_dt.strftime(DATETIME_FORMAT)} ({target_dt.tzname()})"
    if output_mode == MODE_TIMESTAMP_SECONDS:
        return format_timestamp(target_dt, milliseconds=False)
    if output_mode == MODE_TIMESTAMP_MILLISECONDS:
        return format_timestamp(target_dt, milliseconds=True)
    raise ValueError(f"不支持的输出模式：{output_mode}")


def convert_time(
    input_text: str,
    source_zone: str,
    target_zone: str,
    input_mode: str = MODE_DATETIME,
    output_mode: str = MODE_DATETIME,
    valid_timezones: list[str] | None = None,
) -> ConversionResult:
    timezones = valid_timezones or get_timezone_list()
    if not input_text:
        raise ValueError("请输入待转换的时间。")
    if source_zone not in timezones:
        raise ValueError(f"不支持的源时区：{source_zone}")
    if target_zone not in timezones:
        raise ValueError(f"不支持的目标时区：{target_zone}")
    if input_mode not in INPUT_MODES:
        raise ValueError(f"不支持的输入模式：{input_mode}")
    if output_mode not in INPUT_MODES:
        raise ValueError(f"不支持的输出模式：{output_mode}")

    source_dt = parse_input_datetime(input_text, source_zone, input_mode)
    target_dt = source_dt.astimezone(ZoneInfo(target_zone))
    source_local_dt = source_dt.astimezone(ZoneInfo(source_zone))

    return ConversionResult(
        source_text=f"{source_local_dt.strftime(DATETIME_FORMAT)} ({source_local_dt.tzname()})",
        target_text=format_output_datetime(target_dt, output_mode),
        source_zone=source_zone if input_mode == MODE_DATETIME else "UTC",
        target_zone=target_zone,
        source_timestamp_seconds=format_timestamp(source_dt, milliseconds=False),
        source_timestamp_milliseconds=format_timestamp(source_dt, milliseconds=True),
        target_timestamp_seconds=format_timestamp(target_dt, milliseconds=False),
        target_timestamp_milliseconds=format_timestamp(target_dt, milliseconds=True),
    )


class ConverterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.minsize(860, 460)
        self.timezones = get_timezone_list()

        self.source_tz_var = tk.StringVar(value="UTC")
        self.target_tz_var = tk.StringVar(value="Asia/Shanghai")
        self.input_mode_var = tk.StringVar(value=MODE_DATETIME)
        self.output_mode_var = tk.StringVar(value=MODE_DATETIME)
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.status_var = tk.StringVar(value="输入时间后点击“转换”。格式：YYYY-MM-DD HH:MM:SS")

        self._build_ui()
        self.fill_now()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        container = ttk.Frame(self.root, padding=18)
        container.grid(sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(4, weight=1)

        title = ttk.Label(
            container,
            text="UTC 时间互转工具",
            font=("Microsoft YaHei UI", 18, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ttk.Label(
            container,
            text="日期时间、秒级时间戳、毫秒级时间戳互转。",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, 14))

        form = ttk.Frame(container)
        form.grid(row=2, column=0, sticky="ew")
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        ttk.Label(form, text="输入模式").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=6)
        input_mode_box = ttk.Combobox(
            form,
            textvariable=self.input_mode_var,
            values=INPUT_MODES,
            state="readonly",
            height=6,
        )
        input_mode_box.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(form, text="输出模式").grid(row=0, column=2, sticky="w", padx=(12, 8), pady=6)
        output_mode_box = ttk.Combobox(
            form,
            textvariable=self.output_mode_var,
            values=INPUT_MODES,
            state="readonly",
            height=6,
        )
        output_mode_box.grid(row=0, column=3, sticky="ew", pady=6)

        ttk.Label(form, text="源时区").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=6)
        source_box = ttk.Combobox(
            form,
            textvariable=self.source_tz_var,
            values=self.timezones,
            state="readonly",
            height=18,
        )
        source_box.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(form, text="目标时区").grid(row=1, column=2, sticky="w", padx=(12, 8), pady=6)
        target_box = ttk.Combobox(
            form,
            textvariable=self.target_tz_var,
            values=self.timezones,
            state="readonly",
            height=18,
        )
        target_box.grid(row=1, column=3, sticky="ew", pady=6)

        ttk.Label(form, text="输入值").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=6)
        input_entry = ttk.Entry(form, textvariable=self.input_var)
        input_entry.grid(row=2, column=1, columnspan=3, sticky="ew", pady=6)
        input_entry.focus_set()

        ttk.Label(form, text="输出值").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=6)
        output_entry = ttk.Entry(form, textvariable=self.output_var, state="readonly")
        output_entry.grid(row=3, column=1, columnspan=3, sticky="ew", pady=6)

        button_row = ttk.Frame(container)
        button_row.grid(row=3, column=0, sticky="ew", pady=(14, 10))

        for column in range(4):
            button_row.columnconfigure(column, weight=1)

        ttk.Button(button_row, text="现在", command=self.fill_now).grid(row=0, column=0, sticky="ew", padx=4)
        ttk.Button(button_row, text="交换", command=self.swap_timezones).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(button_row, text="转换", command=self.convert).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(button_row, text="复制", command=self.copy_result).grid(row=0, column=3, sticky="ew", padx=4)

        result_frame = ttk.LabelFrame(container, text="摘要", padding=12)
        result_frame.grid(row=4, column=0, sticky="nsew", pady=(6, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.result_text = tk.Text(
            result_frame,
            wrap="word",
            height=10,
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        self.result_text.grid(row=0, column=0, sticky="nsew")
        self.result_text.configure(state="disabled")

        status = ttk.Label(container, textvariable=self.status_var, foreground="#1f4f82")
        status.grid(row=5, column=0, sticky="sw")

        self.root.bind("<Return>", lambda _event: self.convert())

    def fill_now(self) -> None:
        zone_name = self.source_tz_var.get() or "UTC"
        if self.input_mode_var.get() == MODE_DATETIME:
            now_text = datetime.now(ZoneInfo(zone_name)).strftime(DATETIME_FORMAT)
        else:
            now_text = self._now_timestamp_text(self.input_mode_var.get())
        self.input_var.set(now_text)
        self.status_var.set("已填充当前输入值。")
        self.convert()

    def _now_timestamp_text(self, input_mode: str) -> str:
        now_utc = datetime.now(UTC)
        if input_mode == MODE_TIMESTAMP_MILLISECONDS:
            return format_timestamp(now_utc, milliseconds=True)
        return format_timestamp(now_utc, milliseconds=False)

    def swap_timezones(self) -> None:
        source, target = self.source_tz_var.get(), self.target_tz_var.get()
        self.source_tz_var.set(target)
        self.target_tz_var.set(source)
        self.status_var.set("已交换源时区与目标时区。")
        self.convert()

    def set_utc_to_local(self) -> None:
        self.source_tz_var.set("UTC")
        self.target_tz_var.set(self.detect_local_timezone())
        self.input_mode_var.set(MODE_DATETIME)
        self.output_mode_var.set(MODE_DATETIME)
        self.fill_now()

    def set_local_to_utc(self) -> None:
        self.source_tz_var.set(self.detect_local_timezone())
        self.target_tz_var.set("UTC")
        self.input_mode_var.set(MODE_DATETIME)
        self.output_mode_var.set(MODE_DATETIME)
        self.fill_now()

    def detect_local_timezone(self) -> str:
        local_zone = datetime.now().astimezone().tzinfo
        if hasattr(local_zone, "key"):
            return getattr(local_zone, "key")
        return "Asia/Shanghai"

    def convert(self) -> None:
        try:
            result = self._do_conversion(
                self.input_var.get().strip(),
                self.source_tz_var.get(),
                self.target_tz_var.get(),
                self.input_mode_var.get(),
                self.output_mode_var.get(),
            )
        except ValueError as exc:
            self.output_var.set("")
            self._set_result_text("")
            self.status_var.set(str(exc))
            return

        self.output_var.set(result.target_text)
        details = self._build_summary(result)
        self._set_result_text(details)
        self.status_var.set("转换完成。")

    def _do_conversion(
        self,
        input_text: str,
        source_zone: str,
        target_zone: str,
        input_mode: str,
        output_mode: str,
    ) -> ConversionResult:
        return convert_time(
            input_text=input_text,
            source_zone=source_zone,
            target_zone=target_zone,
            input_mode=input_mode,
            output_mode=output_mode,
            valid_timezones=self.timezones,
        )

    def copy_result(self) -> None:
        result = self.output_var.get()
        if not result:
            messagebox.showinfo(APP_NAME, "当前没有可复制的结果。")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        self.status_var.set("结果已复制到剪贴板。")

    def _build_summary(self, result: ConversionResult) -> str:
        target_time_text = result.target_text
        if self.output_mode_var.get() != MODE_DATETIME:
            target_time_text = (
                f"{result.target_zone}: "
                f"{datetime.fromtimestamp(int(result.target_timestamp_seconds), tz=UTC).astimezone(ZoneInfo(result.target_zone)).strftime(DATETIME_FORMAT)}"
            )

        return (
            f"{self.input_mode_var.get()} | {result.source_zone}\n"
            f"{result.source_text}\n\n"
            f"{self.output_mode_var.get()} | {result.target_zone}\n"
            f"{result.target_text}\n\n"
            f"{target_time_text}\n"
            f"秒级时间戳: {result.target_timestamp_seconds}\n"
            f"毫秒时间戳: {result.target_timestamp_milliseconds}\n"
        )

    def _set_result_text(self, text: str) -> None:
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def main() -> None:
    root = tk.Tk()
    try:
        root.iconname(APP_NAME)
    except tk.TclError:
        pass
    ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
