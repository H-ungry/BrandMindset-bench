# -*- coding: utf-8 -*-
"""收工同步工作台。读本人个人仓全部任务包的 任务状态.yaml，生成公共区里本人的工作台文件；
传了 --日期 就以「本人身份」提交并推送公共区（供个人仓 post-commit hook 调用）。

用法：
  python sync_desk.py --代号 X [--个人仓 <个人仓路径>] [--日期 YYYY-MM-DD] [--时刻 HH:MM]

工作台只由本脚本写，人不手改。默认个人仓是 个人区/{代号}仓。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 共用 import (公共区根, 个人区根, 取身份, 校验日期, 读任务状态, 写文件,
                   提交并推送, 报错退出, 状态枚举)


def 收集任务(个人仓):
    任务根 = os.path.join(个人仓, "02-任务")
    出 = []
    for 任务 in sorted(os.listdir(任务根)) if os.path.isdir(任务根) else []:
        y = os.path.join(任务根, 任务, "任务状态.yaml")
        if not os.path.exists(y):
            continue
        s = 读任务状态(y)
        if s["task"] != 任务:
            报错退出("task 字段与任务包目录名不一致：" + 任务)
        if s["status"] not in 状态枚举:
            报错退出("状态值不在契约枚举里：" + 任务 + " 是 " + s["status"])
        校验日期(s["updated"])
        出.append(s)
    return 出


def 生成(代号, 个人仓):
    任务们 = 收集任务(个人仓)
    任务们.sort(key=lambda t: (t["updated"], t["task"]))
    行 = ["# %s 的工作台" % 代号, "",
          "由 `88-工具箱/脚本/sync_desk.py` 从本人个人仓全部任务包的 `任务状态.yaml` 生成，本人收工时跑一次，不手改。任务包路径在本人个人仓内，对外不可达；对账用关联单据列。",
          "",
          "| 任务名 | 状态 | 任务包路径 | 关联单据 | updated |",
          "| --- | --- | --- | --- | --- |"]
    for t in 任务们:
        f = t["from"].strip()
        单据 = "无" if f in ("", "无") else os.path.basename(f.replace("\\", "/"))
        行.append("| %s | %s | 02-任务/%s/ | %s | %s |"
                  % (t["task"], t["status"], t["task"], 单据, t["updated"]))
    目标 = os.path.join(公共区根(), "00-推进管理", "工作台区", 代号 + ".md")
    写文件(目标, "\n".join(行) + "\n")
    return len(任务们)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--代号", required=True)
    ap.add_argument("--个人仓", default="")
    ap.add_argument("--日期", default="")
    ap.add_argument("--时刻", default="12:00")
    a = ap.parse_args()

    个人仓 = os.path.abspath(a.个人仓) if a.个人仓 else os.path.join(个人区根(), a.代号 + "仓")
    if not os.path.isdir(os.path.join(个人仓, "02-任务")):
        报错退出("个人仓里没有 02-任务 目录：" + 个人仓)

    n = 生成(a.代号, 个人仓)
    print("工作台已生成：%d 条任务" % n)
    if a.日期:
        校验日期(a.日期)
        名字, 邮箱 = 取身份(a.代号)
        提交并推送(公共区根(), "工作台同步：" + a.代号, 名字, 邮箱, a.日期, a.时刻)
        print("已提交并推送公共区")


if __name__ == "__main__":
    main()
