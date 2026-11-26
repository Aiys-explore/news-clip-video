# Assemble and verify

Dependencies: Python 3.10+, Pillow, FFmpeg/ffprobe, CJK font. Use `--font` to specify a font file. Commands:

```sh
python scripts/assemble.py examples/artemis.json --media DIR --out OUT
python scripts/assemble.py examples/artemis.json --media DIR --out OUT --narration DIR/user-authorized.wav --voice-kind recorded
```

The manifest is editable. Top-level title, edition, story_source, optional music, assets dictionary, and beats array. Every asset needs a local filename, original source page plus rights URL or written permission reference, visible credit, and rights_status=cleared_for_edit. The flag records a human/agent review decision, not an automated licensing judgment. Optional crop is [width,height,x,y] in source pixels. Leaving music empty renders no backing track. Every beat has a duration, headline, three short data/notes fields, and up to one full-sentence caption. Clip beats also have asset ID and source in. Source out is in+duration. A graphic beat has no asset; give it graphic.title and graphic.steps (2–4 label/sublabel pairs), and optionally graphic.note. Preview timing is an initial cut; after narration, re-time beats/captions to the real audio. The tool pads up to two seconds of trailing silence but rejects narration too long for the edit. If caption changes occur inside a single shot, split the beat into adjacent segments of that shot. Source sound is muted in this starter; separately clear and preserve source audio for any editorial quotation.

For personal voice: capture a clean, explicitly authorized sample (start with 30–60s; model-specific requirements vary). For voice replication a locally deployable option to evaluate is [Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS). Deployment, model license, available hardware and final pronunciation must be checked before promising it; the tool accepts rendered narration, it does not download a model or perform voice cloning. Include AI audio disclosure when using synthetic narration and do not present it as an original interview tape. Check any service consent requirements and user approval before transfers or billing.

Before delivery check cut boundaries, safe titles and fonts, captions versus actual narration and the file's source-attribution rows. Test peak levels and hear final playback. Source references recorded in the sidecar include direct assets, date and rights notes. Compare fact-to-shot role especially where footage is illustrative. For public posting confirm license is suitable for that publication and remove unverified clips. This workflow performs no posting.

## Broadcast template and discovery

```sh
python scripts/discover.py 'Artemis I Orion splashdown' --year 2022 --limit 6
python scripts/broadcast.py examples/artemis-broadcast.json --media DIR --out OUT
```

Discovery fetches metadata, not permission or a downloaded clip. On general news topics, use web search with event name, dates and terms like “press footage”, “raw video”, “b-roll”, and “media kit”; follow primary links rather than scrape a social repost. The NASA example includes reviewed direct download URLs. Where available, pick an official lower-resolution MP4 to avoid downloading a huge original. Keep original URLs, exact in/out and whether shots are real evidence or contextual archive. No account, credentials, bypass, or post is needed.

Broadcast presets are split (portrait/archive+headline), full (wide clip+lower-third), timeline (animated three-stage data graphic), and close (end slate). Cut on score accents or a change in the story, keeping one metric per beat and the bottom line stable. The default score uses an original 120BPM rhythm with string bed, plucked ostinato, brass and restrained hits; it uses a system SoundFont through libfluidsynth and NumPy. No station logo or signature tune is included. For alternate original cues, see the [music library](../music/README.md) and its post-mix example. A private preview may use “private_reference_reviewed” only when the manifest has mode=private_preview. Graphic claims still require evidence. Narration replaces placeholder timing; inspect the final mix with speech ducking and both the caption and cut boundaries. If the target is a fixed A4 paper video, keep this broadcast preset separate.

## Editorial preflight and visual layouts by function

See [story-structures.md](story-structures.md) for choosing the route, required semantic roles, and evidence fields. The renderer automatically checks structured manifests and writes the editorial ledger plus beat-to-fact attribution into the output edit sidecar. Legacy manifests without an `editorial` object still render, but do not get these checks. `statement` is a graphic-only layout for an attributed reaction, method note, or concrete watchpoint; use `graphic.lines` (1–3 concise lines). It does not animate fake time or draw a relationship where there is none. Timeline/close draw sequential milestones; custom charts, maps or process illustrations may be rendered as sourced local visuals and marked `illustration`; visually review on final cut.

```sh
python scripts/story_preflight.py examples/artemis-event-intro.json
python scripts/story_preflight.py examples/artemis-reverse.json
python -m unittest discover -s scripts -p 'test_story_preflight.py'
python scripts/broadcast.py examples/artemis-event-intro.json --media DIR --out OUT
```

The two Artemis examples share original NASA clips with the prior sample. The selected sample is a **private, labeled archive**; NASA dates in the script are editorial source time. Presets do not add statements, facts, natural sound, or real-world dates on their own.

For prebuilt or offline stock narration, use `--voice-kind synthetic-stock` and retain the visible AI narration disclosure. See [stock-voice.md](stock-voice.md) for the optional Chaowen workflow. The original source and model/data permissions remain separate.
