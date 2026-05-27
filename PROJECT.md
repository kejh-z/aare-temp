# Aare Temperature Daily Email — Project Description

## Overview

A small automation that checks the daily peak water temperature of the river
Aare in Bern (the swimming spot served by **aaremarzili.ch**) and emails a
formatted daily report to a list of recipients every day at **18:00 Zurich
time**. 18:00 is chosen because it falls after the warmest part of the day, so
the reported peak reflects the true daily maximum.

The whole system runs in the cloud — no personal computer needs to be switched
on for the email to be sent.

---

## What the email contains

Each daily report includes:

- **Peak water temperature** reached that day, and the time it occurred
- **Current water temperature** at the moment the report is generated
- **Flow rate** of the river (m³/s)
- **Number of measurements** taken that day
- A friendly **swim verdict** based on the peak temperature:
  - `>= 20°C` → "Perfect for swimming!"
  - `>= 18°C` → "Warm enough for a swim."
  - `>= 16°C` → "A bit fresh, but doable."
  - `< 16°C` → "Too cold for most swimmers."

The email is sent as styled HTML (a blue temperature card, a stats table, and a
data-source footer).

**Recipients:**
- kevin@holden.ch
- jessica@holden.ch
- brigitte.lendl@bluewin.ch

**From address:** `aare@holden.ch` (sending from the verified `holden.ch` domain)

---

## Data source

- **Website:** https://aaremarzili.ch (redirects to aaremarzili.info)
- **Actual data API:** `https://aareguru.existenz.ch/v2018/current?app=aare-temp&version=1.0.0`

The aaremarzili site loads its data dynamically, so rather than scraping the
page we use the public **aare.guru API** (the same underlying data source for
Aare conditions in Bern). The API returns a JSON object containing:

- `aare.temperature` — current water temperature
- `aare.flow` — current flow rate
- `aarepast[]` — an array of ~48 hours of historical readings, each with a
  Unix `timestamp` and a `temperature` (10-minute intervals)

The app filters `aarepast[]` down to readings from the current day (Zurich
time), then finds the maximum temperature and the time it occurred.

---

## How it runs (architecture)

The scheduling and execution are split across three services:

```
  cron-job.org                GitHub Actions               Resend
  (scheduler)        →        (compute / runner)     →     (email delivery)
  fires at 18:00             fetches Aare data,            sends the HTML
  Zurich daily               builds the email              email to recipients
```

1. **cron-job.org** — a free external cron service. Every day at 18:00
   (timezone set to Europe/Zurich) it sends an authenticated **POST** request to
   the GitHub API to trigger the workflow:
   - URL: `https://api.github.com/repos/kejh-z/aare-temp/actions/workflows/daily-email.yml/dispatches`
   - Method: `POST`
   - Headers:
     - `Authorization: Bearer <GitHub personal access token>`
     - `Accept: application/vnd.github+json`
     - `Content-Type: application/json`
   - Body: `{"ref":"main"}`

2. **GitHub Actions** — runs the workflow defined in
   `.github/workflows/daily-email.yml`. The workflow runs an inline Node.js
   script on an `ubuntu-latest` runner that:
   - fetches the aare.guru API,
   - computes the day's peak temperature,
   - builds the HTML email,
   - sends it via the Resend REST API.
   The Resend API key is injected from a GitHub repository **secret** named
   `AARE_TEMP`.

