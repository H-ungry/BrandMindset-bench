# -*- coding: utf-8 -*-
"""归集：把经对方回执确认的生效件放进知识区 current/，旧版进 history/。

用法：python collect.py --来源 "个人区/某代号仓/03-生效区/xxx.md" [--归集名 "xxx.md"] [--日期 YYYYMMDD]
"""
import argparse
import datetime
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 共用 import 公共区根, 项目根, 报错退出


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--来源", required=True, help="相对仓库根的生效件路径")
    ap.add_argument("--归集名", default="")
    ap.add_argument("--日期", default=datetime.date.today().strftime("%Y%m%d"))
    a = ap.parse_args()

    源 = a.来源 if os.path.isabs(a.来源) else os.path.join(项目根(), a.来源)
    if not os.path.isfile(源):
        报错退出("找不到来源件：" + 源)

    名 = a.归集名 or os.path.basename(源)
    base = os.path.join(公共区根(), "03-知识区", "02-动态知识", "归集产出")
    cur = os.path.join(base, "current", 名)
    his = os.path.join(base, "history")

    if os.path.isfile(cur):
        旧 = os.path.join(his, "%s-%s" % (os.path.splitext(名)[0], a.日期) + os.path.splitext(名)[1])
        os.makedirs(his, exist_ok=True)
        shutil.move(cur, 旧)
        print("旧版进历史：" + os.path.relpath(旧, 项目根()))

    os.makedirs(os.path.dirname(cur), exist_ok=True)
    shutil.copyfile(源, cur)
    print("已归集：" + os.path.relpath(cur, 项目根()))


if __name__ == "__main__":
    main()
