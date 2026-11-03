define config.name = _("红楼梦：林黛玉与北静王")
define config.version = "1.0-renpy"
define config.window_title = "红楼梦：林黛玉与北静王"
define config.save_directory = "HLM-RenPy"
define config.has_sound = True
define config.has_music = True
define config.has_voice = True
define config.window_icon = "gui/window_icon.png"
define config.default_text_cps = 35
define config.mouse = {
    "default": [("gui/cursor_default.png", 0, 0)],
    "button": [("gui/cursor_wait.png", 0, 0)],
    "pause": [("gui/cursor_default.png", 0, 0)],
}

# Right click / ESC opens the six jade-tag menu, not the save screen.
define _game_menu_screen = "esc_menu"

# Chinese prompts for Ren'Py's built-in confirmation dialogs.
translate None strings:
    old "Are you sure you want to quit?"
    new "确定要结束游戏吗？"
    old "Are you sure you want to return to the main menu?\nThis will lose unsaved progress."
    new "确定要返回主菜单吗？\n未保存的进度会丢失。"
    old "Are you sure you want to overwrite this save?"
    new "这个存档位已经有存档了，确认覆盖吗？"
    old "Are you sure you want to delete this save?"
    new "确认删除这个存档吗？"
    old "Are you sure you want to load this save?"
    new "确认读取这个存档吗？"
