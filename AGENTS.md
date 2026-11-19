# AGENTS.md — Binding Rules for AI Agents in YUE2-Agent

## 1. Required Agents
1.1 **MUST** use the seven custom agents in `.kilo/agent/` for every song generation task:
`manager`, `lyricist`, `music-stylist`, `reviewer`, `critiquer`, `releaser`, `tiktok-composer`.

1.2 **Manager is the entry point.** Any song request starts at `manager`; it delegates to sub-agents automatically. Do not reimplement orchestration in the root agent.

1.3 **No direct MCP tool calls from the root agent.** All `yue2-studio_*` calls (`song_create`, `studio_wait`, stems, exports) go through `manager`.

1.4 `tiktok-composer` handles short-form requests (30–60 s); everything else goes through the normal manager pipeline.

## 2. Sub-Agent Obligations
2.1 **Lyricist MUST read `lyric-guide.md`** before drafting and MUST follow the Global Anti-AI Checklist in it.

2.2 **Music-stylist MUST follow the YuE2 style sentence format exactly** (section 4). No deviations.

2.3 **Reviewer validates compliance** of style and lyrics against this file and `lyric-guide.md`. A reviewer failure blocks the final output.

2.4 **Critiquer improves quality** on a passing draft: singability, emotional weight, weak lines. Its suggestions are optional and must not break reviewer constraints.

2.5 **Releaser handles album and folder organization**: titles, track ordering, naming, folder structure for finished songs.

## 3. Song Length
3.1 Standard songs **MUST be 2:30–4:00** (150–240 s).
3.2 TikTok output **MUST be 30–60 s**.
3.3 No other durations unless the user explicitly overrides and the manager records it.

## 4. Style Sentence Format
Exactly one English sentence, in this order:
```
language, genre + era, vocal, instruments, mood (2-4 words), production, N BPM
```
Rules:
- One sentence only; commas separate the slots.
- Mood is 2–4 words, not a clause.
- Tempo is stated as `N BPM` (integer).
- Vocal describes type and character (e.g. `raspy male lead, close-mic`); say `instrumental` for no vocals.
- Do not stack synonyms or list more than the slots allow.

## 5. Lyrics Format
5.1 Use bracketed sections, one per line, in this set:
`[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]`.

5.2 Separate every section with a blank line. No inline tags, no annotations, no stage directions inside the words.

5.3 Keep density at roughly **2–3 sung words per second**; a 3-minute song carries about 360–540 words total including repeats.

5.4 Section order must make sense musically; a chorus that never repeats is a defect.

## 6. Genre Patterns
6.1 Reference `lyric-guide.md` for per-genre patterns (pop, rock, hip-hop, R&B, country, electronic, latin, K-pop, afrobeats, jazz/blues) before writing in that genre.

6.2 Prefer the guide's craft mechanics (concrete nouns, contractions, slant rhyme, broken symmetry, time/place anchors) over generic poetic phrasing.

## 7. Prohibited Language
7.1 The following clichés are banned outright, in any language:
`heart of gold`, `dance in the rain`, `stars align`, `whispers in the dark`, `set me free`,
`chasing dreams`, `painted skies`, `broken wings`, `light up the night`, `diamond in the rough`,
`against all odds`, `shattered pieces`, `ocean of tears`, `eternal flame`, the `fire/desire/higher`
rhyme trio, `only you`, `forever and a day`, `lost in your eyes`, `mysterious as the night`.

7.2 Also prohibited: greeting-card moral summaries, tidy resolutions on a verse or bridge ending, and abstract emotion stated instead of shown.

## 8. Evidence
8.1 The manager must not report a song as complete without a job id and a finished `studio_wait` result naming the library song.

8.2 Failures are reported with the job id and the studio's error, not paraphrased.

## 9. Precedence
9.1 This file binds over default prompts and over any agent's own habits.

9.2 `lyric-guide.md` binds for lyric craft specifics; where it is more specific than this file, its detail wins for lyric decisions only.
