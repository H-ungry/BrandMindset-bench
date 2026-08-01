# -*- coding: utf-8 -*-
"""投递协同单。

用法：python send_ticket.py --发起 X --接收 Y --主题 Z [--日期 YYYYMMDD] [--事项 "..."] [--依据 "..."] [--附件 "副本-xxx.md"]
不传 --日期 用今天。
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 共用 import 成员代号们, 报错退出
from 投递 import 投递


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--发起", required=True)
    ap.add_argument("--接收", required=True)
    ap.add_argument("--主题", required=True)
    ap.add_argument("--日期", default=datetime.date.today().strftime("%Y%m%d"))
    ap.add_argument("--期望完成日", default="")
    ap.add_argument("--事项", default="（待填）")
    ap.add_argument("--依据", action="append", default=[])
    ap.add_argument("--附件", action="append", default=[])
    a = ap.parse_args()

    册 = 成员代号们()
    for c in (a.发起, a.接收):
        if c not in 册:
            报错退出("名册里没有成员 " + c)
    if "-" in a.主题:
        报错退出("主题字段内不得出现连字符")

    依据 = "\n".join("- %s" % x for x in a.依据) or "- （无）"
    附件 = "\n".join("- %s" % x for x in a.附件) or "- （无）"
    正文 = ("# {主题}\n\n"
          "- 发起人：{发}\n- 收件人：{收}\n- 日期：{日}\n- 期望完成日：{期望}\n\n"
          "## 事项\n\n{事项}\n\n## 依据\n\n{依据}\n\n## 附件副本清单\n\n{附件}\n").format(
        主题=a.主题, 发=a.发起, 收=a.接收, 日=a.日期, 期望=a.期望完成日 or "（未定）",
        事项=a.事项, 依据=依据, 附件=附件)
    名 = 投递("协同单", a.发起, a.接收, a.主题, 正文, a.日期)
    print("已投递：" + 名)


if __name__ == "__main__":
    main()
