# 构建状态

- 源游戏：红楼梦：林黛玉与北静王 v1.0（CMGDK 18.47）
- 源脚本：330 个编译脚本，44,410 条指令
- 剧情转译：1,580 个 Ren'Py label，约 3.24 MB，75,721 行
- 未识别命令/操作：0
- Ren'Py 8.5.3 lint：通过（返回码 0）
- 运行时素材清单校验：0 个缺失本地文件
- 运行时依赖 Data.HAC、Local.HAC 或 API：无

## 素材数量

- 背景：300 张实际 PNG（清单 312 条：另含 BLACK/WHITE 与 BG526 别名）
- CG：224 张
- 立绘：869 条映射 / 554 个文件（2026-11 补 19 个 WNA/WTA/YXA + QQA700 L
  别名，并按像素内容去重，L/S 等同图共用一份文件）
- BGM：58 个清单项 / 30 个文件（大小写与重复曲目共用文件）
- SE：75 个
- 语音：6,419 个（2026-11 补 QQ_0365、BC_0579）
- 影片：11 个（992×560 宽屏版，只保留这一档）

## 运行时验证

- 标题菜单：已启动并截图
- 居中旁白：已显示并截图
- 普通对话：已显示并截图
- 中文显示：SimHei 字体已生效
- 立绘：XRA200L 已成功显示，角色名为花袭人
- 鼠标指针：获取到的系统光标句柄与默认箭头不同，自定义蝴蝶指针已生效

截图与 lint 报告位于 verification/。

## 已知缺失

- WNA、WTA、YXA 前缀共 19 个 4 通道 RYC 立绘层：已解决（2026-11）。RYC-4
  格式为 `u32 颜色长度 + RLE YUV420 + u32 alpha 长度 + RLE alpha`，
  19 个立绘已解码并登记；表情/口型切换仍为基础层。
- BG526：原包不存在，已按相同的场景说明（北静王府大门•冬•日间）映射到 BG500。
- 语音：34 个“缺失”拆分为 2 个编号笔误（已修正）、29 条「……」静默行
  （按无语音处理）、3 条真缺失（DY_0393、DY_1000、XR_1079）。
- 音乐：28 首曲目与 28 张曲名图均在原包内，无缺失；曲名图与映射表已导出到
  `逆向分析/Extracted/DreamMusic/`。
- 影片：VIDEO11–21 的 4 个版本（画质 0/1 × wide/normal）共 44 个 OGV 全部存在；
  便携包已从 512×288（1/wide）换成 992×560（0/wide）。

上述剩余项只影响个别画面、语音或界面，不会阻断剧情和分支。

## 2026-11 二次解包

- 新增 RYC 4 通道解码（hgp_tool.py），全档案 33 个 RYC-4 层均可解。
- 立绘映射从 849 增至 869（补 19 个 WNA/WTA/YXA，另加 QQA700 L 别名）。
- 影片统一为 992×560（0/wide）一档，其余画质/画幅版本不再保留。
- 按 SHA-256 去重：324 个像素相同的文件合并为一份，清单保留全部别名，
  立绘 868→554、背景 309→300、BGM 31→30，约省 144 MB。
- `ui_original` 中与 `gui/` 字节相同的 15 个 PNG 已删除，映射见其
  `_dedupe_map.txt`；解包出的低画质/异画幅影片与 `Extracted/Video` 已删除。

## UI 还原（2026-11-03）

- 右键/ESC：打开六枚玉牌菜单（结束游戏/返回游戏/游戏选项/保存存档/读取存档/文字记录），
  黑底、带挂链，和原版一致；存档/读档再进入书卷式界面。
- 对话框：全宽白色纸面底（`#ffffffb0`，贴底、左右无留白，上沿加金色细线与淡阴影），
  黑色正文靠上；人名黑色、居中于白底描边名牌，名牌独立放在白框上沿之上；
  每句末尾用 CTC 显示原版红色小花（`MessageBox/flower` 缩放）。光标保持红色箭头。
- 确认框：覆盖 Ren'Py 默认 `confirm`，用原版绿色横条 + `yesno.TEX` 的
  是/否字块；返回主菜单、退出、覆盖存档等提示改为中文。
