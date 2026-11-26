# 新闻配乐素材库

两段22秒原创纯音乐。独立合成旋律、和声和声响，不含电影原声、节目片头、人声或第三方采样。

| 素材 | 适合的段落 | 结构 |
| --- | --- | --- |
| [A 悬疑调查](assets/A-suspense.mp3) | 追踪事件、技术事故调查、线索比对 | 低音钢琴、低弦与稀疏敲击，约每5秒一次转折 |
| [B 轨道远景](assets/B-orbit.mp3) | 航天、科学、纪录片式解释 | 管风琴式泛音、渐入弦乐、开阔尾音，后半段逐层推进 |

## 混音

先把实拍和旁白剪对。导语落下前可留短暂现场声或音乐，解释段让音乐退到旁白后面。两条试听成品响度接近，约−18 LUFS；混到有旁白的视频时，从音乐降12dB试起。下面的示例随人声自动压低底乐；正式剪辑要在句间试听底乐回升的速度。超过22秒可先循环预览，成片尽量用整乐句交叉淡化，避免直接硬接。

```sh
ffmpeg -i narration.wav -stream_loop -1 -i music/assets/B-orbit.mp3 \
  -filter_complex '[0:a]aresample=48000,asplit=2[n][k];[1:a]volume=0.25[b];[b][k]sidechaincompress=threshold=0.025:ratio=4:attack=20:release=300[m];[n][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]' \
  -map '[a]' -c:a pcm_s16le mixed.wav
```

## 重建素材

Python 3.10+，需NumPy、SciPy和FFmpeg。运行 `python music/render_scores.py` 可复现两个MP3。单独下载成品无需安装这些依赖。库内只收原创或经核实可分发的音乐；第三方素材记录出处、许可范围与署名。

## 原创音效

| 素材 | 用法 |
| --- | --- |
| [短气流](sfx/air-sweep.mp3) | 约0.64秒，用于实拍切图解。让尾巴落在下一镜头开头 |
| [低频落点](sfx/soft-impact.mp3) | 约0.92秒，放在关键数字出现时；避免做成实拍里的撞击声 |
| [数据提示](sfx/data-tick.mp3) | 约0.33秒，给图表的一个关键动作，连续数字不逐个加 |
| [低频空间底](sfx/low-room-tone.mp3) | 5.5秒，铺在机制示意段，和纪实现场声分开 |

可用 `python music/render_sfx.py` 重建这四个文件，依赖同上。更多选择见[外部配乐和音效](sources.md)，里面有逐条许可、出处和署名格式。

## 现场声怎么放

有真实录音时，先保留事件自己的声音。可单独标注NASA直播的溅落确认，把旁白放在确认之后，音乐只在空隙抬头。短气流和提示音只辅助段落和图表，不能冒充现场证据。
