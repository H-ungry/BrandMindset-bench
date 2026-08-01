# -*- coding: utf-8 -*-
"""重建三本索引与人物文件。数据源全在公共区（工作台、交换区、知识区、名册）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 共用 import 公共区根, 成员们, 读名册, 读工作台, 写文件

R = None


def _静态知识():
    d = os.path.join(R, "03-知识区", "01-静态知识")
    return [f for f in sorted(os.listdir(d))] if os.path.isdir(d) else []


def _归集():
    d = os.path.join(R, "03-知识区", "02-动态知识", "归集产出", "current")
    return [f for f in sorted(os.listdir(d))] if os.path.isdir(d) else []


def _单据(代号, 盒):
    d = os.path.join(R, "04-交换区", 代号, 盒)
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d) if f.endswith(".md"))


def _工作台任务(代号):
    return [c["任务名"] for c in 读工作台() if c["代号"] == 代号]


def 文件索引():
    行 = ["# 文件索引", "", "> 按文件查。给出路径与效力级，机器生成。", "", "## 正本", "",
         "| 文件 | 效力级 |", "| --- | --- |"]
    for f in _静态知识():
        行.append("| `03-知识区/01-静态知识/%s` | 正本 |" % f)
    for f in _归集():
        行.append("| `03-知识区/02-动态知识/归集产出/current/%s` | 正本 |" % f)
    行 += ["| `01-成员名册/成员名册.md` | 正本 |", "| `00-推进管理/决策记录.md` | 正本 |",
          "| `公告栏.md` | 正本 |", "", "## 副本", "", "| 来源 | 效力级 |", "| --- | --- |",
          "| 有正件带的 `副本-*` | 副本 |", "", "## 不取", "",
          "草稿（`工作产出/`）、`归集产出/history/`、他人个人仓。", ""]
    写文件(os.path.join(R, "00-推进管理", "索引", "文件索引.md"), "\n".join(行))


def 人物索引():
    行 = ["# 人物索引", "", "> 倒排自 `01-成员名册/`，正本是名册，本表机器生成。", "",
         "| 代号 | 姓名 | 类别 | 人物文件 | 发出单据 | 收到单据 | 工作台任务 |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
    for m in 读名册():
        c = m["代号"]
        发 = len(_单据(c, "出件箱")) if m["类别"] == "成员" else 0
        收 = len(_单据(c, "收件箱")) if m["类别"] == "成员" else 0
        任务 = len(_工作台任务(c)) if m["类别"] == "成员" else 0
        行.append("| %s | %s | %s | `00-推进管理/索引/人物/%s.md` | %d | %d | %d |" %
                 (c, m["姓名"], m["类别"], c, 发, 收, 任务))
    写文件(os.path.join(R, "00-推进管理", "索引", "人物索引.md"), "\n".join(行) + "\n")


def 人物文件():
    for m in 读名册():
        c = m["代号"]
        if m["类别"] != "成员":
            continue
        任务 = _工作台任务(c)
        文 = ("# %s\n\n- 姓名：%s\n- 类别：%s\n"
             "- 发出单据：\n%s\n- 收到单据：\n%s\n- 工作台任务：\n%s\n") % (
            c, m["姓名"], m["类别"],
            "\n".join("  - `%s`" % f for f in _单据(c, "出件箱")) or "  - （无）",
            "\n".join("  - `%s`" % f for f in _单据(c, "收件箱")) or "  - （无）",
            "\n".join("  - %s" % t for t in 任务) or "  - （无）")
        写文件(os.path.join(R, "00-推进管理", "索引", "人物", c + ".md"), 文)


def 关键词索引():
    行 = ["# 关键词索引", "", "> 按事查。机器生成的倒排表。", "", "| 关键词 | 命中文件 | 效力级 |", "| --- | --- | --- |"]
    for f in _静态知识():
        title = f[:-3]
        行.append("| %s | `03-知识区/01-静态知识/%s` | 正本 |" % (title, f))
    行.append("| 分工 / 谁负责 | `01-成员名册/成员名册.md` | 正本 |")
    写文件(os.path.join(R, "00-推进管理", "索引", "关键词索引.md"), "\n".join(行) + "\n")


def main():
    global R
    R = 公共区根()
    文件索引()
    人物索引()
    人物文件()
    关键词索引()
    print("已重建三本索引与人物文件")


if __name__ == "__main__":
    main()
