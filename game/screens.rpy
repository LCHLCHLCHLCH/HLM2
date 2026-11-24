# Original-style UI for the standalone port.
# Layout and artwork follow the original game's 1280x960 screens.

default save_page = 0
default save_sel = "1-1"
default save_sel_idx = 1

init python:
    CN_NUM = "一二三四五六七八九十"

    def save_goto_page(page):
        """翻页后把光标放到新页的第一格，右侧信息栏才不会停在上一页。"""
        store.save_page = page
        store.save_sel = "%d-1" % (page + 1)
        store.save_sel_idx = page * 7 + 1

    def set_autosave(on):
        persistent.autosave_on = bool(on)
        try:
            config.autosave_frequency = 300 if on else 10 ** 9
        except Exception:
            pass


# ---------------------------------------------------------------- dialogue

screen say(who, what):
    window:
        id "window"
        style "say_window"
        text what id "what" style "say_dialogue"
    add Solid("#00000026") xpos 0 ypos 686 xysize (1280, 14)
    add Solid("#a8834f") xpos 0 ypos 698 xysize (1280, 2)
    if who is not None:
        fixed:
            xpos 56
            ypos 630
            xysize (320, 60)
            add "gui/ui/name_plate_white.png" xysize (320, 60)
            text who id "who" style "say_name" xalign 0.5 yalign 0.5
    if chapter_title:
        text chapter_title style "chapter_label"


screen center_say_screen(who, what):
    window:
        id "window"
        style "centered_window"
        if current_bg == "BLACK":
            text what id "what" style "opening_text"
        else:
            text what id "what" style "centered_text"


# ---------------------------------------------------------------- choices

screen choice(items):
    style_prefix "choice"
    vbox:
        xalign 0.5
        yalign 0.55
        spacing 16
        for i in items:
            textbutton i.caption action i.action


# ---------------------------------------------------------------- esc tags

screen esc_tags():
    hbox:
        xalign 0.5
        ypos 36
        spacing 18
        imagebutton:
            idle Transform("gui/menu/exit_game.png", zoom=0.78)
            hover Transform("gui/menu/exit_game.png", zoom=0.82)
            action Quit(confirm=True)
        imagebutton:
            idle Transform("gui/menu/return_game.png", zoom=0.78)
            hover Transform("gui/menu/return_game.png", zoom=0.82)
            action Return()
        imagebutton:
            idle Transform("gui/menu/option.png", zoom=0.78)
            hover Transform("gui/menu/option.png", zoom=0.82)
            action ShowMenu("preferences")
        imagebutton:
            idle Transform("gui/menu/save.png", zoom=0.78)
            hover Transform("gui/menu/save.png", zoom=0.82)
            action ShowMenu("save")
        imagebutton:
            idle Transform("gui/menu/load.png", zoom=0.78)
            hover Transform("gui/menu/load.png", zoom=0.82)
            action ShowMenu("load")
        imagebutton:
            idle Transform("gui/menu/history.png", zoom=0.78)
            hover Transform("gui/menu/history.png", zoom=0.82)
            action ShowMenu("history")


screen esc_menu():
    tag menu
    add Solid("#000000")
    use esc_tags()
    key "game_menu" action Return()


# ---------------------------------------------------------------- main menu

screen main_menu():
    tag menu
    add Transform("gui/title_background.png", xysize=(1280, 960))
    add Transform("gui/title_logo.png", zoom=0.72) xpos 1015 ypos 10
    add Transform("gui/title_subtitle.png", zoom=0.45) xpos 900 ypos 405
    hbox:
        xpos 248
        ypos 380
        spacing 14
        imagebutton:
            idle Transform("gui/menu_exit.png", zoom=0.62)
            hover Transform("gui/menu_exit.png", zoom=0.66)
            action Quit(confirm=True)
        imagebutton:
            idle Transform("gui/menu_back.png", zoom=0.62)
            hover Transform("gui/menu_back.png", zoom=0.66)
            action ShowMenu("load")
        imagebutton:
            idle Transform("gui/menu_enter.png", zoom=0.62)
            hover Transform("gui/menu_enter.png", zoom=0.66)
            action Start()

    # ==== 临时：芙蓉女儿诔试看入口（日后连同 hlm_lei_demo.rpy 一起删）====
    textbutton "· 试看：芙蓉女儿诔（临时）":
        xpos 44
        ypos 884
        text_size 22
        text_color "#8fb4c7"
        text_hover_color "#ffffff"
        text_outlines [(1, "#0b1c26aa", 0, 0)]
        action Start("hlm_lei_demo")
    # ==== 临时入口结束 ====


