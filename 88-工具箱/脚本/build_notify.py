# -*- coding: utf-8 -*-
"""通知台账。扫全部收件箱里的指向消息，按正件路径去重追加到每人的通知台账。

真实环境由公共区远端的 post-receive hook 调用，再经公司 IM 推送（钉钉）；
本项目不接 IM，只落站内通知台账（内容与 IM 消息一一对应）；不在 git 仓里也能直接跑，
跑两次不重复追加。

用法：python build_notify.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 共用 import 公共区根, 读文件, 写文件, 成员代号们

表头 = ("# %s 的通知台账\n\n"
        "由脚本汇总本人收件箱里的指向消息。谁找我、什么时候、什么动作。\n\n"
        "| 日期 | 类型 | 正件路径 |\n| --- | --- | --- |\n")


def 读指向(路径):
    文 = 读文件(路径)

    def 取(名):
        m = re.search(r"^" + 名 + r"[:：]\s*(.+)$", 文, re.M)
        return m.group(1).strip() if m else ""
    return 取("正件路径"), 取("动作类型"), 取("日期")


def 生成(仓根):
    交换区 = os.path.join(仓根, "04-交换区")
    台账根 = os.path.join(仓根, "00-推进管理", "通知台账")
    os.makedirs(台账根, exist_ok=True)
    新增 = 0
    for 代号 in 成员代号们():
        盒 = os.path.join(交换区, 代号, "收件箱")
        台账 = os.path.join(台账根, 代号 + ".md")
        if not os.path.exists(台账):
            写文件(台账, 表头 % 代号)
        已有 = 读文件(台账)
        行 = []
        for 名 in sorted(os.listdir(盒)) if os.path.isdir(盒) else []:
            if not 名.startswith("指向-"):
                continue
            路径, 类型, 日期 = 读指向(os.path.join(盒, 名))
            if not (路径 and 类型 and 日期):
                continue
            if 路径 in 已有 or 路径 in "".join(行):
                continue
            行.append("| %s | %s | `%s` |\n" % (日期, 类型, 路径))
        if 行:
            with open(台账, "a", encoding="utf-8", newline="\n") as f:
                f.writelines(行)
            新增 += len(行)
    print("通知台账新增 %d 条" % 新增)


if __name__ == "__main__":
    生成(公共区根())
