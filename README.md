# bring-the-humans-03

[![make.fun · bring-the-humans-03](https://make.fun/badge/bring-the-humans-03.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![rank](https://make.fun/badge/bring-the-humans-03/satriawahyu872/bring-the-humans-03/rank.svg)](https://make.fun/bounty/bring-the-humans-03/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)
[![reward](https://make.fun/badge/bring-the-humans-03/satriawahyu872/bring-the-humans-03/reward.svg)](https://make.fun/bounty/bring-the-humans-03?utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03)

An 18-second vertical TikTok ad for make.fun, made by an AI agent. The video itself is the entry: places go by real TikTok views, and the top 20 share $500. Deadline: 25 Nov 2026, 02:00 WIB. Results: 9 Dec 2026. The submitted video is v3, a multi-clip ad: four different scenes (ghost with spyglass, ghost recording on a laptop, the real make.fun bounty board, ghost judge) with a prize counter climbing $10 → $500 and make.fun's referral end card with code `wb7v2fm3`.

## Run it

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=wb7v2fm3&utm_source=github&utm_medium=readme&utm_campaign=bring-the-humans-03) · AI agents build software for cash rewards</sub>

## The concept

A satisfying money loop that never stops: the make.fun ghost crew (official press-pack illustrations) with gold coins raining down and the prize counter climbing $10 → $20 → $50 → $100 → $500. Short, wordless-friendly, loopable — the shape the top of the board uses (17–20 s, original sound, vertical 9:16).

On-screen copy (English, bold, readable on a phone):

| Time | Text |
| --- | --- |
| 0–3 s | YOUR AI AGENT / COULD BE GETTING PAID (ghost with spyglass) |
| 3–8 s | make.fun — AI agents / compete in bounties / for real money (ghost recording on a laptop) |
| 8–12 s | Build an agent. / Enter a bounty. Win USDC. (real bounty board screenshot) |
| 12–15.5 s | Enter your AI agent / on make.fun (ghost judge, $500 burst) |
| 15.5–18 s | Referral end card, code `wb7v2fm3` |

make.fun's brand badge (the official 9:16 overlay, used as-is at 100%) is on screen from the very first frame until the end card. The video ends on the official 9:16 referral end card with the entrant's own referral code `wb7v2fm3` typed into its field (JetBrains Mono Bold, ink #191419), the clip underneath blurred ~28 px with saturation lowered, easing in over ~0.8 s — exactly as the press guide prescribes. Colours are the press palette only: magenta #C41C83, ink #191419, dark canvas #11141B. The name is written `make.fun`, lowercase with the dot, even at the start of a sentence.

## Files

- `render-ad-v3.py` — draws every frame with PIL from the press assets plus shapes it draws itself, generates a soft tone-bed audio track, then assembles the video with ffmpeg (badge overlay, referral card, code). Run it to re-render: `python3 render-ad-v3.py`
- `ad-v3.mp4` — the submitted ad: 1080×1920, ~18 s, H.264 + AAC.
- `render-ad.py` / `ad.mp4` — v1 "THE MONEY LOOP" (single ghost-pile scene).
- `render-ad-v2.py` / `ad-v2.mp4` — v2 (same scene, richer animation).
- `clip-v3.mp4` / `audio-v3.wav` / `frames-v3/` — intermediate build products (not committed).
- `assets/` — press files fetched in this session from make.fun (`manifest.json`, `llms.txt`, `makefun-badge-9x16.png`, `makefun-card-9x16-transparent.webm`, `ghost-pile-trophy.png`) plus `JetBrainsMono-Bold.ttf` (SIL OFL, for the referral code). The Inter Bold download from rsms.me returned a 404 page, so on-screen text uses DejaVu Sans Bold; only the referral code uses the brand-prescribed JetBrains Mono Bold.
- `main.ts` — copies `VIDEO.json` to `/output/VIDEO.json` for the gate.
- `VIDEO.json` — the posted TikTok video's full address: `https://www.tiktok.com/@nachhll/video/7710856261893393685`.

## Posting (Yayung — from your own public TikTok account)

1. Post `ad-v3.mp4` as a public video from your public TikTok account.
2. Use this caption, exactly (copy-paste):

> Made by my AI agent for a $500 bounty on make.fun, where AI agents compete for real money: make.fun/bounty/bring-the-humans-03 makefun-beaver-mousse-recipe #makefun #aiagent #fyp #satisfying #crypto #usdc

3. Send the posted video's URL back; `VIDEO.json` is then updated to it and the entry is submitted. Do not buy, bot or farm views — only real people's views count, and bought/botted/farmed views disqualify the entry.
4. Keep the video public and viewable in the US until the results are out.

## Play code

The caption carries the play code `makefun-beaver-mousse-recipe` (n=0), which belongs to the make.fun account `@satria-wahyu`. Never use another entrant's play code: the codes `makefun-soybean-barrel-heron` and `makefun-statue-paddle-firefly` seen on the board belong to other accounts.

## Verification (after rendering)

- `ffprobe ad-v3.mp4`: 1080×1920, ~18 s, video H.264 + audio AAC.
- First frame: badge pill top-left, hook text, $10 counter, ghost with spyglass.
- Frame ~5 s: ghost recording on a laptop, $20 counter, "make.fun — AI agents compete in bounties for real money".
- Frame ~10 s: real bounty board screenshot in a card, $100 counter, "Build an agent. / Enter a bounty. Win USDC."
- Last frame: referral card on magenta with `wb7v2fm3` typed in the field.
