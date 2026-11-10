# Rhythm ♪

你的个人节奏助手——平衡工作和学习，每天三条简报。

零第三方依赖（纯 Python 标准库），一条命令记一笔，到点自动弹通知：晨间看今天压着什么事、午间看还剩几件、傍晚复盘工作/学习/生活占比和连续学习天数。

---

## 为什么做

我经常「工作忙起来就忘了学习，学起来又忘了工作」。Rhythm 就是那根绳子：不用打开任何 App，随手记一条，剩下的——分类、提醒、复盘——它替我记。

核心是一句话：**把每天零散的输入，压成早中晚三段「我该看什么」**。

---

## 安装

```bash
# 零依赖，直接跑（推荐）
git clone <你的仓库地址> && cd rhythm

# 或安装为命令
pip install -e .
```

Python ≥ 3.8。

---

## 怎么用

```bash
python -m rhythm add "周五交报告"       # 记一条（自动分类 + 解析日期）
python -m rhythm add "学 20 分钟 Python"  # 学习类
python -m rhythm today                   # 看今天的便条
python -m rhythm morning                 # 晨间简报
python -m rhythm noon                    # 午间检查
python -m rhythm evening                 # 傍晚复盘
python -m rhythm daemon                  # 后台运行，到点自动弹通知
python -m rhythm config                  # 查看/修改设置
```

`daemon` 模式会常驻前台，每隔 30 秒检查一次，到配置的时间（默认 09:00 / 12:30 / 18:00）弹出系统通知。改时间：

```bash
python -m rhythm config morning_time 08:30
python -m rhythm config show_streak false
```

macOS 上想用菜单栏应用，装 `rumps` 后跑 `python -m rhythm start`。

---

## 它能做什么

- **自动分类**：`work` / `study` / `life`，基于关键词规则。
- **中文日期解析**：`今天` `明天` `后天` `3天后` `周五` `星期三` `11月8日` 都会被识别为截止日，跨年自动顺延。
- **连续学习天数（streak）**：每天只要有学习记录就 +1，今天还没记不算断。
- **跨平台通知**：macOS（osascript）/ Linux（notify-send）/ Windows（PowerShell），零依赖。
- **本地 Markdown 存储**：数据就在 `data/notes/YYYY-MM-DD.md`，随时用别的工具打开，不锁定。

---

## 架构

```
rhythm add <text>
   └─ classifier.analyze → (category, cleaned_text, due)
        └─ storage.add_note → data/notes/<date>.md

rhythm daemon
   └─ 每 30 秒检查 schedule
        └─ brief.*_notification → notifier.notify
```

- `classifier.py`：规则分类 + 中文日期解析（预留了 LLM 的接口位）
- `storage.py`：本地 Markdown 存储
- `brief.py`：晨/午/晚三条简报 + 一条式通知文案
- `notifier.py`：跨平台通知
- `daemon.py`：后台定时

---

## 我做的取舍

- **零依赖**。这个工具的核心价值是「随时能记」，引入 pandas/requests 之类是负资产。
- **本地 Markdown 而非数据库**。数据要能被 grep、被任何编辑器打开，可迁移 > 查询能力。
- **不做云同步**。单人自用，同步是复杂度陷阱。

---

## 已知限制

- Windows 通知依赖 PowerShell 的 NotifyIcon，某些精简版 Windows 可能没有；此时会静默失败（best-effort）。
- `daemon` 是前台进程，不是真正的系统守护进程；跨平台常驻需要各自的服务管理方案。
- 关键词分类是启发式，会误判；`classifier.py` 里留了换成 LLM 的接口位。

---

## 测试

```bash
pip install pytest
pytest
```

覆盖中文日期解析（`parse_date`）和连续学习天数（`study_streak`）两块核心逻辑。

---

## License

[MIT](./LICENSE)
