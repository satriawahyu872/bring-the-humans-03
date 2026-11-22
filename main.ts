// bring-the-humans-03 v1 — "THE MONEY LOOP" (Node 22, standard library only).
//
// The entry is the video itself: an 18 s vertical TikTok ad for make.fun, made by
// this agent (see render-ad.py for how it was built) and posted publicly on TikTok
// from a public account. This program only copies VIDEO.json from the repository
// root to /output/VIDEO.json, where the gate reads the video's TikTok address.
//
// The ad shows make.fun's brand badge from its first frame and ends on make.fun's
// referral end card with the entrant's own referral code typed in, both from
// make.fun's press pack and used as they are:
//   https://make.fun/press/manifest.json
//   https://make.fun/press/llms.txt
//
// VIDEO.json holds a placeholder until the video is posted; the real TikTok URL
// goes in before submitting.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR stand
// in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });

// Read VIDEO.json first so a malformed file fails here, loudly, instead of
// silently copying a broken address to the output.
const videoPath = join(BOT_DIR, 'VIDEO.json');
let video: unknown;
try {
  video = JSON.parse(readFileSync(videoPath, 'utf8'));
} catch (err) {
  console.error(`VIDEO.json could not be read from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
if (!video || typeof video !== 'object' || typeof (video as { url?: unknown }).url !== 'string') {
  console.error('VIDEO.json must hold an object with a string "url" field.');
  process.exit(1);
}

try {
  copyFileSync(videoPath, join(OUTPUT_DIR, 'VIDEO.json'));
} catch (err) {
  console.error(`VIDEO.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
