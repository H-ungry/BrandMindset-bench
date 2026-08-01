# -*- coding: utf-8 -*-
"""一键启动：按名册里的代号建个人仓（独立 git 仓）、私有远端、git 身份，并在公共区给本人建工作台与收发件箱。

用法：
  python init_member.py --代号 商业化产品（本人）
  python init_member.py --代号 商业化产品（本人） --远端 <私有远端地址>
  python init_member.py --全部

个人仓建在 个人区/{代号}仓，默认私有远端是 机房/远端/{代号}仓.git；不传 --远端 时自动用这个本地裸仓。
已经存在的部件跳过不覆盖，可以重复运行。个人仓里已有的文件（如任务包）不删，纳入首次提交。
"""
import argparse
import datetime
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 共用 import (公共区根, 个人区根, 机房根, 读名册, 成员们, 取身份, 岗位,
                   跑, 写文件, 是git仓, 提交并推送, 报错退出)

个人仓目录 = ["01-输入", "02-任务", "03-生效区", "04-归档区", "09-工作日志"]


def 个人仓README(代号, 姓名, 岗位名):
    return """# %s仓

本仓是 %s（岗位 %s，代号 %s）在「品牌新力」广告项目里的个人仓，装本人的全部工作过程。

## 本仓怎么读

| 目录 | 装什么 |
| --- | --- |
| `01-输入/` | 本人积累的材料、笔记、岗位口径；别人投来的材料副本也收在这里 |
| `02-任务/` | 每个任务一个包，五件套加 `任务状态.yaml`，草稿在包内 `工作产出/` |
| `03-生效区/` | 本人确认后的唯一生效版 |
| `04-归档区/` | 升版前的旧版原样存放，只增不删 |
| `09-工作日志/` | 一天一个文件，收工时写 |

本人对外的进度在公共区 `00-推进管理/工作台区/%s.md`，由本仓的 post-commit hook 在提交动了任务状态时自动跑 `sync_desk.py` 生成并推送，人不手改。

## 与公共区的关系（双仓）

本工作区是**双仓**：公共区是一个共识仓，**每人一个独立个人仓**（本仓），各有私有远端。本仓的提交与推送只走本仓的私有远端；公共区另有一仓、另有一远端。个人仓内容别人看不到，也不该被别人改。

## 对外只有一个通道

要给别人派活或者交回产出，跑公共区 `88-工具箱/脚本/` 下的投递脚本，正件落在公共区交换区。
""" % (代号, 姓名, 岗位名, 代号, 代号)


def 个人仓AGENTS(代号, 姓名, 岗位名):
    return """# AGENTS.md · %s仓规程

公共区 `AGENTS.md` 是全局宪法，本文件只写本仓的具体做法，冲突时以公共区为准。

## 我是谁

- 代号 %s，姓名 %s，岗位 %s。本仓的 git 提交作者就是本人。
- 在本项目中承担什么、对接谁、哪些口径在我手里：公共区 `01-成员名册/成员名册.md` 里本人那一行。
- 项目要拿到什么结果：公共区 `03-知识区/01-静态知识/项目目标.md`。
- 要查别人在项目里干了什么：公共区 `00-推进管理/索引/人物/{对方代号}.md`。

## 开工三读

1. 公共区 `00-推进管理/当前推进.md`：阶段与本人分工。
2. 公共区 `00-推进管理/通知台账/%s.md` 与 `04-交换区/%s/收件箱/`：谁找我。
3. 公共区 `00-推进管理/工作台区/%s.md`：我手头有哪些任务。

## 建包六步

1. 在 `02-任务/{任务名}/` 建五件套与 `任务状态.yaml`。
2. 跑公共区 `88-工具箱/skills/fetch-task-inputs/SKILL.md` 出候选输入清单。
3. 本人确认后写进 `输入清单.md`，此后只读清单内文件。
4. 草稿写进 `工作产出/`，拿不准的记进 `待裁决事项.md` 并标本人裁决还是跨人裁决。
5. 每个动作追加 `过程记录.md`。
6. 本人确认后草稿升 `03-生效区/`，旧版先进 `04-归档区/`。

## 收工三件套，进度自己走

更新 `任务状态.yaml`、追加 `过程记录.md`、写 `09-工作日志/{日期}.md`，然后提交本仓并推送。提交里动了 `任务状态.yaml`，本仓的 post-commit hook 自动跑公共区 `88-工具箱/脚本/sync_desk.py --代号 %s`，把工作台从全部任务包的 yaml 重新生成并推送公共区，公共区远端再重建看板。工作台不手抄；hook 没跑起来就手动跑同一条命令。

## 写回边界

- 可以自动写：本仓 `02-任务/`、`09-工作日志/`；公共区里本人的工作台只经 `sync_desk.py` 写。
- 要本人确认才写：`03-生效区/`、交换区投递与回执、知识区归集。
- 不许写：别人的仓、别人的箱子、公共区治理文件，以及**商户预算金额、商户 ROI 数值**这两类密级数值（**泛品牌词全表**按资产隔离处理，别在公共区留副本）。

## 岗位口径

%s 在本项目中的职责与对接范围见公共区 `01-成员名册/成员名册.md`。本岗掌握的口径不外传副本，别人要用走协同单问。
""" % (代号, 代号, 姓名, 岗位名, 代号, 代号, 代号, 代号, 岗位名)


