# -*- coding: utf-8 -*-
"""投递退回单。发起人 = 发出退回的人；接收人 = 原单发起人。

用法：python send_back.py --发起 Y --接收 X --主题 Z --原单 "原签完整文件名" [--理由 "..."] [--期望补充 "..."] [--日期 YYYYMMDD]
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
    ap.add_argument("--理由", default="（待填）")
    ap.add_argument("--期望补充", default="（待填）")
    ap.add_argument("--日期", default=datetime.date.today().strftime("%Y%m%d"))
    a = ap.parse_args()
    册 = 成员代号们()
    for c in (a.发起, a.接收):
        if c not in 册:
            报错退出("名册里没有成员 " + c)
    正文 = ("# {主题} · 退回\n\n"
          "- 原单：{原单}\n- 发出人：{发}\n- 收件人：{收}\n- 日期：{日}\n\n"
          "## 退回理由\n\n{理由}\n\n## 期望补充\n\n{补充}\n").format(
        主题=a.主题, 原单=a.原单, 发=a.发起, 收=a.接收, 日=a.日期, 理由=a.理由, 补充=a.期望补充)
    print("已投递：" + 投递("退回单", a.发起, a.接收, a.主题, 正文, a.日期))


if __name__ == "__main__":
    main()
