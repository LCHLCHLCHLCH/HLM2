## 这是什么

《红楼梦：林黛玉与北静王》(2010, BTpig) 的 Ren'Py 移植版，**文字版**：

- 包含：Ren'Py 8.5.3 引擎、全部剧本（`game/script.rpa`）、界面美术与字体（`game/ui.rpa`）
- 不包含：背景 / 立绘 / CG（`images/`）、语音与音乐（`audio/`）、影片（`video/`）

没有素材时游戏不会报错，按「缺素材降级」逻辑运行：背景纯黑、立绘位置透明、没有声音，
剧情、选项、分支、存档、章节标题全部正常。想看到完整画面与配音，把自己那份素材
打包成 RPA 放进 `game/` 即可：

```bash
cd game
python ../tools/mk_rpa.py images.rpa images/
python ../tools/mk_rpa.py audio.rpa  audio/
python ../tools/mk_rpa.py video.rpa  video/
```

引擎启动时会自动扫描 `game/*.rpa` 并合并索引，不需要改任何配置。

## 运行

解压后双击 `HongLou.exe`（Windows x64）。存档写在 `%APPDATA%\RenPy\HLM-RenPy`。

## 声明

本项目仅用于对已购买 / 持有的原版游戏做兼容性研究与个人移植验证，
工程内不含原版的图像、语音、影片与字体资源，请勿分发原版资源。