def 建个人仓(代号, 姓名, 岗位名, 远端参数):
    个人仓 = os.path.join(个人区根(), 代号 + "仓")
    新建 = not 是git仓(个人仓)
    if not os.path.isdir(个人仓):
        os.makedirs(个人仓)
    if 新建:
        跑(["git", "init", "--initial-branch=main", 个人仓])

    # 私有远端：默认 机房/远端/{代号}仓.git
    if 远端参数:
        远端 = 远端参数
    else:
        裸 = os.path.join(机房根(), "远端", 代号 + "仓.git")
        if not os.path.isdir(裸):
            os.makedirs(os.path.dirname(裸), exist_ok=True)
            跑(["git", "init", "--bare", "--initial-branch=main", 裸])
        远端 = os.path.relpath(裸, 个人仓).replace("\\", "/")

    r = 跑(["git", "remote"], cwd=个人仓, 允许失败=True)
    if "origin" not in (r.stdout or ""):
        跑(["git", "remote", "add", "origin", 远端], cwd=个人仓)

    名字, 邮箱 = 取身份(代号)
    跑(["git", "config", "user.name", 名字], cwd=个人仓)
    跑(["git", "config", "user.email", 邮箱], cwd=个人仓)
    跑(["git", "config", "core.autocrlf", "false"], cwd=个人仓)
    跑(["git", "config", "core.quotepath", "false"], cwd=个人仓)

    for d in 个人仓目录:
        dp = os.path.join(个人仓, d)
        os.makedirs(dp, exist_ok=True)
        k = os.path.join(dp, ".gitkeep")
        if not os.path.exists(k) and not os.listdir(dp):
            写文件(k, "")

    # README / AGENTS 按双仓口径写（迁移时覆盖为最新口径）
    写文件(os.path.join(个人仓, "README.md"), 个人仓README(代号, 姓名, 岗位名))
    写文件(os.path.join(个人仓, "AGENTS.md"), 个人仓AGENTS(代号, 姓名, 岗位名))
    if not os.path.exists(os.path.join(个人仓, ".gitattributes")):
        写文件(os.path.join(个人仓, ".gitattributes"), "* -text\n")
    if not os.path.exists(os.path.join(个人仓, ".gitignore")):
        写文件(os.path.join(个人仓, ".gitignore"), "__pycache__/\n*.pyc\n")

    # 个人仓 post-commit hook
    源 = os.path.join(公共区根(), "88-工具箱", "hooks", "post-commit")
    目标 = os.path.join(个人仓, ".git", "hooks", "post-commit")
    if os.path.exists(源):
        os.makedirs(os.path.dirname(目标), exist_ok=True)
        shutil.copyfile(源, 目标)
        os.chmod(目标, 0o755)
    return 个人仓, 远端, (名字, 邮箱), 新建


def 建公共区档案(代号):
    r = 公共区根()
    工作台 = os.path.join(r, "00-推进管理", "工作台区", 代号 + ".md")
    if not os.path.exists(工作台):
        写文件(工作台, """# %s 的工作台

由 `88-工具箱/脚本/sync_desk.py` 从本人个人仓全部任务包的 `任务状态.yaml` 生成，本人收工时跑一次，不手改。任务包路径在本人个人仓内，对外不可达；对账用关联单据列。

| 任务名 | 状态 | 任务包路径 | 关联单据 | updated |
| --- | --- | --- | --- | --- |
""" % 代号)
    for 盒 in ["出件箱", "收件箱"]:
        d = os.path.join(r, "04-交换区", 代号, 盒)
        os.makedirs(d, exist_ok=True)
        gk = os.path.join(d, ".gitkeep")
        if not os.path.exists(gk) and not os.listdir(d):
            写文件(gk, "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--代号", default="")
    ap.add_argument("--全部", action="store_true")
    ap.add_argument("--远端", default="")
    ap.add_argument("--日期", default="")
    ap.add_argument("--时刻", default="12:00")
    a = ap.parse_args()

    名册 = 读名册()
    代号表 = [r["代号"] for r in 成员们()]
    if a.全部:
        选中 = 成员们()
    elif a.代号:
        选中 = [r for r in 名册 if r["代号"] == a.代号]
        if not 选中:
            报错退出("名册里没有代号 " + a.代号 + "，先让统筹登记名册")
        if 选中[0].get("类别") != "成员":
            报错退出(a.代号 + " 不是成员（外圈不建个人仓）")
    else:
        报错退出("请用 --代号 X 指定一名成员，或用 --全部")

    日期 = a.日期 or datetime.date.today().isoformat()
    for r in 选中:
        代号 = r["代号"]
        姓名 = r.get("姓名", "")
        岗位名 = 岗位(代号)
        个人仓, 远端, (名字, 邮箱), 新建 = 建个人仓(代号, 姓名, 岗位名, a.远端)
        建公共区档案(代号)
        # 首次提交个人仓；此时跳过 post-commit 自动同步，保持建档干净
        老 = os.environ.get("SKIP_DESK_SYNC")
        os.environ["SKIP_DESK_SYNC"] = "1"
        try:
            提交并推送(个人仓, "建档：" + 代号 + " 的个人仓", 名字, 邮箱, 日期, a.时刻)
        finally:
            if 老 is None:
                os.environ.pop("SKIP_DESK_SYNC", None)
            else:
                os.environ["SKIP_DESK_SYNC"] = 老
        print("个人仓：" + 个人仓 + ("（新建）" if 新建 else "（已存在）"))
        print("私有远端：" + 远端)
        print("git 身份：%s / %s" % (名字, 邮箱))
        print("工作台同步 hook：.git/hooks/post-commit")
        print("工作台：00-推进管理/工作台区/%s.md" % 代号)
        print("出件箱：04-交换区/%s/出件箱/" % 代号)
        print("收件箱：04-交换区/%s/收件箱/" % 代号)
    print("共处理 %d 名成员" % len(选中))


if __name__ == "__main__":
    main()
