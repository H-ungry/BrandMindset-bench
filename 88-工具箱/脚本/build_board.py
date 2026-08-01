# -*- coding: utf-8 -*-
"""任务看板。无人维护：进度只从公共区文件来。

数据源全在公共区，不读任何个人仓路径，因此公共区远端 post-receive 在 机房/协同系统/公共区
副本里也能直接跑：
- 00-推进管理/工作台区/{代号}.md：每人的任务与状态，由 sync_desk.py 从本人任务包的 yaml 生成
- 01-成员名册/成员名册.md：成员与岗位

用法：python build_board.py
"""
import html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 共用 import 公共区根, 成员们, 读工作台, 写文件, 状态枚举

颜色 = {
    "未开始": "#9aa4b2", "进行中": "#2f6fed", "待本人确认": "#c47f17",
    "已生效": "#2e8b57", "已交回": "#6a5acd", "已完成": "#1f7a4d", "阻塞": "#c0392b",
}


def esc(s):
    return html.escape(str(s))


def main():
    条目 = 读工作台()
    rows = []
    for m in 成员们():
        代号 = m["代号"]
        本人 = [c for c in 条目 if c["代号"] == 代号]
        if not 本人:
            rows.append("<tr><td>%s</td><td>%s</td><td colspan=\"4\" class=\"空\">工作台上没有条目</td></tr>"
                        % (esc(代号), esc(m.get("姓名", ""))))
            continue
        for c in 本人:
            色 = 颜色.get(c["状态"], "#333")
            rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s</td>"
                "<td style=\"color:%s;font-weight:600\">%s</td><td>%s</td><td>%s</td></tr>" % (
                    esc(代号), esc(m.get("姓名", "")), esc(c["任务名"]), 色,
                    esc(c["状态"]), esc(c["单据"]), esc(c["updated"])))
    文 = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>品牌新力 · 任务看板</title>
<style>
body{font:14px/1.6 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif;margin:0;background:#f5f6f8;color:#2d3142}
header{background:#fff;border-bottom:1px solid #e3e6ea;padding:16px 28px}
h1{margin:0;font-size:18px}header p{margin:6px 0 0;color:#6b7280;font-size:12px}
main{padding:20px 28px}
table{border-collapse:collapse;width:100%%;background:#fff;font-size:13px}
th,td{border:1px solid #e3e6ea;padding:7px 10px;text-align:left}
th{background:#fafbfc;color:#6b7280;font-weight:600}
td.空{color:#9ca3af}
</style></head>
<body>
<header>
  <h1>品牌新力 · 任务看板</h1>
  <p>无人维护。进度只从文件来：各人个人仓的 <code>任务状态.yaml</code> 经 post-commit hook 由 sync_desk.py 生成公共区工作台，推送后公共区远端 post-receive 重建本页。共 %d 个任务。</p>
</header>
<main>
<table>
<thead><tr><th>成员</th><th>姓名</th><th>任务名</th><th>状态</th><th>关联单据</th><th>updated</th></tr></thead>
<tbody>
%s
</tbody></table>
</main>
</body></html>
""" % (len(条目), "\n".join(rows))
    写文件(os.path.join(公共区根(), "00-推进管理", "任务看板.html"), 文)
    print("已重建任务看板：00-推进管理/任务看板.html（%d 个任务）" % len(条目))


if __name__ == "__main__":
    main()
