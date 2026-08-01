# -*- coding: utf-8 -*-
"""初始化「机房」：模拟服务端。建公共区裸远端、每个成员的私有裸远端、协同系统工作副本，并装 post-receive。

做法：
  1. 建 机房/公共区.git（git init --bare --initial-branch=main）；
  2. 建 机房/远端/{代号}仓.git（8 个，bare）；
  3. 把 机房/公共区.git 设为公共区仓的远端（公共区是 git 仓时才设）；
  4. git clone 出 机房/协同系统/公共区；
  5. 把 88-工具箱/hooks/post-receive 拷到 机房/公共区.git/hooks/ 并加可执行位。

可重复运行，已存在的部件跳过。真实环境里这些远端都在服务器上；本演练全部是本地裸仓。

用法：python 公共区/88-工具箱/脚本/init_server.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 共用 import 公共区根, 项目根, 机房根, 成员代号们, 跑, 是git仓, 报错退出


def 建裸仓(路径, 名):
    if os.path.isdir(路径):
        print("已存在，跳过：" + 名)
        return
    os.makedirs(os.path.dirname(路径), exist_ok=True)
    跑(["git", "init", "--bare", "--initial-branch=main", 路径])
    print("已建裸远端：" + 名)


def 挂公共区远端(裸仓):
    公 = 公共区根()
    if not 是git仓(公):
        print("公共区还不是 git 仓，稍后 git init 时再挂远端")
        return
    r = 跑(["git", "remote"], cwd=公, 允许失败=True)
    if "origin" in (r.stdout or ""):
        print("公共区已挂远端，跳过")
        return
    相对 = os.path.relpath(裸仓, 公).replace("\\", "/")
    跑(["git", "remote", "add", "origin", 相对], cwd=公)
    print("公共区远端已挂：" + 相对)


def 克隆协同系统(裸仓):
    目标 = os.path.join(机房根(), "协同系统", "公共区")
    if os.path.isdir(os.path.join(目标, ".git")):
        print("协同系统工作副本已存在，跳过")
        return
    os.makedirs(os.path.dirname(目标), exist_ok=True)
    跑(["git", "clone", 裸仓, 目标])
    print("已克隆协同系统工作副本：" + os.path.relpath(目标, 项目根()))


def 装post_receive(裸仓):
    源 = os.path.join(公共区根(), "88-工具箱", "hooks", "post-receive")
    目标 = os.path.join(裸仓, "hooks", "post-receive")
    if not os.path.exists(源):
        报错退出("找不到 hooks/post-receive：" + 源)
    os.makedirs(os.path.dirname(目标), exist_ok=True)
    shutil.copyfile(源, 目标)
    os.chmod(目标, 0o755)
    print("已装 post-receive：机房/公共区.git/hooks/post-receive")


def main():
    公裸 = os.path.join(机房根(), "公共区.git")
    建裸仓(公裸, "机房/公共区.git")
    for 代号 in 成员代号们():
        建裸仓(os.path.join(机房根(), "远端", 代号 + "仓.git"), "机房/远端/%s仓.git" % 代号)
    挂公共区远端(公裸)
    克隆协同系统(公裸)
    装post_receive(公裸)
    print("机房就绪。下一步：公共区 git init 并首次提交，再跑 init_member.py --全部")


if __name__ == "__main__":
    main()