- 存档/读档：整屏使用原版 `save1.TEX` 底板（含双面板与「红楼梦/保存游戏」
  侧签），每页 8 个竖排存档位、右侧预览与序号/章节名/时间/游戏时长、
  底部「新/选/自」印章和上下页按钮。
- 选项：用原版 `option/*.HGP` 的绿色标签条、数值按钮、分隔线重建 7 行
  （快进模式、自动存档、语音/音乐/音效音量、文字速度、自动播放速度），
  接到 Ren'Py 实际偏好。
- ESC 菜单沿用六枚玉牌，但换成带挂链的原始 64×300 图。
- 已知缺口：存档位的章节名文字尚未绘制出来（按钮与右侧信息正常）；
  确认框两端圆点被纵向拉伸。

## 立绘尺寸修复（2026-11-03）

- 问题：19 张立绘的原始画布高 1700 / 1230 像素，导出时没有归一化，
  运行时又按 1100 高的统一 0.86 缩放显示，导致人物放大约 1.55 倍、头部被切。
  AA09 场景（TCA100L 贾探春）就是这种情况。
- 处理：把这 19 张统一缩放到 1100 高（宽等比），覆盖原文件；
  原始大图备份在 `逆向分析/Extracted/char_large_backup/`。
  涉及 NNA100–104/200–201、TCA100/101/102/200/201/202/301/302/303、
  QAA100S、YCA100S、YCA201S。
- 复核：554 张立绘全部为 1100 高，无空图、无底部悬空；
  5 张（PRA、ZZA）构图本身偏左/偏右，属美术构图，未改。

## 便携包

- 便携目录：D:\opencode\HongLouMeng2\RenPy版\HongLouMeng2-RenPy-Portable
- 运行时：RenPy 8.5.3，已包含 renpy、lib、sdk-fonts
- 启动：双击“红楼梦.exe”（图标与原版 HongLou.exe 相同，替换了原来的 bat）
- 素材缺失日志：便携包根目录 missing_assets.log

## 背景/CG 遮挡与音频修复

- 已修复 Ren'Py 启动时 scene black 遮住 zorder 为负的背景/CG。
- BG/CG/立绘现在均可见；语音不再被静音通道丢弃，改为独立 sound 通道；SE 使用专用 se 通道。

## 标题菜单与 ESC 菜单还原

- 标题菜单使用原版蓝荷背景、WordHLM、SecondTitle 与 EnterDream/BackDream/ExitDream 资源。
- ESC 菜单使用 MenuRes 原版玉牌资源。
- 光标改为红色箭头，蝴蝶作为窗口图标。

## center_say 修复

- say screen 恢复 window + text id=what，center_say 不再触发 Text object 异常。

## 选项分支修复

- switch 表达式从 ['lit','FLAG...'] 修正为 RGET 读取；106 处菜单分支已修补。

## 存读档界面改版（2026-11-16）

- 左页七条竖栏改成七个存档位，点列即存/读（原来是 8 个隐形按钮，第 8 个在框外）。
  格位名用「页码-格号」（`1-1`…`6-7`），与既有存档文件同名，老存档仍然可见。
- 每格显示竖排章节名；进入 `script_XXXX` 时由 `config.label_callbacks` 查
  `Chapter.CPP` 的 308 条 `SetChapter` 表写进 `save_name`，所以新存档的
  「章节名」不再是空。旧存档没有该字段，格内显示「旧档」。
- 去掉页面底部的三枚红印章（新/选/自）。
- 翻页键重做：整条侧栏都是热区，文字沿用原版竖排「下一页 / 上一页」，
  到首页/末页自动置灰；页码改为 `1 / 6`。
- 缩略图变清晰：`config.thumbnail_width/height` 从 Ren'Py 对 4:3 游戏的默认
  66×50 改成 640×480，预览框按 4:3 显示 480×360（原来把 66×50 放大到
  480×400，糊了 7 倍多）。旧存档的缩略图仍是 66×50，无法追溯修复。