# ---------------------------------------------------------------- confirm

screen confirm(message, yes_action, no_action):
    modal True
    zorder 200
    add Solid("#00000088")
    frame:
        xpos 250
        ypos 650
        xysize (780, 230)
        background Frame("gui/ui/opt_frame.png", 46, 26)
        padding (60, 24)
        text message:
            style "confirm_text"
            xalign 0.5
            yalign 0.32
            xsize 660
            text_align 0.5
    button:
        xpos 472
        ypos 786
        xysize (72, 72)
        background "gui/ui/confirm_btn.png"
        hover_background "gui/ui/confirm_btn.png"
        action yes_action
        add "gui/ui/yes_idle.png" xalign 0.5 yalign 0.5
    button:
        xpos 732
        ypos 786
        xysize (72, 72)
        background "gui/ui/confirm_btn.png"
        hover_background "gui/ui/confirm_btn.png"
        action no_action
        add "gui/ui/no_idle.png" xalign 0.5 yalign 0.5


# ---------------------------------------------------------------- save/load

screen file_slots(title, mode="save"):
    tag menu
    add "gui/ui/save_bg.png" xysize (1280, 960)
    key "game_menu" action Return()

    # 每页七格，一列一格：位置取自 save_bg.png 左页七条竖栏分隔线
    # （原图像素 72/129/189/248/307/366/426/486 × 1.25）。
    $ cols = (90, 161, 236, 310, 384, 458, 533, 608)
    $ pages = 6

    for i in range(7):
        $ slot = "%d-%d" % (save_page + 1, i + 1)
        $ cx = cols[i]
        $ cw = cols[i + 1] - cx
        $ sname = FileSaveName(slot, slot=True)
        $ slot_action = FileLoad(slot, slot=True) if mode == "load" else FileSave(slot, slot=True)
        $ filled = FileLoadable(slot, slot=True)
        button:
            xpos cx
            ypos 94
            xsize cw
            ysize 770
            background None
            hover_background Solid("#00000012")
            hovered [SetVariable("save_sel", slot), SetVariable("save_sel_idx", save_page * 7 + i + 1)]
            action slot_action
            if sname:
                text chr(10).join(sname.replace(chr(12288), "")) style "slot_name"
            elif filled:
                text chr(10).join("旧档") style "slot_name"
            else:
                text "空" style "slot_empty"
        if save_sel == slot:
            text "▼" style "slot_cursor" xpos (cx + cw // 2 - 11) ypos 54

    # 翻页：整条侧栏都是热区，文字就是原版的竖排「下一页 / 上一页」
    button:
        xpos 0
        ypos 664
        xysize (90, 238)
        background None
        hover_background Solid("#00000012")
        sensitive save_page < pages - 1
        action Function(save_goto_page, min(save_page + 1, pages - 1))
        add Transform("gui/ui/page_next.png", zoom=1.1) xalign 0.5 yalign 0.5 alpha (1.0 if save_page < pages - 1 else 0.3)
    button:
        xpos 1190
        ypos 664
        xysize (90, 238)
        background None
        hover_background Solid("#00000012")
        sensitive save_page > 0
        action Function(save_goto_page, max(save_page - 1, 0))
        add Transform("gui/ui/page_prev.png", zoom=1.1) xalign 0.5 yalign 0.5 alpha (1.0 if save_page > 0 else 0.3)
    $ pgtxt = "%d / %d" % (save_page + 1, pages)
    text pgtxt size 20 color "#6b4a1e" xpos 0 xsize 90 text_align 0.5 ypos 908
    text pgtxt size 20 color "#6b4a1e" xpos 1190 xsize 90 text_align 0.5 ypos 908

    $ sname = FileSaveName(save_sel, slot=True)
    $ sfill = FileLoadable(save_sel, slot=True)
    $ shown_name = sname or ("旧存档" if sfill else "—")
    $ stime = FileTime(save_sel, "%Y-%m-%d %H:%M", empty="—", slot=True)
    $ srun = format_playtime(FileJson(save_sel, "_game_runtime", 0, slot=True))
    add Transform(FileScreenshot(save_sel, slot=True), xysize=(480, 360)) xpos 700 ypos 150
    vbox:
        xpos 720
        ypos 550
        spacing 8
        text "序号：[save_sel_idx]" size 30 color "#2f2417"
        text "章节名：[shown_name]" size 30 color "#2f2417"
        text "" size 14
        text "存档时间：[stime]" size 30 color "#2f2417"
        text "游戏时间：[srun]" size 30 color "#2f2417"


screen save():
    tag menu
    use file_slots("保存存档", "save")


screen load():
    tag menu
    use file_slots("读取存档", "load")


# ---------------------------------------------------------------- options

screen opt_choice(img, px, py, sel, act):
    fixed:
        xpos px - 35
        ypos py
        xysize (70, 52)
        button:
            background None
            hover_background Solid("#ffffff26")
            xysize (70, 52)
            action act
            add Transform(img, zoom=0.72) xalign 0.5 yalign 0.5


screen preferences():
    tag menu
    add Solid("#000000")
    use esc_tags()

    add Solid("#3b3b3b") xpos 125 ypos 328 xysize (1030, 574)
    add Transform("gui/ui/line.png", xysize=(1030, 8)) xpos 125 ypos 320
    add Transform("gui/ui/line.png", xysize=(1030, 8)) xpos 125 ypos 902

    # row 1: skip mode
    add Transform("gui/ui/opt_quickmode.png", zoom=0.82) xpos 185 ypos 368
    add Transform("gui/ui/opt_frame.png", xysize=(545, 52)) xpos 535 ypos 368
    if persistent.ui_skip == 0:
        add Transform("gui/ui/opt_sel.png", xysize=(300, 50)) xpos 548 ypos 369
    if persistent.ui_skip == 1:
        add Transform("gui/ui/opt_sel.png", xysize=(200, 50)) xpos 848 ypos 369
    text ">>>>" xpos 456 ypos 374 size 30 color "#9dbb8a"
    button:
        background None
        xpos 548
        ypos 368
        xysize (300, 52)
        action [SetField(persistent, "ui_skip", 0), SetField(_preferences, "skip_unseen", False)]
        add Transform("gui/ui/opt_Already.png", zoom=0.72) xalign 0.0 yalign 0.5
    button:
        background None
        xpos 848
        ypos 368
        xysize (200, 52)
        action [SetField(persistent, "ui_skip", 1), SetField(_preferences, "skip_unseen", True)]
        add Transform("gui/ui/opt_All.png", zoom=0.72) xalign 0.0 yalign 0.5

    # row 2: autosave
    add Transform("gui/ui/opt_autosave.png", zoom=0.82) xpos 185 ypos 446
    add Transform("gui/ui/opt_frame.png", xysize=(545, 52)) xpos 535 ypos 446
    use opt_choice("gui/ui/val_open.png", 600, 446, persistent.autosave_on, Function(set_autosave, True))
    use opt_choice("gui/ui/val_close.png", 880, 446, not persistent.autosave_on, Function(set_autosave, False))

    # row 3: voice
    add Transform("gui/ui/opt_sounds.png", zoom=0.82) xpos 185 ypos 524
    add Transform("gui/ui/opt_frame.png", xysize=(545, 52)) xpos 535 ypos 524
    use opt_choice("gui/ui/val_null.png", 590, 524, persistent.ui_voice == 0, [SetField(persistent, "ui_voice", 0), Preference("voice volume", 0.0)])
    use opt_choice("gui/ui/val_small.png", 710, 524, persistent.ui_voice == 1, [SetField(persistent, "ui_voice", 1), Preference("voice volume", 0.35)])
    use opt_choice("gui/ui/val_normal.png", 830, 524, persistent.ui_voice == 2, [SetField(persistent, "ui_voice", 2), Preference("voice volume", 0.7)])
    use opt_choice("gui/ui/val_big.png", 950, 524, persistent.ui_voice == 3, [SetField(persistent, "ui_voice", 3), Preference("voice volume", 1.0)])

    # row 4: music
    add Transform("gui/ui/opt_music.png", zoom=0.82) xpos 185 ypos 602
    add Transform("gui/ui/opt_frame.png", xysize=(545, 52)) xpos 535 ypos 602
    use opt_choice("gui/ui/val_null.png", 590, 602, persistent.ui_music == 0, [SetField(persistent, "ui_music", 0), Preference("music volume", 0.0)])
    use opt_choice("gui/ui/val_small.png", 710, 602, persistent.ui_music == 1, [SetField(persistent, "ui_music", 1), Preference("music volume", 0.35)])
    use opt_choice("gui/ui/val_normal.png", 830, 602, persistent.ui_music == 2, [SetField(persistent, "ui_music", 2), Preference("music volume", 0.7)])
    use opt_choice("gui/ui/val_big.png", 950, 602, persistent.ui_music == 3, [SetField(persistent, "ui_music", 3), Preference("music volume", 1.0)])

    # row 5: sound
    add Transform("gui/ui/opt_voice.png", zoom=0.82) xpos 185 ypos 680
    add Transform("gui/ui/opt_frame.png", xysize=(545, 52)) xpos 535 ypos 680
    use opt_choice("gui/ui/val_null.png", 590, 680, persistent.ui_sound == 0, [SetField(persistent, "ui_sound", 0), Preference("sound volume", 0.0)])
    use opt_choice("gui/ui/val_small.png", 710, 680, persistent.ui_sound == 1, [SetField(persistent, "ui_sound", 1), Preference("sound volume", 0.35)])
    use opt_choice("gui/ui/val_normal.png", 830, 680, persistent.ui_sound == 2, [SetField(persistent, "ui_sound", 2), Preference("sound volume", 0.7)])
    use opt_choice("gui/ui/val_big.png", 950, 680, persistent.ui_sound == 3, [SetField(persistent, "ui_sound", 3), Preference("sound volume", 1.0)])

    # row 6: text speed
    add Transform("gui/ui/opt_wordspeed.png", zoom=0.82) xpos 185 ypos 758
    add Transform("gui/ui/opt_frame.png", xysize=(545, 52)) xpos 535 ypos 758
    use opt_choice("gui/ui/val_slow.png", 590, 758, persistent.ui_text == 0, [SetField(persistent, "ui_text", 0), Preference("text speed", 15)])
    use opt_choice("gui/ui/val_normal.png", 710, 758, persistent.ui_text == 1, [SetField(persistent, "ui_text", 1), Preference("text speed", 30)])
    use opt_choice("gui/ui/val_fast.png", 830, 758, persistent.ui_text == 2, [SetField(persistent, "ui_text", 2), Preference("text speed", 55)])
    use opt_choice("gui/ui/val_veryfast.png", 950, 758, persistent.ui_text == 3, [SetField(persistent, "ui_text", 3), Preference("text speed", 100)])

    # row 7: auto-forward speed
    add Transform("gui/ui/opt_autospeed.png", zoom=0.82) xpos 185 ypos 836
    add Transform("gui/ui/opt_frame.png", xysize=(545, 52)) xpos 535 ypos 836
    use opt_choice("gui/ui/val_slow.png", 590, 836, persistent.ui_auto == 0, [SetField(persistent, "ui_auto", 0), Preference("auto-forward time", 8)])
    use opt_choice("gui/ui/val_normal.png", 710, 836, persistent.ui_auto == 1, [SetField(persistent, "ui_auto", 1), Preference("auto-forward time", 5)])
    use opt_choice("gui/ui/val_fast.png", 830, 836, persistent.ui_auto == 2, [SetField(persistent, "ui_auto", 2), Preference("auto-forward time", 3)])
    use opt_choice("gui/ui/val_veryfast.png", 950, 836, persistent.ui_auto == 3, [SetField(persistent, "ui_auto", 3), Preference("auto-forward time", 2)])


# ---------------------------------------------------------------- history

screen history():
    tag menu
    add Solid("#000000")
    use esc_tags()
    frame:
        xpos 150
        ypos 300
        xysize (980, 620)
        background Frame("gui/ui/msg_box.png", 70, 36)
        padding (50, 40)
        viewport:
            yinitial 1.0
            mousewheel True
            draggable True
            vbox:
                spacing 10
                for h in _history_list:
                    vbox:
                        if h.who:
                            text h.who color "#6b4a1e" size 26
                        text h.what color "#2f2417" size 26 substitute False
                if not _history_list:
                    text "暂时没有文字记录。" size 28 color "#2f2417"


# ---------------------------------------------------------------- ending

screen ending_screen(eid):
    modal True
    add Transform("gui/title_background.png", xysize=(1280, 960))
    frame:
        xalign 0.5
        yalign 0.5
        padding (60, 42)
        background Frame("gui/ui/msg_box.png", 60, 30)
        vbox:
            style_prefix "main_menu"
            spacing 18
            text "本章完" size 30 color "#6b4a1e" xalign 0.5
            text game_end_name(eid) size 40 color "#4a2f18" xalign 0.5
            text "结局编号 [eid]" size 20 color "#7a6248" xalign 0.5
            null height 10
            textbutton "返回标题" action Return() xalign 0.5


# ---------------------------------------------------------------- styles

style say_window:
    background "#ffffffb0"
    xpos 0
    xsize 1280
    ysize 260
    yalign 1.0
    padding (64, 46, 64, 10)

style say_name:
    color "#000000"
    size 30

style say_dialogue:
    color "#1f1a14"
    size 30
    line_spacing 8
    xfill True

style slot_box:
    xpos 4
    ypos 4
    size 30
    color "#000"

style slot_cursor:
    font "fonts/simhei.ttf"
    size 26
    color "#c0392b"
    outlines [(1, "#00000033", 0, 0)]

style slot_name:
    font "fonts/simhei.ttf"
    xalign 0.5
    yalign 0.42
    size 34
    color "#2f2417"
    line_spacing 2
    text_align 0.5

style slot_empty:
    font "fonts/simhei.ttf"
    xalign 0.5
    yalign 0.44
    size 40
    color "#8a7355"

style chapter_label:
    color "#d9b77a"
    size 18
    xalign 0.98
    yalign 0.02

style confirm_text:
    color "#1f3517"
    size 34
    line_spacing 8

style opening_text:
    color "#f7f0df"
    size 30
    xpos 90
    ypos 180
    xsize 1100
    text_align 0.0
    line_spacing 12

style centered_text:
    color "#f7f0df"
    size 30
    text_align 0.5
    xalign 0.5
    yalign 0.44
    line_spacing 10

style choice_button:
    background Frame("gui/ui/opt_frame.png", 30, 20)
    hover_background Frame("gui/ui/opt_highlight.png", 20, 14)
    padding (36, 12)
    xminimum 520

style choice_button_text:
    color "#22381c"
    hover_color "#1a2c14"
    size 28
    text_align 0.5
    xalign 0.5

style main_menu_button:
    background "#160d10cc"
    hover_background "#4d2528dd"
    padding (18, 8)
    xminimum 240

style main_menu_button_text:
    color "#f5d48a"
    hover_color "#fff1c7"
    size 28

style main_menu_text:
    color "#e8d8b5"
    size 26

style default:
    font "fonts/simhei.ttf"
    size 26
    color "#f7f0df"
