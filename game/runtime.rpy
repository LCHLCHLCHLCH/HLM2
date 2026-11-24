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

# 章节名表：取自原版 Local.HAC 的 script/Chapter.CPP（308 条 SetChapter）。
# 进入 script_XXXX 时把章节名写进 store.save_name，存档位和右侧信息栏都用它，
# 这也解掉了「章节名永远是 —」的问题；不写 chapter_title 是不想在画面上多出小字。
init -1 python:

    CHAPTER_TITLES = {
        "AA00": "入梦",
        "AA01": "庄周梦蝶",
        "AA02": "梦回前世",
        "AA03": "新的生活",
        "AA04": "刘姥姥　一",
        "AA05": "二春对弈",
        "AA06": "香菱的故事",
        "AA07": "冷香丸制法",
        "AA08": "挖冷香丸",
        "AA09": "金锁",
        "AA10": "颦颦",
        "AA100": "恶梦",
        "AA101": "鸳鸯　一",
        "AA102": "贾环的真情",
        "AA103": "鸳鸯　二",
        "AA104": "苔挞",
        "AA105": "旧手帕",
        "AA106": "绛珠仙草　一",
        "AA107": "金玉钏儿",
        "AA108": "小黄花",
        "AA109": "凭吊金钏儿",
        "AA11": "胭脂印",
        "AA110": "凤姐生日",
        "AA111": "海棠诗社　一",
        "AA112": "当票",
        "AA113": "重逢",
        "AA114": "海棠诗社　二",
        "AA115": "蟹宴",
        "AA116": "贾兰的烦恼",
        "AA117": "灰银手镯",
        "AA118": "海棠诗社　三",
        "AA119": "蒲公英飞散",
        "AA12": "大观园题匾",
        "AA120": "翡镂蝶",
        "AA121": "断发簪",
        "AA122": "紫鹃劝言",
        "AA123": "黛玉与翡镂蝶",
        "AA124": "青檀木与湘云",
        "AA125": "贤宝钗",
        "AA126": "迁怒捻红　一",
        "AA127": "刘姥姥　二",
        "AA128": "参观大观园",
        "AA129": "醉卧怡红院",
        "AA13": "黛玉剪香袋",
        "AA130": "栊翠庵",
        "AA131": "回忆湘云",
        "AA132": "母蝗虫",
        "AA133": "害羞的宝钗",
        "AA134": "迁怒捻红　二",
        "AA135": "泪变少",
        "AA136": "绛珠仙草　二",
        "AA137": "血发簪",
        "AA138": "捻红被撵",
        "AA139": "蝴蝶报梦　一",
        "AA14": "元妃省亲",
        "AA140": "床边的黛玉",
        "AA141": "床边的宝钗",
        "AA142": "床边的湘云",
        "AA143": "袭人求去",
        "AA144": "湘云欲表白",
        "AA145": "通灵宝玉",
        "AA146": "薛蟠提亲",
        "AA147": "赤霞仙女",
        "AA148": "袭人失势",
        "AA149": "旧爱",
        "AA15": "酥酪",
        "AA150": "香菱拜师",
        "AA151": "送黛玉发簪",
        "AA152": "香菱着魔",
        "AA153": "秋窗风雨夕",
        "AA154": "玻璃绣球灯",
        "AA155": "宝钗送还发簪",
        "AA156": "才女资格",
        "AA157": "蝴蝶报梦　二",
        "AA158": "思念捻红",
        "AA159": "寻找捻红",
        "AA16": "红荷包",
        "AA160": "嬉闹",
        "AA161": "鹿肉宴",
        "AA162": "乞红梅",
        "AA163": "元妃病弱",
        "AA164": "可怜的王奶妈",
        "AA165": "假秘术书",
        "AA166": "黛玉恢复记忆",
        "AA167": "湘云昏迷",
        "AA168": "病弱的晴雯",
        "AA169": "坠儿",
        "AA17": "大嘴秋纹",
        "AA170": "抄检风波",
        "AA171": "晴雯和芳官",
        "AA172": "探望晴雯",
        "AA173": "花袭人",
        "AA174": "宝钗搬出大观园",
        "AA175": "元妃赐婚",
        "AA176": "黛玉探望",
        "AA177": "捻红捉了蝴蝶",
        "AA178": "衰弱的宝钗",
        "AA179": "屋顶看星",
        "AA18": "傲慢的李嬷嬷",
        "AA180": "宝钗和贾兰",
        "AA181": "红麝香珠　二",
        "AA182": "入宫见元妃　一",
        "AA183": "墨绿蝴蝶",
        "AA184": "探望黛玉",
        "AA185": "入宫见元妃　二",
        "AA186": "花冢遇黛玉",
        "AA187": "黛玉表白",
        "AA188": "泪尽身亡",
        "AA189": "潇湘馆外",
        "AA19": "病袭人",
        "AA190": "琪官被抓",
        "AA191": "入宫见元妃　三",
        "AA192": "为袭人饯别",
        "AA193": "贾芸之死",
        "AA194": "那盆蒲公英",
        "AA195": "",
        "AA196": "宝钗想要退婚",
        "AA197": "替湘云做衣服",
        "AA198": "湘云陷入昏迷",
        "AA199": "入宫见元妃　四",
        "AA20": "初会贾环",
        "AA200": "空明",
        "AA201": "二人撑篙",
        "AA202": "灰侍者",
        "AA203": "解脱",
        "AA204": "三世情",
        "AA205": "永远的等待",
        "AA206": "宝钗想要退婚",
        "AA207": "度绪",
        "AA208": "赵姨娘生事",
        "AA209": "琪官归来",
        "AA21": "初会蒋玉菡",
        "AA210": "袭人赎身",
        "AA211": "凹晶馆",
        "AA22": "呕吐",
        "AA23": "宝钗生日",
        "AA24": "吃胭脂",
        "AA25": "看画",
        "AA26": "洛神图",
        "AA27": "戏子",
        "AA28": "迁入大观园",
        "AA29": "凹晶馆之夜",
        "AA30": "再现梦境",
        "AA31": "初会贾芸",
        "AA32": "莲花池的秘密",
        "AA33": "宝玉的记忆",
        "AA34": "妙玉",
        "AA35": "凹晶馆的真相",
        "AA36": "黛玉葬花",
        "AA37": "生日的事",
        "AA38": "琪官拜祭父母",
        "AA39": "晋朝画布",
        "AA40": "蘅芜院",
        "AA41": "画像",
        "AA42": "宝钗与袭人",
        "AA43": "春意盎然",
        "AA44": "别样的琪官",
        "AA45": "看云",
        "AA46": "葬花词",
        "AA47": "红麝香珠　一",
        "AA48": "宝玉生日",
        "AA49": "湘云卧芍",
        "AA50": "呆雁",
        "AA51": "怡红夜宴",
        "AA52": "醉袭人",
        "AA53": "丫丫",
        "AA54": "看星",
        "AA55": "袭人夜游　一",
        "AA56": "袭人夜游　二",
        "AA57": "夜叉海鬼",
        "AA58": "珠算",
        "AA59": "扇套子",
        "AA60": "入宫谢恩",
        "AA61": "贾环和彩云",
        "AA62": "金麒麟　一",
        "AA63": "琪官欲走",
        "AA64": "摔玉",
        "AA65": "袭人劝言",
        "AA66": "哄黛玉",
        "AA67": "中暑的黛玉",
        "AA68": "扑蝶",
        "AA69": "陪画洛神图",
        "AA70": "脸伤的真相",
        "AA71": "琪官之约",
        "AA72": "蝴蝶琴　一",
        "AA73": "蝴蝶琴　二",
        "AA74": "绛纹戒指",
        "AA75": "信物",
        "AA76": "金麒麟　二",
        "AA77": "湘云绣花",
        "AA78": "戏弄金钏儿",
        "AA79": "袭人被踢",
        "AA80": "袭人与琪官",
        "AA81": "暴打贾环",
        "AA82": "彩云被撵",
        "AA83": "金钏儿失踪",
        "AA84": "琴音",
        "AA85": "青檀木",
        "AA86": "金钏儿的老父",
        "AA87": "湘云舍命相救",
        "AA88": "探望湘云",
        "AA89": "情深入梦",
        "AA90": "云深与黛玉",
        "AA91": "神秘书籍",
        "AA92": "老太妃薨",
        "AA93": "云深",
        "AA94": "芳官被欺",
        "AA95": "安排琪官逃走",
        "AA96": "捻红",
        "AA97": "傲慢的捻红",
        "AA98": "开始疏远黛玉",
        "AA99": "捻红和琪官",
        "BJ00": "北静王水溶",
        "BJ01": "御赐念珠",
        "BJ02": "王府赏诗",
        "BJ03": "琪官落难",
        "BJ04": "送信",
        "BJ05": "琪官之约",
        "BJ06": "老太妃薨",
        "BJ07": "吊唁",
        "BJ08": "琪官离京",
        "BJ09": "栊翠庵的传闻",
        "BJ10": "长府官索人",
        "BJ11": "祸起",
        "BJ12": "求助元妃",
        "BJ13": "挽留水溶",
        "BJ14": "荷花梦蝶酒",
        "BJ15": "报信",
        "BJ16": "卖画",
        "BJ17": "送别",
        "BJ18": "采莲",
        "BJ19": "诗稿",
        "BJ20": "丫丫的伤",
        "BJ21": "隐情",
        "BJ22": "猩红汗巾的秘密",
        "BJ23": "真假猩红汗巾",
        "BJ24": "元妃的嘱托",
        "BJ25": "最后的莲花",
        "BJ26": "最后的莲花",
        "BJ27": "碎裂的念珠",
        "BJ28": "噩耗",
        "BJ29": "琪官归来",
        "BJ30": "重逢",
        "BJ31": "琪官离去",
        "BJ32": "赐婚",
        "BJ33": "薛家遭难",
        "BJ34": "宝钗之死",
        "BJ35": "入宫",
        "BJ36": "解救琪官",
        "BJ37": "告别",
        "DY00": "心病",
        "DY01": "强娶",
        "DY02": "夜奔",
        "DY03": "衷情",
        "DY04": "指婚",
        "DY05": "泪尽",
        "DY06": "抢亲",
        "DY07": "玉碎",
        "DY08": "奇缘",
        "DY09": "大荒",
        "DY10": "薛蟠提亲",
        "DY11": "元妃赐婚",
        "MY00": "邂逅",
        "MY01": "寻找树苗",
        "MY02": "道谢",
        "MY03": "桃花与梅花",
        "MY04": "初遇蝴蝶",
        "MY05": "生疑",
        "MY06": "再探妙玉",
        "MY07": "捻红",
        "MY08": "捻红入栊翠庵",
        "MY09": "捻红久久未归",
        "MY10": "捻红犯事",
        "MY11": "谈心",
        "MY12": "捻红离去",
        "MY13": "忆酒",
        "MY14": "梅烟旧事",
        "MY15": "听琴",
        "MY16": "乞红梅",
        "MY17": "王妈妈的故事",
        "MY18": "苏醒的记忆",
        "MY19": "梅烟",
        "QW00": "包晴天",
        "QW01": "另一个晴雯",
        "QW02": "苏绣门传说",
        "QW03": "长生殿",
        "QW04": "小小飞贼",
        "QW05": "武晴雯",
        "QW06": "学武",
        "QW07": "重逢之日",
        "QW08": "苔挞",
        "QW09": "玉钏儿",
        "QW10": "海棠诗社",
        "QW11": "晴雯撕扇",
        "QW12": "学做诗",
        "QW13": "夜色诗会",
        "QW14": "孔雀裘",
        "QW15": "补裘",
        "QW16": "病弱的晴雯",
        "QW17": "坠儿",
        "QW18": "抄检风波",
        "QW19": "晴雯与芳官",
        "QW20": "装病",
        "QW21": "离别",
        "QW22": "元妃赐婚",
        "QW23": "绝情的嫁衣",
        "QW24": "折柳亭",
        "QW25": "西域",
    }

    # 右键/ESC 走的是 _game_menu_screen，而这个变量会被写进存档。
    # 老存档里存的是 Ren'Py 默认的 "save_screen"（一个旧标签），读档后它会盖掉
    # options.rpy 里的 esc_menu，于是右键直接跳到存档页、跳过玉牌菜单。
    # 开局与每次读档都钉回来；新存档写回的也是 esc_menu。
    def _pin_game_menu_screen(*args, **kwargs):
        store._game_menu_screen = "esc_menu"

    config.start_callbacks.append(_pin_game_menu_screen)
    config.after_load_callbacks.append(_pin_game_menu_screen)

    def _chapter_label_cb(name, abnormal):
        if not name or not name.startswith("script_"):
            return
        code = name[7:].upper()
        title = CHAPTER_TITLES.get(code)
        if title:
            store.chapter_code = code
            store.save_name = title

    config.label_callbacks.append(_chapter_label_cb)


label show_ending:
    call screen ending_screen(ending_id)
    return
