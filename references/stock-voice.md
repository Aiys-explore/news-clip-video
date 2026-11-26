# 离线普通话旁白（可选）

成片可以直接使用你有权使用的录音，也可以用Piper的普通话预设音色Chaowen。下面只演示预设音色，不要求个人样本。真人声音的克隆需要本人明示授权，标明AI合成，未经授权不要模仿或冒充。普通录音可换成 `--voice-kind recorded`，获得本人授权的克隆旁白用 `--voice-kind synthetic-own`。两者均需要提前准备音轨。

## 准备模型

1. 执行 `python -m pip install -r requirements-voice.txt`。测试使用Piper 1.8.0。Piper引擎和模型、分词器、训练数据的条款各自独立。
2. 从[Chaowen模型目录](https://huggingface.co/rhasspy/piper-voices/tree/main/zh/zh_CN/chaowen/medium)下载同一版本的 `zh_CN-chaowen-medium.onnx` 与 `zh_CN-chaowen-medium.onnx.json` 到 `models/`。上游[模型卡](https://huggingface.co/rhasspy/piper-voices/raw/main/zh/zh_CN/chaowen/medium/MODEL_CARD)列出声线来源、中文发音要求、训练信息与数据许可。
3. 按[Piper中文发音模块](https://github.com/OHF-Voice/piper1-gpl/blob/main/src/piper/phonemize_chinese.py)指向的[上游g2pW压缩包](https://huggingface.co/datasets/rhasspy/piper-checkpoints/resolve/main/zh/zh_CN/_resources/g2pw.tar.gz?download=true)下载并展开，确保 `models/g2pW/g2pw.onnx` 和 `models/g2pW/config.py` 存在。此配置是运行时会读取的Python文件，只使用可信上游的文件。
4. 下载[上游中文BERT分词器](https://huggingface.co/google-bert/bert-base-chinese/tree/main)的 `tokenizer.json`、`tokenizer_config.json`、`vocab.txt`、`config.json` 到 `models/tokenizer/`；将 `models/g2pW/config.py` 中的 `model_source` 改成该分词器目录的本地绝对路径。无需下载BERT模型权重。记录所选资源版本或本地文件的SHA-256；不要把模型、配置或私人录音提交到仓库。

## 对齐旁白与画面

每个镜头可加中文 `narration` 字段，省略时使用 `caption`。在口语稿内写清读法，尤其是地名、专有名词、单位和百分比。旁白不应补入画面和来源没有支持的判断。脚本默认限制变速；报错时应先缩短旁白或延长镜头。

```sh
mkdir -p out media
python scripts/narrate.py examples/artemis-text-only.json \
  --model models/zh_CN-chaowen-medium.onnx --data models --out out/narration.wav
python scripts/broadcast.py examples/artemis-text-only.json --media media --out out \
  --narration out/narration.wav --voice-kind synthetic-stock
```

生成48kHz单声道WAV，再用侧链压低旁白下的背景音乐。渲染文件会写明“AI合成旁白”。检查数字和人名读音、断句、停顿、口播与字幕的对应关系。旁白默认只在本机合成，脚本不需模型服务密钥。
