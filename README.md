# YUE2-Agent — Multi-Agent Song Generation System for YuE2 Studio

A team of seven specialized agents that turn a one-line brief into a finished, released song by
orchestrating [YuE2 Studio](https://github.com/el-utama/YuE2-Studio) through its MCP server.

## Overview

YUE2-Agent does not reimplement music generation. Each agent owns one craft discipline and hands a
tight artifact to the next: a normalized brief, a style sentence, tagged lyrics, a compliance verdict,
an optional quality pass, and finally an organized release folder. Generation itself is a single MCP
call (`yue2-studio_song_create`) followed by a wait on the job.

```
brief -> manager -> (lyricist || music-stylist) -> reviewer -> (critiquer) -> song_create -> studio_wait -> releaser
```

Everything runs against the studio's MCP tools, so the same rules apply whether the studio runs
headless on a server or with its window open on a desktop.

## Quick start

1. **Install YuE2 Studio** with the music model set downloaded (Settings — Models).
2. **Start it headless** (no window, MCP server only):

   ```bash
   yue2-studio --headless
   ```

3. **Connect its MCP server** to your agent client. The studio exposes its tools under the
   `yue2-studio` server name; the studio's own skill resource is `studio://skill`.
4. **Use the agents.** Ask the manager for a song:

   ```
   manager: write a 3-minute garage-rock song about a night shift at a 24-hour laundromat
   ```

5. Listen in the library, then ask the releaser to file the result into an album folder.

## Agents

| Agent | Role | Key output |
| --- | --- | --- |
| `manager` | Entry point. Interprets the brief, delegates, merges, enforces the quality gate. | Final song package + `song_create` request |
| `lyricist` | Writes lyrics from the brief and the style cues, following `lyric-guide.md`. | Tagged lyric sheet |
| `music-stylist` | Writes the YuE2 style sentence (language, genre, vocal, instruments, mood, production, BPM). | One-line style string |
| `reviewer` | Validates style and lyrics against the YuE2 rules and internal coherence. | Pass/fail with specific fixes |
| `critiquer` | Optional aesthetic pass: singability, emotional impact, weak lines. | Targeted improvements |
| `releaser` | Titles, files and organizes finished tracks into albums and folders. | Release folder layout |
| `tiktok-composer` | Short-form variant: 30–60 s songs built around one hook. | Short song package |

Agent definitions live in `.kilo/agent/`.

## Workflow

1. **manager** normalizes the brief (theme, language, genre, duration, must-have/must-avoid).
2. **lyricist** and **music-stylist** run in parallel when the brief is sufficient.
3. **reviewer** checks the draft; failures route back to the owning agent, up to two revision loops.
4. **critiquer** runs only when the draft is weak or the user asks for a quality uplift.
5. The manager assembles the request and calls `song_create`.
6. `studio_wait` until the job is idle; the song lands in the studio library.
7. **releaser** files the track into the album structure.

## Links

- YuE2 Studio: <https://github.com/el-utama/YuE2-Studio>
- Studio MCP skill: resource `studio://skill` on the `yue2-studio` MCP server
- Lyric craft guide: [`lyric-guide.md`](./lyric-guide.md)
- Agent contracts: [`AGENTS.md`](./AGENTS.md)

## Requirements

- Windows 10 or 11 (64-bit)
- GPU with 6 GB+ VRAM (8 GB+ recommended for full-context generation)
- YuE2 Studio v4.1.0 or newer, with the music model set installed
- An MCP-capable agent client for the seven agent definitions

## License

See the YuE2 Studio repository for the license of the underlying engine and model weights.
