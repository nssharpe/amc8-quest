# AMC 8 Quest

A daily AMC 8 practice game for kids, served at **https://nssharpe.github.io/amc8-quest/**.

Two player profiles (Zyler and Kadyn) each get a daily mission: pick a problem
number (1–25, or random) and solve one real AMC 8 / AJHSME problem against a
timer. Solving earns XP, levels, an evolving pet, and trophies.

## How it works

- **Single self-contained `index.html`** — no build step, no dependencies.
- **Problems are fetched live** from the [AoPS Wiki](https://artofproblemsolving.com/wiki/)
  MediaWiki API at the moment a kid starts a problem. No problem text is stored
  in this repo (problems are © MAA); only the answer letters (facts) are embedded.
- **Coverage**: all 41 contests — 1985–1998 AJHSME and 1999–2026 AMC 8
  (2021 was canceled) — 1,025 problems total.
- **Progress syncs across devices** through a tiny serverless backend on the
  owner's Google account: every game event (answer, pet choice, reset, settings
  change) is POSTed to a Google Form, which appends it to a link-readable
  response Sheet; the app reads the full event log back via the Sheets gviz
  JSONP endpoint and folds it into per-kid state (XP is recomputed from the
  formula, never trusted from storage). `localStorage` acts as an offline
  cache + outbox, so the app still works without internet and syncs later.
  Unknown/malformed rows in the sheet are ignored, and duplicate rows are
  deduped by event id.
- **Grown-up settings are password-protected** (SHA-256 hash in source; the
  gate keeps kids out, it is not high security). Settings: problems per day
  (synced), and per-kid full resets (synced, so they apply on every device).

## Game rules

- The daily goal is one problem by default (change it under "grown-up
  settings"), but problems are never capped — once the goal is hit, extras
  are framed as bonus rounds.
- Some individual problem wiki pages omit the answer choices; the app detects
  this and falls back to extracting the problem from the year's combined
  problems page, which includes them.
- Picking a number serves a random not-yet-attempted year for that number;
  once every year has been attempted, missed problems come back for retry.
  A number is disabled once all 41 of its problems are solved.
- An in-progress problem is per-device: refreshing resumes it with the clock
  still running.
  Quitting/giving up counts as a wrong answer (5 consolation XP).
- XP: `20 + 4×number` for a correct answer, `+15` speed bonus under par
  (`30 + 6×number` seconds), `5` for a wrong answer or give-up.
- Pets evolve at levels 3, 6, 10, 15, and 21.

## Attribution

Problem content is © Mathematical Association of America, displayed live from
the Art of Problem Solving wiki. This is a personal, non-commercial practice
tool for two kids.
