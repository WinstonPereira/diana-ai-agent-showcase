# Demo media (recording guide)

Drop your demo assets in this folder. The main README already links to them:

| File | Required | What it is |
|------|----------|------------|
| `diana-demo.gif` | recommended | 10-15 s looping clip: orb reacting + one real action. Keep under 8 MB. |
| `diana-demo.mp4` | optional | Full 60-90 s walkthrough, 720p or 1080p. |
| `demo-thumb.png` | optional | Thumbnail for the video link (1280x720). |

## Recording checklist (60-90 s total)

1. **Voice in, orb out (10 s)** - ask something simple. Show the orb changing color and motion before the spoken answer starts.
2. **Real OS action (15 s)** - "open Chrome and search for the weather". Show the window actually opening.
3. **Honesty (15 s)** - ask for a measurement the agent cannot perform. It must refuse and offer to install the skill. This is the most underrated differentiator.
4. **Safe self-modification (20 s)** - request a small code change, then show a deliberately broken edit being rejected and auto-reverted.
5. **Security layer (15 s)** - trigger a protection scan and show the alert plus the false-positive filter.
6. **Long task (optional, 15 s)** - start a multi-step plan and show the step-by-step progress log.

## Tips

- Record at 1080p and crop to the app window. No desktop clutter, no personal file names.
- Move the mouse slowly and deliberately - the viewer must follow what the agent is doing.
- If the GIF exceeds 8 MB, shrink it: `ffmpeg -i in.mp4 -vf "fps=12,scale=820:-1" out.gif`.
- Never include API keys, tokens, real user paths, or third-party personal data.
