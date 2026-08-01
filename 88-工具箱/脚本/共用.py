# -*- coding: utf-8 -*-
"""工作区脚本共用：定位公共区/项目根/个人区/机房，读名册、读写任务状态、按身份提交并推送。

本文件不单独执行，由 公共区/88-工具箱/脚本/ 下的脚本导入。
路径基准（脚本在 公共区/88-工具箱/脚本/ 下）：
  公共区根 = 脚本目录\\..\\..
  项目根   = 公共区根\\..
  个人区根 = 项目根\\个人区
  机房根   = 项目根\\机房
"""
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

成员名册路径 = "01-成员名册/成员名册.md"
状态枚举 = ["未开始", "进行中", "待本人确认", "已生效", "已交回", "已完成", "阻塞"]


def _脚本目录():
    return os.path.dirname(os.path.abspath(__file__))


def 公共区根():
    return os.path.abspath(os.path.join(_脚本目录(), "..", ".."))


def 项目根():
    return os.path.abspath(os.path.join(公共区根(), ".."))


def 个人区根():
    return os.path.join(项目根(), "个人区")


def 机房根():
    return os.path.join(项目根(), "机房")


def 报错退出(msg):
    print("错误：" + msg)
    sys.exit(1)


def 读文件(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def 写文件(p, 文):
    d = os.path.dirname(p)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(文)


def 读名册():
    """成员名册.md 的全部行（成员 + 相关人员）。名册是身份的唯一正本。"""
    p = os.path.join(公共区根(), 成员名册路径)
    rows = []
    if not os.path.exists(p):
        return rows
    for line in 读文件(p).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        first = cells[0]
        if first in ("代号", "---") or set(first) <= set("-: "):
            continue
        rows.append({
            "代号": cells[0], "姓名": cells[1], "类别": cells[2],
            "在项目里承担什么": cells[3] if len(cells) > 3 else "",
            "对接谁": cells[4] if len(cells) > 4 else "",
            "口径归属": cells[5] if len(cells) > 5 else "",
        })
    return rows


def 成员们():
    return [r for r in 读名册() if r.get("类别") == "成员"]


def 成员代号们():
    return [r["代号"] for r in 成员们()]


def 成员清单():
    return 成员代号们()


def 岗位(代号):
    return 代号.split("（")[0] if "（" in 代号 else 代号


def 取身份(代号):
    """代号 -> (git user.name, git user.email)。姓名取名册，邮箱统一 p{n}@brand.local。"""
    if 代号 == "协同系统":
        return ("协同系统", "collab-bot@brand.local")
    for i, r in enumerate(成员们()):
        if r["代号"] == 代号:
            return (r["姓名"], "p%d@brand.local" % (i + 1))
    报错退出("名册里没有代号 " + 代号 + "，先让统筹登记名册")


def 读任务状态(p):
    d = {"task": "", "from": "无", "status": "未开始", "blocked_by": "无", "outputs": [], "updated": ""}
    if not os.path.exists(p):
        return d
    for line in 读文件(p).splitlines():
        s = line.rstrip("\n")
        if s.startswith("task:"):
            d["task"] = s[len("task:"):].strip()
        elif s.startswith("from:"):
            d["from"] = s[len("from:"):].strip()
        elif s.startswith("status:"):
            d["status"] = s[len("status:"):].strip()
        elif s.startswith("blocked_by:"):
            d["blocked_by"] = s[len("blocked_by:"):].strip()
        elif s.startswith("updated:"):
            d["updated"] = s[len("updated:"):].strip()
        elif s.strip().startswith("- "):
            d["outputs"].append(s.strip()[2:].strip())
    return d


def 列任务包(代号):
    """返回本人全部 (任务名, 任务状态 dict)。"""
    base = os.path.join(个人区根(), 代号 + "仓", "02-任务")
    out = []
    if not os.path.isdir(base):
        return out
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            continue
        y = os.path.join(d, "任务状态.yaml")
        if not os.path.exists(y):
            continue
        st = 读任务状态(y)
        if not st["task"]:
            st["task"] = name
        out.append((name, st))
    return out


def 读工作台():
    """公共区 00-推进管理/工作台区 全部条目。"""
    条目 = []
    d = os.path.join(公共区根(), "00-推进管理", "工作台区")
    for 名 in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not 名.endswith(".md"):
            continue
        代号 = 名[:-3]
        for 行 in 读文件(os.path.join(d, 名)).splitlines():
            if not 行.strip().startswith("|"):
                continue
            格 = [c.strip() for c in 行.strip().strip("|").split("|")]
            if len(格) < 5 or 格[0] in ("任务名", "---") or set(格[0]) <= set("- "):
                continue
            条目.append({"代号": 代号, "任务名": 格[0], "状态": 格[1], "任务包": 格[2],
                        "单据": 格[3], "updated": 格[4]})
    return 条目


def 校验日期(值):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", 值 or ""):
        报错退出("日期要写成 YYYY-MM-DD，收到的是 " + str(值))
    return 值


def 时间戳(日期, 时刻="12:00"):
    if not re.fullmatch(r"\d{2}:\d{2}", 时刻 or ""):
        报错退出("时刻要写成 HH:MM，收到的是 " + str(时刻))
    return 日期 + "T" + 时刻 + ":00 +0800"


def 是git仓(仓):
    return os.path.isdir(os.path.join(仓, ".git"))


def 跑(cmd, cwd=None, 环境=None, 允许失败=False):
    e = dict(os.environ)
    e["LC_ALL"] = "C.UTF-8"
    for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_QUARANTINE_PATH"):
        e.pop(k, None)
    if 环境:
        e.update(环境)
    r = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0 and not 允许失败:
        报错退出("命令失败 " + " ".join(cmd) + "\n" + (r.stdout or "") + (r.stderr or ""))
    return r


def 有远端(仓):
    r = 跑(["git", "remote"], cwd=仓, 允许失败=True)
    return "origin" in (r.stdout or "")


def 提交并推送(仓, 提交信息, 作者名, 作者邮箱, 日期, 时刻="12:00"):
    """按指定身份与日期提交并推送。不在 git 仓里就只落文件不提交；无变更不产生提交。"""
    if not 是git仓(仓):
        print("本目录不是 git 仓，跳过提交与推送：" + 仓)
        return
    戳 = 时间戳(日期, 时刻)
    环境 = {"GIT_AUTHOR_NAME": 作者名, "GIT_AUTHOR_EMAIL": 作者邮箱,
            "GIT_COMMITTER_NAME": 作者名, "GIT_COMMITTER_EMAIL": 作者邮箱,
            "GIT_AUTHOR_DATE": 戳, "GIT_COMMITTER_DATE": 戳}
    跑(["git", "add", "-A"], cwd=仓)
    r = 跑(["git", "diff", "--cached", "--quiet"], cwd=仓, 允许失败=True)
    if r.returncode == 0:
        print("没有变更，不产生提交")
        return
    跑(["git", "commit", "-m", 提交信息], cwd=仓, 环境=环境)
    if 有远端(仓):
        跑(["git", "pull", "--rebase", "origin", "main"], cwd=仓, 环境=环境, 允许失败=True)
        跑(["git", "push", "origin", "HEAD:main"], cwd=仓)
