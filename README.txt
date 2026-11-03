# 红楼梦：林黛玉与北静王 — Ren'Py 便携版

双击“红楼梦.exe”即可运行。运行时 RenPy 和游戏素材都在本目录内，不需要安装
Ren'Py，也不需要原来的 Data.HAC、Local.HAC 或 Web 服务。

目录：

    RenPy/                  Ren'Py 8.5.3 运行时
    game/                   独立游戏项目和全部素材
    红楼梦.exe              双击启动（图标与原版游戏一致）
    missing_assets.log      素材缺失日志（第一次出现缺失时自动创建）

如果游戏目录移动了位置，只要保持 RenPy、game 和启动脚本在同一个文件夹即可。
缺失的 BG/CG/立绘/BGM/SE/语音/影片会记录到 missing_assets.log，同一次运行中相同素材只记录一次。

## 缺失素材日志

运行时遇到缺失的背景、CG、立绘、BGM、SE、语音或影片时，会在便携包根目录创建或追加 missing_assets.log。每行记录时间、类型、素材名和触发函数；同一次运行中相同素材只记录一次。

## 图像与音频通道修复

- BG 使用 master 层 zorder 1，CG 使用 zorder 2，均高于 Ren'Py 启动时的 scene black；立绘使用 zorder 10。
- BGM 使用 music 通道；语音使用独立 sound 通道；SE 使用专用 se 通道，避免音效与语音互相打断。
- 修复后通过调试标签实际截图确认 BG、CG、立绘均能显示，语音播放状态为 True。

## 界面还原

- 标题菜单使用原版蓝色荷塘背景、白色书法标题和入梦/归梦/醒梦按钮。
- ESC 菜单使用原版六枚玉牌：结束游戏、返回游戏、游戏选项、保存存档、读取存档、文字记录。
- 鼠标指针改为原版红色箭头；蝴蝶图作为窗口图标。
- 游戏选项、存档、读取和文字记录提供简化面板。

## center_say 修复

- 恢复 say screen 必需的 window 和 text id=what 结构，修复 center_say 报错。

## 选项分支修复

- 修复 switch 变量被当作字符串字面量的问题，改为 RGET 读取 game_vars。
- 共修补 106 处选择分支；选择不同选项会进入对应 label。
