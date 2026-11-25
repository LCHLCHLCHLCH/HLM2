#!/usr/bin/env bash
# 构建「文字版」发布包：Ren'Py 引擎 + RPA 打包的工程，不含任何图像 / 语音 / 影片素材。
#
#   bash tools/build_textonly.sh --sdk /path/to/renpy-8.5.3-sdk [--font font.otf] [--out build]
#
# 产物布局（Ren'Py 标准 Windows 版，双击 HongLou.exe 运行）：
#
#   HongLou.exe  HongLou.py  lib/  renpy/  game/
#                                       ├── script.rpa   脚本(.rpyc) + data/asset_manifest.json
#                                       └── ui.rpa        game/gui/ + 字体
#
# images.rpa / audio.rpa / video.rpa 由使用者自行补进 game/ 即可（引擎启动时自动合并索引）。
set -euo pipefail

SDK=""
FONT=""
OUT="build"

while [ $# -gt 0 ]; do
    case "$1" in
        --sdk)  SDK="${2:-}";  shift 2 ;;
        --font) FONT="${2:-}"; shift 2 ;;
        --out)  OUT="${2:-}";  shift 2 ;;
        -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
        *) echo "未知参数：$1" >&2; exit 2 ;;
    esac
done

[ -n "$SDK" ] || { echo "缺 --sdk（Ren'Py SDK 目录）" >&2; exit 2; }
[ -d "$SDK" ] || { echo "SDK 目录不存在：$SDK" >&2; exit 2; }

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

SDK="$(cd "$SDK" && pwd)"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"

# Windows(git-bash) 下交给原生程序的路径要转成盘符形式
native() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s\n' "$1"; fi; }

# 选一个能跑 renpy.py 的解释器：优先 Linux 版（CI），退回 Windows 版（本机）
PY=""
for cand in "$SDK/lib/py3-linux-x86_64/python" "$SDK/lib/py3-linux-x86_64/python3" \
            "$SDK/lib/py3-windows-x86_64/python.exe"; do
    [ -x "$cand" ] && { PY="$cand"; break; }
done
[ -n "$PY" ] || { echo "在 SDK 里找不到可用的 python：$SDK/lib/" >&2; exit 2; }

echo "== 1/5 收集工程源码 =="
rm -rf "$OUT/game"
mkdir -p "$OUT/game/data" "$OUT/game/gui" "$OUT/game/fonts"
cp "$REPO"/game/*.rpy "$OUT/game/"
cp -r "$REPO"/game/data/. "$OUT/game/data/"
cp -r "$REPO"/game/gui/.  "$OUT/game/gui/"

if [ -n "$FONT" ]; then
    [ -f "$FONT" ] || { echo "字体不存在：$FONT" >&2; exit 2; }
    cp "$FONT" "$OUT/game/fonts/simhei.ttf"
    echo "   字体：$FONT"
elif [ -f "$REPO/game/fonts/simhei.ttf" ]; then
    cp "$REPO/game/fonts/simhei.ttf" "$OUT/game/fonts/simhei.ttf"
    echo "   字体：沿用工程内 game/fonts/simhei.ttf"
else
    echo "没有字体：gui.rpy 用的是 fonts/simhei.ttf，缺了会在启动时报错，请用 --font 指定" >&2
    exit 2
fi

echo "== 2/5 编译 .rpy -> .rpyc =="
# Ren'Py 在 Windows 上写文件会被目录权限挡住时，退回用游戏自带的 python 也行
"$PY" "$(native "$SDK/renpy.py")" "$(native "$OUT")" compile
ls "$OUT/game"/*.rpyc >/dev/null || { echo "编译没有产出 .rpyc" >&2; exit 1; }

echo "== 3/5 打 RPA =="
( cd "$OUT/game" && "$PY" "$(native "$REPO/tools/mk_rpa.py")" script.rpa *.rpyc data/asset_manifest.json )
( cd "$OUT/game" && "$PY" "$(native "$REPO/tools/mk_rpa.py")" ui.rpa gui fonts )
rm -rf "$OUT/game/gui" "$OUT/game/fonts" "$OUT/game/data"
rm -f  "$OUT/game"/*.rpy "$OUT/game"/*.rpyc
rm -rf "$OUT/game/cache" "$OUT/game/saves"
rm -f  "$OUT"/log.txt "$OUT"/errors.txt "$OUT"/traceback.txt

echo "== 4/5 装引擎（只要 Windows 版） =="
cp "$SDK/renpy.exe" "$OUT/HongLou.exe"
cp "$SDK/renpy.py"  "$OUT/HongLou.py"
rm -rf "$OUT/renpy" "$OUT/lib"
cp -r "$SDK/renpy" "$OUT/renpy"
mkdir -p "$OUT/lib"
cp -r "$SDK/lib/python3.12" "$OUT/lib/"
cp -r "$SDK/lib/py3-windows-x86_64" "$OUT/lib/"
find "$OUT/renpy" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
rm -f "$OUT"/renpy.exe "$OUT"/renpy.py 2>/dev/null || true

echo "== 5/5 自检 =="
for f in HongLou.exe HongLou.py lib/py3-windows-x86_64/python.exe renpy/common/00start.rpyc \
         game/script.rpa game/ui.rpa; do
    [ -e "$OUT/$f" ] || { echo "产物缺文件：$f" >&2; exit 1; }
done
loose=$(find "$OUT/game" -maxdepth 1 \( -name '*.rpy' -o -name '*.rpyc' \) | wc -l)
[ "$loose" -eq 0 ] || { echo "game/ 里还有散装脚本" >&2; exit 1; }
if [ -d "$OUT/game/images" ] || [ -d "$OUT/game/audio" ] || [ -d "$OUT/game/video" ]; then
    echo "game/ 里出现了素材目录，文字版不该带素材" >&2; exit 1
fi

echo
echo "完成：$OUT"
du -sh "$OUT"
ls -lh "$OUT/game"
