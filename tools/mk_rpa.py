#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把资源目录打包成 Ren'Py 的 RPA-3.0 归档。

用法（在 game/ 目录下执行，这样归档里的路径就是引擎要找的相对路径）：

    python ../tools/mk_rpa.py script.rpa *.rpyc data/asset_manifest.json
    python ../tools/mk_rpa.py images.rpa images/
    python ../tools/mk_rpa.py audio.rpa audio/

引擎会在启动时扫描 game/ 下所有 *.rpa 并自动合并索引
（renpy/loader.py 的 index_archives），因此可以按需增删归档，
不需要在 options.rpy 里登记。归档内部路径必须与脚本引用的路径一致，
例如 images/bg/BG01.png、audio/voice/BC_0001.ogg。

RPA-3.0 结构（对照 renpy/loader.py 的 RPAv3ArchiveHandler.read_index）：

    b"RPA-3.0 %016x %08x\\n"     索引偏移、XOR key（共 34 字节）
    各文件原始字节               依次紧排
    zlib(pickle(index))          index: name -> [(offset^key, length^key, b"")]
"""

import os
import pickle
import sys
import zlib

HEADER = "RPA-3.0 %016x %08x\n"
HEADER_LEN = 34
KEY = 0


def collect(paths):
    """把命令行给的目录/文件展开成 (arcname, 绝对路径) 列表。"""
    out = []
    for p in paths:
        p = p.rstrip("/\\")
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for fn in sorted(files):
                    full = os.path.join(root, fn)
                    arc = os.path.relpath(full, ".").replace("\\", "/")
                    out.append((arc, full))
        elif os.path.isfile(p):
            out.append((p.replace("\\", "/"), p))
        else:
            raise SystemExit("找不到：%s" % p)
    out.sort()
    seen = set()
    for arc, _full in out:
        if arc in seen:
            raise SystemExit("归档内路径重复：%s" % arc)
        seen.add(arc)
    return out


def build(out_path, entries):
    index = {}
    with open(out_path, "wb") as out:
        out.write((HEADER % (0, KEY)).encode("ascii"))
        for arcname, full in entries:
            with open(full, "rb") as f:
                data = f.read()
            offset = out.tell()
            out.write(data)
            index[arcname] = [(offset ^ KEY, len(data) ^ KEY, b"")]

        index_offset = out.tell()
        out.write(zlib.compress(pickle.dumps(index, 2)))

        out.seek(0)
        out.write((HEADER % (index_offset, KEY)).encode("ascii"))

    return len(entries), os.path.getsize(out_path)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2

    out_path = argv[1]
    entries = collect(argv[2:])
    if not entries:
        raise SystemExit("没有可打包的文件")

    count, size = build(out_path, entries)
    print("%s: %d 个文件, %.2f MB" % (out_path, count, size / 1048576.0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
