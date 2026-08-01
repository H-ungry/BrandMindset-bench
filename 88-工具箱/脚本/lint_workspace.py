# -*- coding: utf-8 -*-
"""工作区巡检：双仓结构与交换区命名。

检查项：
  1. 公共区是 git 仓；
  2. 每个成员的个人仓是独立 git 仓，且已挂私有远端；
  3. 每人有工作台、交换区出件箱与收件箱，且命名合规；
  4. 任务状态枚举合法。
零违规输出 PASS，有违规逐条列出并以非零码退出。

用法：python lint_workspace.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 共用 import 公共区根, 个人区根, 成员代号们, 状态枚举, 列任务包, 是git仓, 有远端

正件 = re.compile(r"^\d{8}-.+?.+?-.+-(协同单|回执|退回单)\.md$")
收件箱名 = re.compile(r"^指向-.+\.md$")
出件箱名 = re.compile(r"^(\d{8}-.+-(协同单|回执|退回单)\.md|副本-.+\.md|\.gitkeep)$")
个人仓目录 = ["01-输入", "02-任务", "03-生效区", "04-归档区", "09-工作日志"]


def main():
    R = 公共区根()
    P = 个人区根()
    问题 = []

    # 一、公共区是 git 仓
    if not 是git仓(R):
        问题.append("公共区不是 git 仓（缺 公共区/.git）")

    个人区在 = os.path.isdir(P)
    if not 个人区在:
        print("提示：本副本没有 个人区（如协同系统副本），跳过个人仓检查")

    for c in 成员代号们():
        if 个人区在:
            仓 = os.path.join(P, c + "仓")
            if not os.path.isdir(仓):
                问题.append("缺个人仓：" + c + "仓")
            else:
                if not 是git仓(仓):
                    问题.append("个人仓不是独立 git 仓：" + c + "仓")
                elif not 有远端(仓):
                    问题.append("个人仓没挂私有远端：" + c + "仓")
                for d in 个人仓目录:
                    if not os.path.isdir(os.path.join(仓, d)):
                        问题.append("个人仓缺目录：%s仓/%s" % (c, d))
        if not os.path.isfile(os.path.join(R, "00-推进管理", "工作台区", c + ".md")):
            问题.append("缺工作台：" + c)
        for 盒 in ["出件箱", "收件箱"]:
            if not os.path.isdir(os.path.join(R, "04-交换区", c, 盒)):
                问题.append("缺盒子：%s/%s" % (c, 盒))

        出 = os.path.join(R, "04-交换区", c, "出件箱")
        if os.path.isdir(出):
            for f in os.listdir(出):
                if not 出件箱名.match(f):
                    问题.append("出件箱命名违规：%s/%s" % (c, f))
        收 = os.path.join(R, "04-交换区", c, "收件箱")
        if os.path.isdir(收):
            for f in os.listdir(收):
                if not (收件箱名.match(f) or f == ".gitkeep"):
                    问题.append("收件箱命名违规：%s/%s" % (c, f))

        # 任务状态枚举
        for 任务名, st in 列任务包(c):
            if st["status"] not in 状态枚举:
                问题.append("任务状态非法：%s/%s -> %s" % (c, 任务名, st["status"]))

    if 问题:
        print("巡检报出 %d 项：" % len(问题))
        for x in 问题:
            print("  - " + x)
        sys.exit(2)
    print("PASS")


if __name__ == "__main__":
    main()
