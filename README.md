# 新闻短视频 Skill

用一份可核查的脚本清单制作新闻短片。先选叙事结构，逐条登记事实、日期和素材出处，再输出带字幕、图卡和旁白的1080p视频。

- 支持事件介绍、倒叙、时间线、机制解释、数据核查等八类结构。
- 每段绑定事实编号，检查时间顺序、素材日期、引语身份和转述标记。
- 输出MP4、SRT、剪辑与署名清单。不登录账号，不代发社交平台。
- 旁白可用录音，也可选配本地Piper普通话音色Chaowen。AI音频在成片标注。

## 新闻配乐素材库

[试听并下载原创配乐](music/README.md)：悬疑调查和太空纪实各一段，含MP3、生成脚本和旁白混音示例。制作样片时可先选音乐，再根据事实节奏剪转场。

## 五分钟试跑

以Linux为例。需要Python 3.10+、FFmpeg（含ffprobe和libx264）、Noto Sans CJK、libfluidsynth.so.3及一个本地General MIDI SoundFont。Debian/Ubuntu对应系统包通常为 `ffmpeg fonts-noto-cjk libfluidsynth3 timgm6mb-soundfont`；若字体或SoundFont位置不同，在渲染命令中传入 `--font`、`--bold`、`--soundfont`。本仓库不分发字体、SoundFont或模型。

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p media out
python scripts/story_preflight.py examples/artemis-text-only.json
python scripts/broadcast.py examples/artemis-text-only.json --media media --out out
```

这个示例只用原创图卡，渲染无需下载NASA视频。查看 `out/broadcast-preview.mp4`、`out/captions.srt` 和 `out/edit-and-credits.json`。可选普通话配音见[离线旁白](references/stock-voice.md)。

在支持 `SKILL.md` 的助手里，按该助手的技能安装方式放入完整仓库目录；`SKILL.md`、`scripts/`、`references/`和`examples/`保持相对路径。只想手动剪辑，直接运行上面的命令即可。

## 改成自己的新闻

1. 复制示例JSON，按[叙事结构](references/story-structures.md)选择 `editorial.structure`。给每条事实填日期、原始URL、定位说明和事实类别。区分报道当时已知的信息与后来才知道的结果。
2. 给每段填事实编号、画面类型、秒数与字幕。现场画面、资料镜头与说明图分开标记。NASA素材可运行 `python scripts/discover.py 'Artemis I Orion splashdown' --year 2022 --limit 6` 找候选；下载前核对具体文件的授权和署名要求。
3. 按[制作说明](references/production.md)准备本地素材。尺寸、剪辑点和路径以你实际下载的版本为准。先跑预检，再渲染并看完整成片。核对字幕、引语、混音、素材日期和出处后，才考虑发布。

公开可看不等于可改编、分发或用作宣传。逐个核对画面、音乐、声音及第三方标志的权利。素材、声音模型及库有各自条款；仓库的代码许可不能替代这些条款。推荐在公开贴文中附原始报道链接和必要署名。

```sh
python -m unittest discover -s scripts -p 'test_*.py'
```

## 两条成片示例

- **30秒｜机制解读**：对比两次猎户座返航的隔热盾脱落点，解释再入轨迹改变了什么。
- **29秒｜数据核对**：用同站点同月份比较二氧化碳读数，展示季节性会如何改变短期趋势的解读。

事实来源和音色署名见[样片资料与署名](references/demo-credits.md)。
