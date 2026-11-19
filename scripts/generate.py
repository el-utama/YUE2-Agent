#!/usr/bin/env python3
"""Generate one song through YuE2 Studio's MCP endpoint. Standard library only."""

import argparse
import json
import os
import shutil
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "http://127.0.0.1:8791/mcp"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULTS = os.path.join(ROOT, "config", "defaults.json")
STATE = {"id": 0, "session": None, "url": DEFAULT_URL, "token": ""}


def _decode(raw):
    raw = raw.strip()
    if not raw:
        return {}
    if raw.startswith("{"):
        return json.loads(raw)
    msg = {}
    for line in raw.splitlines():
        if line.startswith("data:"):
            msg = json.loads(line[5:].strip())
    return msg


def post(payload):
    req = urllib.request.Request(STATE["url"], data=json.dumps(payload).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json, text/event-stream")
    if STATE["token"]:
        req.add_header("Authorization", "Bearer " + STATE["token"])
    if STATE["session"]:
        req.add_header("Mcp-Session-Id", STATE["session"])
    with urllib.request.urlopen(req, timeout=900) as resp:
        STATE["session"] = resp.headers.get("Mcp-Session-Id") or STATE["session"]
        return _decode(resp.read().decode("utf-8", "replace"))


def rpc(method, params=None):
    STATE["id"] += 1
    msg = post({"jsonrpc": "2.0", "id": STATE["id"], "method": method, "params": params})
    if "error" in msg:
        raise RuntimeError(json.dumps(msg["error"]))
    return msg.get("result") or {}


def tool(name, arguments):
    result = rpc("tools/call", {"name": name, "arguments": arguments})
    if result.get("isError"):
        text = "\n".join(c.get("text", "") for c in result.get("content") or []).strip()
        raise RuntimeError(text or name + " failed")
    if isinstance(result.get("structuredContent"), dict):
        return result["structuredContent"]
    text = "\n".join(c.get("text", "") for c in result.get("content") or [] if c.get("type") == "text").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except ValueError:
        return {"text": text}


def defaults():
    try:
        with open(DEFAULTS, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def style_line(args, d):
    if args.style_hint:
        return args.style_hint.strip()
    s = d.get("style_defaults") or {}
    genre = " ".join(x for x in (args.genre or s.get("genre", "pop"), s.get("era", "")) if x)
    return ", ".join([
        args.language or s.get("language", "English"), genre,
        s.get("vocal", "female lead, clear"),
        s.get("instruments", "drums, bass, synth, guitar"),
        s.get("mood", "upbeat energetic"),
        s.get("production", "clean modern"),
        "%d BPM" % int(s.get("bpm", 120)),
    ])


def song_args(args, d):
    song = d.get("song_defaults") or {}
    out = dict(song)
    out["style"] = style_line(args, d)
    out["duration_seconds"] = float(args.duration or song.get("duration_seconds", 180))
    lyrics = args.lyrics_hint or d.get("lyrics")
    if lyrics:
        out["lyrics"] = lyrics
    if args.playlist:
        out["playlist_id"] = args.playlist
    if not args.no_cover:
        out["cover_prompt"] = d.get("cover_prompt") or "album cover, " + (args.idea or args.genre or "song")
    return out


def report(args, job, waited):
    song = (waited.get("songs") or job.get("songs") or [job])[0]
    song_id = song.get("song_id") or song.get("id") or job.get("song_id")
    path = song.get("path") or song.get("audio_path") or song.get("file")
    if song_id and not path:
        for value in tool("library_song_files", {"song_id": song_id}).values():
            if isinstance(value, str) and value.lower().endswith((".flac", ".mp3", ".wav")):
                path = value
                break
    seconds = song.get("duration_seconds") or song.get("duration")
    print("job_id:   %s" % (job.get("job_id") or job.get("id")))
    print("song_id:  %s" % song_id)
    if seconds:
        total = int(round(float(seconds)))
        print("duration: %d:%02d (%ds)" % (total // 60, total % 60, total))
    if path and args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        dest = os.path.join(args.output_dir, os.path.basename(path))
        shutil.copy2(path, dest)
        path = dest
    print("path:     %s" % (path or "-"))


def manager_prompt(args, d):
    lines = [
        "Use the manager agent to generate one song with YuE2 Studio.",
        "idea: " + (args.idea or "(none given)"),
        "style: " + style_line(args, d),
        "duration: %ds" % int(args.duration or 180),
    ]
    if args.lyrics_hint:
        lines.append("lyrics hint: " + args.lyrics_hint)
    if args.playlist:
        lines.append("playlist: " + args.playlist)
    lines.append("cover: " + ("no" if args.no_cover else "yes"))
    lines.append("Report job_id and song_id with the finished studio_wait result.")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="Generate a YuE2 song through YuE2 Studio's MCP endpoint.")
    p.add_argument("--idea", help="what the song is about")
    p.add_argument("--genre")
    p.add_argument("--duration", type=float, help="length in seconds (150-240)")
    p.add_argument("--language")
    p.add_argument("--style-hint", help="a whole YuE2 style sentence, used verbatim")
    p.add_argument("--lyrics-hint")
    p.add_argument("--output-dir", help="copy the finished audio here")
    p.add_argument("--playlist", help="playlist id the new song joins")
    p.add_argument("--no-cover", action="store_true", help="do not draw a cover")
    p.add_argument("--wait", type=float, default=55, help="seconds per studio_wait call")
    args = p.parse_args(argv)
    d = defaults()
    STATE["url"] = os.environ.get("YUE2_MCP_URL", "").strip() or DEFAULT_URL
    STATE["token"] = os.environ.get("YUE2_MCP_TOKEN", "").strip()
    try:
        rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                           "clientInfo": {"name": "yue2-generate", "version": "1.0"}})
        post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        job = tool("song_create", song_args(args, d))
        job_id = job.get("job_id") or job.get("id")
        if not job_id:
            raise RuntimeError("song_create returned no job_id: %r" % (job,))
        report(args, job, tool("studio_wait", {"job_id": job_id, "seconds": args.wait}))
        return 0
    except (RuntimeError, urllib.error.URLError, OSError, ValueError) as exc:
        print("MCP unavailable (%s). Hand this to the manager agent instead:" % exc, file=sys.stderr)
        print(manager_prompt(args, d))
        return 0


if __name__ == "__main__":
    sys.exit(main())
