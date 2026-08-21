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
- **Progress is stored in `localStorage`**, per kid, on the device/browser used.
  There is no backend, so progress does not sync across devices.

## Game rules

- One problem per day by default (change it under "grown-up settings" on the
  kid-select screen — gear icon at the bottom).
- Picking a number serves a random not-yet-attempted year for that number;
  once every year has been attempted, missed problems come back for retry.
  A number is disabled once all 41 of its problems are solved.
- Refreshing mid-problem resumes the same problem with the clock still running.
  Quitting/giving up counts as a wrong answer (5 consolation XP).
- XP: `20 + 4×number` for a correct answer, `+15` speed bonus under par
  (`30 + 6×number` seconds), `5` for a wrong answer or give-up.
- Pets evolve at levels 3, 6, 10, 15, and 21.

## Attribution

Problem content is © Mathematical Association of America, displayed live from
the Art of Problem Solving wiki. This is a personal, non-commercial practice
tool for two kids.