3. **Resend** — the email delivery service (https://resend.com). The `holden.ch`
   domain is verified in Resend (via DNS records) so emails can be sent from
   `aare@holden.ch` to any recipient.

### Why this combination?

- **GitHub Actions' built-in cron was unreliable** — scheduled runs on inactive
  repos were delayed by hours or skipped entirely. So the `schedule:` trigger
  was removed and replaced with an external scheduler (cron-job.org) that
  triggers a `workflow_dispatch` event on time.
- **GitHub Actions** is used as free, always-on compute so no personal PC is
  needed.
- **Resend** handles deliverability and lets us send from a custom domain.

---

## Repository contents

The project lives at:
- **Local:** `C:\Users\kejh\claude\aare-temp`
- **Remote:** `https://github.com/kejh-z/aare-temp` (default branch: `main`)

| File | Purpose |
|------|---------|
| `.github/workflows/daily-email.yml` | **The live production code.** A self-contained GitHub Actions workflow with an inline Node.js script (no dependencies, no checkout). This is what actually runs each day. |
| `index.js` | A standalone Node.js version of the same logic, runnable locally. Uses the `resend` npm package and reads the API key from a `.env` file. Useful for local testing. Supports a `--dry-run` flag that prints the email without sending. |
| `package.json` | Declares the `resend` dependency and `npm start` / `npm test` scripts (for the local `index.js` version). |
| `.env.example` | Template showing the expected `RESEND_API_KEY` variable. |
| `.env` | (Not committed) Holds the real Resend API key for local runs. |
| `.gitignore` | Excludes `node_modules/` and `.env` from git. |
| `setup-task.bat` | Legacy helper that created a Windows Task Scheduler job (no longer used — replaced by the cloud setup). |
| `PROJECT.md` | This document. |

### Two copies of the logic — why?

- `.github/workflows/daily-email.yml` contains an **inline** copy of the logic.
  It was made self-contained (using Node's built-in `fetch` and the Resend REST
  API directly) because the GitHub organisation restricts the use of external
  Actions like `actions/checkout`, and a private repo couldn't be `git clone`d
  without auth. Inlining the code sidesteps both problems.
- `index.js` is the original, cleaner version kept for local testing. The two
  are functionally equivalent; if you change the recipients or email design,
  update **both** (the workflow is the one that runs in production).

---

## Key processes & how to make changes

### Change the recipients
Edit the `RECIPIENTS` array in **both** `.github/workflows/daily-email.yml`
(line ~16) and `index.js` (line ~7), then commit and push.

### Change the send time
Adjust the schedule in **cron-job.org** (not in the repo). Make sure the
timezone stays Europe/Zurich.

### Test it manually
- **From GitHub:** Actions tab → "Daily Aare Temperature Email" → "Run workflow".
- **From cron-job.org:** use the "Test run" button on the cron job.
- **Locally:** `npm test` (dry run, no email) or `npm start` (sends a real
  email) — requires a valid `.env` file.

### Rotate the API key
1. Create a new key in Resend.
2. Update the `AARE_TEMP` secret at
   `github.com/kejh-z/aare-temp/settings/secrets/actions`.

---

## Git usage

- Git was initialised locally and the repo is pushed to GitHub
  (`github.com/kejh-z/aare-temp`).
- The default branch was renamed from `master` to `main` (GitHub expects `main`,
  and the Actions UI was not surfacing the workflow under `master`).
- Each change (adding recipients, switching domains, fixing the workflow) was
  made as a small, separate commit with a descriptive message.
- Secrets are never committed — `.env` is git-ignored, and the production key
  lives only as a GitHub Actions secret.

---

## Accounts & credentials involved

| Service | Purpose | Notes |
|---------|---------|-------|
| **GitHub** (`kejh-z`) | Hosts the repo and runs the workflow | Repo: `aare-temp` |
| **Resend** | Sends the emails | `holden.ch` domain verified; API key stored as the `AARE_TEMP` GitHub secret |
| **cron-job.org** | Triggers the workflow daily at 18:00 | Uses a GitHub personal access token (classic, `repo` scope) in the Authorization header |

---

## Known considerations / gotchas

- **cron-job.org header formatting matters** — the `Authorization` value must be
  exactly `Bearer <token>` with no missing/extra characters. A truncated token
  caused a 401 during setup.
- **GitHub cron is unreliable** — intentionally not used; the duplicate email
  seen once at ~22:16 was a late-firing GitHub cron run before its `schedule:`
  trigger was removed.
- **Resend free tier** originally only allowed sending to the account owner's
  own address until the `holden.ch` domain was verified. Now any recipient
  works.
- If emails land in **spam**, sending separate emails per recipient (instead of
  one with all three in the `to` field) can improve deliverability — not
  currently done, but easy to switch on.
