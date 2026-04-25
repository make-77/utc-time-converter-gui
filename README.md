# UTC Time Converter

一个桌面 GUI 工具，用于在 `UTC`、任意 IANA 时区与 Unix 时间戳之间双向转换时间。

## 功能

- 支持输入格式：`YYYY-MM-DD HH:MM:SS`
- 支持 Unix 秒级时间戳与毫秒级时间戳
- 源时区与目标时区自由切换
- 一键填充当前时间
- 一键填充当前时间戳
- `UTC -> 本地` / `本地 -> UTC`
- `时间 -> 时间戳` / `时间戳 -> 时间`
- 复制转换结果
- 提供源码、Windows `exe` 构建脚本、Linux `deb` 构建脚本

## 运行源码

```powershell
python app.py
```

## 工程结构

```text
app.py
scripts/
release/
vendor_wheels/
```

- `app.py`：GUI 主程序
- `scripts/`：构建脚本
- `release/windows/`：Windows 交付件
- `release/linux/`：Linux 交付件
- `vendor_wheels/`：本地 PyInstaller 依赖

## 构建 Windows EXE

```powershell
python scripts/build_exe.py
```

产物默认输出到 `release/windows/utc-time-converter.exe`。

## 构建 Debian DEB

```powershell
python scripts/build_deb.py
```

产物默认输出到 `release/linux/utc-time-converter_1.1.0_all.deb`。

说明：当前 `deb` 采用 Python 源码分发方式，安装后通过系统 `python3` 启动，依赖 `python3`、`python3-tk`、`tzdata`。
