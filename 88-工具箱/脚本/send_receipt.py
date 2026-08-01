# -*- coding: utf-8 -*-
"""投递回执。发起人 = 发出回执的人；接收人 = 原单发起人。

用法：python send_receipt.py --发起 Y --接收 X --主题 Z --原单 "原签完整文件名" [--结论 "..."] [--日期 YYYYMMDD]
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
    ap.add_argument("--原单", required=True)
    ap.add_argument("--结论", default="（待填）")
    ap.add_argument("--日期", default=datetime.date.today().strftime("%Y%m%d"))
    a = ap.parse_args()
    册 = 成员代号们()
    for c in (a.发起, a.接收):
        if c not in 册:
            报错退出("名册里没有成员 " + c)
    正文 = ("# {主题} · 回执\n\n"
          "- 原单：{原单}\n- 发出人：{发}\n- 收件人：{收}\n- 日期：{日}\n\n"
          "## 结论\n\n{结论}\n\n## 产出副本清单\n\n- （无）\n").format(
        主题=a.主题, 原单=a.原单, 发=a.发起, 收=a.接收, 日=a.日期, 结论=a.结论)
    print("已投递：" + 投递("回执", a.发起, a.接收, a.主题, 正文, a.日期))


if __name__ == "__main__":
    main()
