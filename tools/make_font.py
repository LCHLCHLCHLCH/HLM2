#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把开源中文字体子集化，只保留工程里真正用到的字符。

用法（在仓库根目录执行）：

    python3 tools/make_font.py --src NotoSansSC-Regular.otf --out /tmp/game-font.otf

`game/gui.rpy` 里字体写的是 `fonts/simhei.ttf`，构建脚本会把这个子集字体
按该文件名放进包里，所以工程文件不用为 CI 改动。子集只保留 game/*.rpy
出现过的字符 + ASCII + 常用中英标点，体积从 8 MB 级降到 1-3 MB。

为什么不在包里直接放 simhei.ttf：中易黑体是 Windows 自带字体，公开再分发不合适。
"""

import argparse
import glob
import io
import os
import sys

# 追加的符号集：字幕里可能出现的半角/全角标点与数字
EXTRA = (
    " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    ".,!?;:\"'()[]{}<>+-=/%#@&*_~^|\\"
    "，。！？；：、“”‘’（）《》〈〉【】〔〕…—～·「」『』％＃＠＆＊＋－＝／＼｜"
    "０１２３４５６７８９"
)


def collect_text():
    chars = set(EXTRA)
    files = sorted(glob.glob("game/*.rpy"))
    if not files:
        raise SystemExit("当前目录下没有 game/*.rpy，请在仓库根目录执行")
    for path in files:
        chars |= set(io.open(path, encoding="utf-8", errors="ignore").read())
    chars.discard("\r")
    chars.discard("\n")
    return "".join(sorted(chars)), files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="源字体（ttf/otf/ttc）")
    ap.add_argument("--out", required=True, help="输出字体路径")
    args = ap.parse_args()

    from fontTools import subset

    text, files = collect_text()
    print("扫描 %d 个脚本，用到的字符 %d 个" % (len(files), len(text)))

    opts = subset.Options()
    opts.layout_features = []          # 中文不依赖 OpenType 排版特性，去掉能省不少体积
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    opts.name_languages = ["*"]
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables += ["DSIG"]

    font = subset.load_font(args.src, opts)
    subsetter = subset.Subsetter(opts)
    subsetter.populate(text=text)
    subsetter.subset(font)
    subset.save_font(font, args.out, opts)

    src_size = os.path.getsize(args.src) / 1048576.0
    out_size = os.path.getsize(args.out) / 1048576.0
    print("%s: %.2f MB -> %s: %.2f MB" % (args.src, src_size, args.out, out_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