- 踩坑记录：Ren'Py 的 `xpos` 给浮点数是「按容器比例」，`xpos 90.0` 等于把整列
  推到 90 屏宽之外；格位坐标一律用整数。

## 右键/ESC 绕过玉牌菜单进入存档页（2026-11-16 修复）

现象：有时在游戏里右键，不出现六枚玉牌菜单，直接跳到存档界面。

原因：右键走的是 Ren'Py 的 `_game_menu_screen`。这个变量是普通 store 变量，
**会被一起写进存档**。老存档里存的是 Ren'Py 老布局的默认值 `"save_screen"`
（`common/00layout.rpy` 在 `_game_menu_screen is None` 时填的旧标签），
读档时它覆盖了 `options.rpy` 里的 `define _game_menu_screen = "esc_menu"`，
于是 `_game_menu` 直接 `jump save_screen` → 显示 `save` 界面，玉牌菜单被跳过。
所以「有时」= 只有在读过旧存档之后才复现，新开局和重开程序都正常。

实测（临时 trace 脚本，已删）：

```
init999  _game_menu_screen='esc_menu'
读档后    _game_menu_screen='save_screen'
右键      label='_game_menu' → label='save_screen' → show_screen='save'   # 复现
修复后    label='_game_menu' → show_screen='esc_menu'                     # 正常
```

修复：`runtime.rpy` 里把 `_game_menu_screen` 钉回 `esc_menu`，挂到
`config.start_callbacks` 和 `config.after_load_callbacks` 上（开局、每次读档都执行）。
新存档写回的就是 `esc_menu`；旧存档不必改写，读档时会被钉住。

---

## 临时演示入口：芙蓉女儿诔（第四版 + 第五版）

**状态**：已接入，**未**并入主流程（AA172/AA173 原样未动），随时可整块删除。

### 加了什么

| 文件 | 改动 |
|---|---|
| `game/hlm_lei_demo.rpy` | 新增。整段演示 `label hlm_lei_demo`，共 4 场（场一 五更托梦／场二 清晨石后／场三 夜里写诔／场四 芙蓉前读诔＋焚帛／场五 回房），约 200 句。结尾 `renpy.full_restart()` 回标题。 |
| `game/screens.rpy` | `screen main_menu` 末尾加一个 `textbutton "· 试看：芙蓉女儿诔（临时）"`，`xpos 44 ypos 884`，`action Start("hlm_lei_demo")`，上下都有 `# ==== 临时 ====` 注释夹住。 |

主界面三个主按钮（醒梦/归梦/入梦）一个字没改；新按钮在左下角留白处，不重叠、不抢焦点。

### 怎么撤

1. 删 `game/hlm_lei_demo.rpy`；
2. 删 `game/screens.rpy` 里 `# ==== 临时：芙蓉女儿诔试看入口` 到 `# ==== 临时入口结束 ====` 之间的 6 行；
3. 删 `game/hlm_lei_demo.rpyc`（Ren'Py 下次启动也会自己清）。

### 已验证

- `renpy lint`：0 error（对白块 30,499 → 30,699）。
- 真机启动，主界面渲染正常，临时按钮在左下角，未遮挡任何主体元素。
- 鼠标实点该按钮 → 进入 `hlm_lei_demo`，第一场台词/背景/立绘正常。
- 快进跑完整段：场一 → 场五 一次跑通，无 `traceback.txt` / `errors.txt`，结束自动回标题。
- 读诔段（68 块）以 `center_say` 呈现，横贯画面的半透明字幕带、黑字居中，无缺字方框、无溢出。

### 已知取舍

- 场四背景用 `BG330`（凹晶馆池上·夜）顶「池上芙蓉」，全库无芙蓉专用背景。
- 场三「裁一幅冰鲛縠」与后面「纸就卷了」的材质说法不统一，按原文优先取了「縠」，焚的那句留「纸」。
- 演示结束直接 `full_restart` 回标题，不在存档里留下「章节」，也不写 `set_chapter`。

## 2026-11 缺素材降级（文字版运行模式）

**状态**：已接入 `game/runtime.rpy`。素材完整时行为完全不变，没有开关、没有提示、没有额外 UI。

### 加了什么

