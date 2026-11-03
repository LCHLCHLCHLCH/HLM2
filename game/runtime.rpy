# Runtime support for the generated Ren'Py port.
# All media is loaded from the local game directory.

init -1 python:
    import json
    import re
    import os
    import time
    renpy.audio.music.register_channel("se", "sfx", loop=False)

    _mf = renpy.open_file("data/asset_manifest.json")
    try:
        asset_manifest = json.loads(_mf.read().decode("utf-8"))
    finally:
        _mf.close()

    def asset_id(name):
        s = re.sub(r"[^A-Za-z0-9_]", "_", str(name))
        if not s or s[0].isdigit():
            s = "_" + s
        return s

    _missing_log_state = {"path": None, "logged": set()}

    def _missing_log_path():
        if _missing_log_state["path"]:
            return _missing_log_state["path"]
        candidates = []
        for base in (getattr(renpy.config, "basedir", None), getattr(renpy.config, "savedir", None)):
            if base:
                candidates.append(os.path.join(base, "missing_assets.log"))
        candidates.append(os.path.abspath("missing_assets.log"))
        for path in candidates:
            try:
                parent = os.path.dirname(path)
                if parent and not os.path.isdir(parent):
                    os.makedirs(parent, exist_ok=True)
                _missing_log_state["path"] = path
                return path
            except Exception:
                continue
        return None

    def missing_asset(kind, name, detail=""):
        key = (str(kind), str(name))
        if key in _missing_log_state["logged"]:
            return
        _missing_log_state["logged"].add(key)
        path = _missing_log_path()
        if not path:
            return
        try:
            new = not os.path.exists(path)
            with open(path, "a", encoding="utf-8") as f:
                if new:
                    f.write("# Missing assets log for HongLouMeng2 Ren'Py port" + chr(10))
                    f.write("# time" + chr(9) + "kind" + chr(9) + "name" + chr(9) + "detail" + chr(10))
                row = chr(9).join([time.strftime("%Y-%m-%d %H:%M:%S"), str(kind), str(name), str(detail)])
                f.write(row + chr(10))
        except Exception:
            pass

    for _name, _path in asset_manifest.get("bg", {}).items():
        if _path:
            renpy.image("bg_" + asset_id(_name), _path)
    for _name, _path in asset_manifest.get("cg", {}).items():
        if _path:
            renpy.image("cg_" + asset_id(_name), _path)
    for _name, _path in asset_manifest.get("chars", {}).items():
        if _path:
            renpy.image("char_" + asset_id(_name), _path)

    def eval_expr(node):
        if not isinstance(node, (list, tuple)):
            return node
        if not node:
            return 0
        op = node[0]
        if op == "lit":
            return node[1] if len(node) > 1 else 0
        if op == "bin":
            a = eval_expr(node[2])
            b = eval_expr(node[3])
            oper = node[1]
            if oper == "==": return a == b
            if oper == "!=": return a != b
            if oper == ">": return a > b
            if oper == "<": return a < b
            if oper == ">=": return a >= b
            if oper == "<=": return a <= b
            if oper == "+": return a + b
            if oper == "-": return a - b
            return 0
        if op == "call":
            fn = node[1]
            args = [eval_expr(x) for x in (node[2] if len(node) > 2 else [])]
            if fn == "RGET": return game_vars.get(args[0], 0) if args else 0
            if fn == "HGET": return game_vars.get(args[0], 0) if args else 0
            return 0
        return 0

    def set_var(name, value):
        game_vars[str(name)] = value

    def _num(value):
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            v = value.strip()
            if re.fullmatch(r"-?[0-9]+", v):
                return int(v)
            if re.fullmatch(r"-?[0-9]+\.[0-9]+", v):
                return float(v)
        return value

    def rset(name, value):
        game_vars[str(name)] = _num(value)

    def radd(name, value):
        k = str(name)
        value = _num(value)
        cur = _num(game_vars.get(k, 0))
        try:
            game_vars[k] = cur + value
        except Exception:
            game_vars[k] = value

    def rsub(name, value):
        k = str(name)
        value = _num(value)
        cur = _num(game_vars.get(k, 0))
        try:
            game_vars[k] = cur - value
        except Exception:
            game_vars[k] = 0

    def set_chapter(title, code):
        store.chapter_title = title or code
        store.chapter_code = code or ""
        store.save_name = store.chapter_title

    def format_playtime(seconds):
        try:
            total = int(float(seconds or 0))
        except Exception:
            total = 0
        if total < 0:
            total = 0
        return "%d\u65f6%d\u5206" % (total // 3600, (total % 3600) // 60)

    def toggle_autosave():
        persistent.autosave_on = not persistent.autosave_on
        try:
            config.autosave_frequency = 300 if persistent.autosave_on else 10 ** 9
        except Exception:
            pass

    def change_bg(name):
        renpy.hide("cg")
        store.current_cg = ""
        if name == "BLACK":
            renpy.show("solid_black", tag="bg", zorder=1)
        elif name == "WHITE":
            renpy.show("solid_white", tag="bg", zorder=1)
        else:
            path = asset_manifest.get("bg", {}).get(name)
            if path:
                renpy.show("bg_" + asset_id(name), tag="bg", zorder=1)
            else:
                missing_asset("bg", name, "change_bg")
                renpy.show("solid_black", tag="bg", zorder=1)
        store.current_bg = name

    def show_cg(name):
        path = asset_manifest.get("cg", {}).get(name)
        if path:
            renpy.show("cg_" + asset_id(name), tag="cg", zorder=2)
            store.current_cg = name
        else:
            missing_asset("cg", name, "show_cg")

    def clear_cg():
        renpy.hide("cg")
        store.current_cg = ""

    def _char_transform(pos):
        p = str(pos or "CENTRE").upper()
        names = {
            "LEFT": "char_pos_left", "BLEFT": "char_pos_bleft",
            "BRLEFT": "char_pos_brleft", "LEFTCEN": "char_pos_leftcen",
            "CENTRE": "char_pos_centre", "CENTER": "char_pos_centre",
            "RIGHTCEN": "char_pos_rightcen", "RIGHT": "char_pos_right",
            "BRIGHT": "char_pos_bright",
        }
        return getattr(store, names.get(p, "char_pos_centre"))

    def show_char(cid, pos, slot=0):
        if not cid:
            return
        slot = int(slot)
        path = asset_manifest.get("chars", {}).get(cid)
        if not path:
            missing_asset("char", cid, "show_char")
            return
        if pos is None:
            pos = store.char_positions.get(slot, "CENTRE")
        tr = _char_transform(pos)
        renpy.show("char_" + asset_id(cid), tag="char%d" % slot,
                   at_list=[tr], zorder=10 + slot)
        store.char_positions[slot] = str(pos)
        store.char_cids[slot] = cid

    def hide_char(slot):
        slot = int(slot)
        renpy.hide("char%d" % slot)
        store.char_cids[slot] = ""
        store.char_positions[slot] = "CENTRE"

    def hide_all_chars():
        for slot in range(5):
            renpy.hide("char%d" % slot)
            store.char_cids[slot] = ""
            store.char_positions[slot] = "CENTRE"

    def move_char(pos, slot=0):
        slot = int(slot)
        cid = store.char_cids.get(slot, "")
        if cid:
            show_char(cid, pos, slot)

    # 原版脚本里这些编号用于「……」静默行，归档中本来就没有对应音频文件；
    # 直接按无语音处理，避免每次运行都把她们记进 missing_assets.log。
    silent_voice_ids = set((
        "DY_0400 DY_0522 DY_0844 DY_0906 JY_0365 NH_0438 QQ_0950 QQ_0954 "
        "XR_0187 XR_0348 XR_0507 XR_0965 XR_0976 XR_0981 XR_0988 XR_0995 "
        "XR_1002 XR_1003 XR_1004 XR_1016 XR_1018 XR_1025 XR_1052 XR_1058 "
        "XR_1063 XR_1065 XR_1071 XR_1075 XR_1083"
    ).split())

    def play_voice(vid):
        if not vid or str(vid) in silent_voice_ids:
            renpy.sound.stop(channel="sound")
            return
        path = asset_manifest.get("voice", {}).get(vid)
        if path:
            renpy.sound.play(path, channel="sound")
        else:
            missing_asset("voice", vid, "play_voice")
            renpy.sound.stop(channel="sound")

    def play_bgm(name):
        path = asset_manifest.get("bgm", {}).get(name)
        if path:
            renpy.music.play(path, channel="music", loop=True,
                             fadeout=0.4, fadein=0.4)
        else:
            missing_asset("bgm", name, "play_bgm")

    def stop_bgm():
        renpy.music.stop(channel="music", fadeout=0.5)

    def set_bgm_volume(value):
        try:
            v = float(value)
            if v > 1.0:
                v = v / 100.0
            renpy.music.set_volume(max(0.0, min(1.0, v)), channel="music")
        except Exception:
            pass

    def play_se(name):
        path = asset_manifest.get("se", {}).get(name)
        if path:
            renpy.sound.play(path, channel="se")
        else:
            missing_asset("se", name, "play_se")

    def play_movie(name):
        path = asset_manifest.get("movies", {}).get(name)
        if not path:
            missing_asset("movie", name, "play_movie")
            return
        try:
            renpy.movie_cutscene(path)
        except Exception:
            missing_asset("movie", name, "playback_failed")
            renpy.notify("影片无法播放: " + name)

    def game_end_name(eid):
        return {
            7: "梦醒 / 无缘",
            10: "最坏结果",
            11: "度绪 · 三世情",
            12: "黛玉 · 泪尽",
            13: "宝钗 · 墨绿蝴蝶",
            14: "湘云 · 灰侍者",
            15: "袭人 · 那盆蒲公英",
            16: "琪官 · 归来",
            17: "北静王线结局",
            18: "妙玉线结局",
            19: "晴雯线结局",
            20: "北黛线 · 大荒",
        }.get(int(eid), "结局 %s" % eid)

transform char_pos_bleft:
    xalign 0.10
    yalign 1.0
    zoom 0.86

transform char_pos_left:
    xalign 0.18
    yalign 1.0
    zoom 0.86

transform char_pos_brleft:
    xalign 0.28
    yalign 1.0
    zoom 0.86

transform char_pos_leftcen:
    xalign 0.34
    yalign 1.0
    zoom 0.86

transform char_pos_centre:
    xalign 0.50
    yalign 1.0
    zoom 0.86

transform char_pos_rightcen:
    xalign 0.66
    yalign 1.0
    zoom 0.86

transform char_pos_right:
    xalign 0.82
    yalign 1.0
    zoom 0.86

transform char_pos_bright:
    xalign 0.90
    yalign 1.0
    zoom 0.86

image solid_black = Solid("#000")
image solid_white = Solid("#fff")

define narrator = Character(None, what_color="#1f1a14", ctc=Transform("gui/ui/flower_mark.png", zoom=1.1), ctc_position="nestled")
define center_say = Character(None, screen="center_say_screen", ctc=Transform("gui/ui/flower_mark.png", zoom=1.1), ctc_position="nestled")

default game_vars = {}
default save_name = ""
default persistent.autosave_on = True
default persistent.ui_music = 2
default persistent.ui_sound = 2
default persistent.ui_voice = 2
default persistent.ui_text = 1
default persistent.ui_auto = 1
default persistent.ui_skip = 0
default chapter_title = ""
default chapter_code = ""
default _switch_value = 0
default _cond_value = False
default _case_value = 0
default ending_id = 0
default current_bg = "BLACK"
default current_cg = ""
default char_cids = {0: "", 1: "", 2: "", 3: "", 4: ""}
default char_positions = {0: "CENTRE", 1: "CENTRE", 2: "CENTRE", 3: "CENTRE", 4: "CENTRE"}

label show_ending:
    call screen ending_screen(ending_id)
    return