`game/runtime.rpy` 在 `image solid_white` 之后加了一个 `init -100 python:` 段（约 15 行）：
把 `config.missing_image_callback` 指向 `_hlm_missing_image()`。图片文件不存在时返回
`im.Null(...)`——引擎自带的 1x1 常量 `ImageBase`，`const_size=True` 会自动铺满分配区域：

- 路径含 `/bg/` 或 `/cg/` → `im.Null("#000")`，效果就是纯黑屏；
- 其它（立绘、界面装饰）→ `im.Null((0, 0, 0, 0))`，全透明，不会压住画面。

`asset_manifest.json` 和 `change_bg` / `show_char` 那一层一个字没动，素材齐全时不触发回调。

### 为什么不用别的办法

- 仅把 `config.developer` 关掉只能让引擎不抛异常，画面会残留异常文本（`im.py:640-648` 的 `_image_error`），不干净。
- 音频不需要守卫：`renpy/audio/audio.py:616-626` 的 except 分支只在 `config.debug_sound` 为真时重抛，默认为假，缺 bgm/语音/音效本来就静默。

### 已验证（2026-11-25）

- `renpy lint`：0 error，统计仍是 30,683 对白块 / 95 menus / 14 screens，与基线一致。
- 把 `game/images` 整个移走后启动并跑到 `hlm_lei_demo`：无 traceback、无错误文本，背景纯黑，对白栏、文字、CTC 花标均正常渲染。
- 把 `game/images` 放回后同样跑一遍：背景正常（中心采样色 37,85,136），说明回调在素材齐全时不影响渲染。

### 已知边界

- 只接管图片。`game/fonts/simhei.ttf` 缺失仍会在字体加载阶段报错（引擎没有 missing-font 回调）。
- `game/gui/` 缺失时界面装饰走透明占位，文字仍然可读，只是没有边框和底板。

## 2026-11 文字版发布流水线（GitHub Actions）

**状态**：已接入 `.github/workflows/release-text-only.yml`，推 `v*` tag 或手动 dispatch 触发。

### 产物形态

Ren'Py 标准 Windows 版布局：`HongLou.exe` + `HongLou.py` + `lib/` + `renpy/` + `game/`，其中
`game/` 只有两个 RPA：

| 归档 | 内容 |
|---|---|
| `script.rpa` | 全部 `.rpyc`（不含 `.rpy` 源码）+ `data/asset_manifest.json` |
| `ui.rpa` | `game/gui/**` + 子集化中文字体（按 `fonts/simhei.ttf` 这个名放进包） |

`images.rpa` / `audio.rpa` / `video.rpa` 留给使用者自己补，引擎启动时自动合并索引
（`renpy/loader.py` 的 `index_archives` 扫描 `game/*.rpa`）。

### 工具

| 文件 | 作用 |
|---|---|
| `tools/mk_rpa.py` | 写 RPA-3.0 归档（`python mk_rpa.py out.rpa 目录/`），格式对照 `renpy/loader.py` 的读写实现 |
| `tools/make_font.py` | 扫 `game/*.rpy` 收集用到的字符，把开源中文字体子集化（本机实测 15.35 MB → 1.65 MB，3758 字） |
| `tools/build_textonly.sh` | 编译 → 打 RPA → 装引擎 → 自检，`--sdk <SDK> [--font f] [--out build]` |

### 已验证（2026-11-25）

- 本机用 `--sdk <包内 RenPy/>` 跑完整构建，产物 86 MB；启动后背景纯黑、对白与 CTC 正常，无 `errors.txt` / `traceback.txt`。
- 用子集字体（1.65 MB）构建的包实跑，中文无缺字、无豆腐块。
- 主界面标题图、按钮、书法标题全部从 `ui.rpa` 正常读取，确认 RPA 里的 gui 与字体都能加载。

### 已知边界

- 只出 Windows x64 包；Arm64 需要另外塞 `lib/py3-windows-arm64`，stock SDK 没有。
- 引擎版本锁在 8.5.3（`.github/workflows` 里的 `RENPY_VERSION`），SDK 的 `lib/python3.12` 必须与之匹配。
