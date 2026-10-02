# Faith Clips Finder

Every morning this finds the best **new** short Christian clips on YouTube and delivers them ready to use:

- **6:00 AM Pacific**: it searches, filters, and adds the top 10 clips to your Google Sheet.
- **7:00 AM Pacific**: it emails you the top 5, with a clickable timestamped link, the quote and the best hook, so you can pick one from your phone in under a minute.

It runs on GitHub by itself. After the one-time setup below, you never have to touch it.

---

## What it does each day

1. **Looks on YouTube** (official API) for anything posted in the last 72 hours:
   - new uploads from your approved channels (the Channels tab in your Sheet)
   - 16 faith searches (sermons, athletes giving glory to God, testimonies) to discover new channels
   - stories from Sports Spectrum, CBN News, Christian Post and ChurchLeaders, then the original video
2. **Throws out** anything political, divisive, vulgar, about a pastor controversy, any "send money" pitch, any repost, compilation or "God's message for you" channel, and anything it has already seen.
3. **Claude reviews the top 20** (latest model, Claude Opus 5.5):
   - **Long sermons:** it reads the transcript and picks the best 20–45 seconds.
   - **Shorts:** they're used whole.
   - **For every clip:** it writes 3 hooks, a caption, the piece pairing, how to use it, and a permission message.
4. **Checks every quote in code.** The quote must appear word for word in the real transcript, or the clip is thrown out. Quoted words in hooks get the same check. Nothing is paraphrased or invented.
5. **Ranks** by emotional punch (35%), stands alone in 30 seconds (30%), the channel's reach (20%) and how recent it is (15%). Keeps the top 10.

**Links and timestamps only.** It never downloads, rips or re-uploads anyone's video.

## What it costs

| Thing | Cost |
|---|---|
| YouTube API, Google Sheets, Gmail, GitHub | **Free.** It uses about 2,500 of YouTube's 10,000 free daily units. |
| Claude (Anthropic API) | **About $30–45 a month.** The Log tab shows each day's estimate. |

You can halve the Claude cost by switching to the cheaper model (see "Changing settings").

---

## One-time setup (about 40 minutes, on a computer)

You'll create 5 things and paste them into GitHub. Do the steps in order. Keep a notes file open to paste things into as you go.

### Step 1: YouTube key (Google Cloud)

1. Go to **console.cloud.google.com** and sign in with walliebusiness1@gmail.com. Accept the terms if asked. It's free, and no credit card is needed for this.
2. Create a project:
   1. At the top, click the **project picker** (it may say "Select a project").
   2. Click **New Project**.
   3. Name it `gospelscribe-clips` and click **Create**.
   4. Make sure that project is selected at the top.
3. Turn on the YouTube API:
   1. In the search bar at the top, type **YouTube Data API v3**, open it and click **Enable**.
4. Turn on the Sheets API:
   1. Search **Google Sheets API**, open it and click **Enable**.
5. Create the YouTube key:
   1. Go to the left menu → **APIs & Services** → **Credentials**.
   2. Click **+ Create credentials** → **API key**.
   3. Copy the key. Save it as **YOUTUBE_API_KEY**.
   4. Click **Edit API key** (or the key's name).
   5. Under **API restrictions**, choose **Restrict key**, tick **YouTube Data API v3**, then click **Save**.

### Step 2: The Google Sheet and its "robot" helper

The finder writes to your Sheet through a robot account that you create and share the Sheet with.

1. Create the robot, still in Google Cloud:
   1. Go to **APIs & Services** → **Credentials** → **+ Create credentials** → **Service account**.
   2. Name it `clips-robot`, then click **Create and continue** → **Done**. Skip the roles.
2. Download the robot's key:
   1. Click the new `clips-robot@…iam.gserviceaccount.com` account in the list.
   2. Go to the **Keys** tab → **Add key** → **Create new key** → **JSON** → **Create**.
   3. A file downloads.
3. Save the key text:
   1. Open the downloaded file with Notepad (Windows) or TextEdit (Mac).
   2. Select everything and copy it. Save it as **GOOGLE_SERVICE_ACCOUNT_JSON**.
   3. Copy the `client_email` address from inside the file too. It looks like `clips-robot@gospelscribe-clips.iam.gserviceaccount.com`.
4. Make the Sheet:
   1. Go to **sheets.new** and name the Sheet **Faith Clips**.
   2. Click **Share**, paste the robot's `client_email`, set it to **Editor**, untick "Notify", and click **Share**.
   3. Copy the Sheet's link from the address bar. Save it as **SHEET_ID**. The whole link is fine.

Leave the Sheet empty. The finder creates its own tabs: Clips, Channels, Seen and Log.

### Step 3: Gmail app password (so it can email you)

Google requires a special password for this. Your normal password won't work.

1. Go to **myaccount.google.com** → **Security**, and make sure **2-Step Verification** is **On**. Turn it on if it isn't.
2. Go to **myaccount.google.com/apppasswords**.
3. Type the name `Faith Clips`, then click **Create**.
4. Copy the 16-letter password. Save it as **GMAIL_APP_PASSWORD**.
5. Your Gmail address (walliebusiness1@gmail.com) is **GMAIL_ADDRESS**.

### Step 4: Claude key (Anthropic)

1. Go to **platform.claude.com** (formerly console.anthropic.com) and sign up or sign in.
2. Add credit:
   1. Go to **Settings** → **Billing** and add **$20** of credit to start.
   2. Optional but smart: under **Limits**, set a monthly spend limit of about **$60**, so a surprise can't run up a bill.
3. Create the key:
   1. Go to **API Keys** → **Create Key**, and name it `faith-clips`.
   2. Copy it (it starts with `sk-ant-`). Save it as **ANTHROPIC_API_KEY**.

### Step 5: Put the keys in GitHub

1. Go to **github.com/Wallie1001/Gospelscribe-Store-1st**.
2. Click **Settings** (top right of the repo) → **Secrets and variables** → **Actions**.
3. For each of the 6 below, click **New repository secret**, type the **Name** exactly as shown, paste the value, and click **Add secret**:

| Name | Value |
|---|---|
| `YOUTUBE_API_KEY` | from Step 1 |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | the whole JSON file text from Step 2 |
| `SHEET_ID` | the Sheet link from Step 2 |
| `GMAIL_ADDRESS` | walliebusiness1@gmail.com |
| `GMAIL_APP_PASSWORD` | the 16-letter password from Step 3 |
| `ANTHROPIC_API_KEY` | from Step 4 |

Optional: add `EMAIL_TO` if you want the email to go to a different address.

Secrets stay hidden even though this repo is public. Nobody can read them, including you after saving. You can only replace them.

### Step 6: Check your setup

1. In the repo, click the **Actions** tab. If GitHub asks, click **"I understand my workflows, go ahead and enable them."**
2. On the left, click **Faith Clips - Check My Setup**.
3. Click **Run workflow** → **Run workflow** (green button).
4. Wait about a minute, then click the run and open **check** → **Check every key**. You'll see a ✅ or ❌ for each key, and every ❌ tells you exactly what to fix.
5. When it works:
   - You'll get a **"setup test ✅"** email.
   - Your Sheet will have its tabs, and the **Channels** tab will list your 35 approved channels.

### Step 7 (optional): See clips right now

1. Go to **Actions** → **Faith Clips - Daily Search** → **Run workflow** → **Run workflow**.
2. In about 5–15 minutes, the clips land in your Sheet and you get an email.

After this you're done. It runs every morning by itself.

---

## Using it every day

1. Open the **7 AM email** on your phone.
2. Tap **Watch at 1:23** on the one you like. It opens YouTube at the exact second.
3. Open the Sheet's **Clips** tab to grab that clip's caption, the other hooks and the permission message. Newest clips are at the top.
4. Change **Status** from `New` to whatever helps you, like `Using`, `Asked permission`, `Posted` or `Skip`.

**Before you post:**
- **Listen once.** Auto-captions can mishear a word. The Notes column flags clips that use auto-captions or have no captions at all.
- **Credit the speaker** on screen and in the caption. The caption is already written that way.
- **Get permission first** unless you're stitching or duetting their own TikTok or Instagram post. The permission message is ready to copy.

## Your channel list (Channels tab)

| Approved says | Meaning |
|---|---|
| `Yes` | On your list. Checked every day. |
| `New` | Found automatically. Its clips still show up, marked **NEW CHANNEL** in the Notes column. Change it to `Yes` to keep it, or `No` to block it. |
| `No` | Blocked. Never used. |

- **To add a channel:** add a row with the **Name** and **Handle** (like `@elevationchurch`), and put `Yes` in Approved. The next run looks it up and fills in the rest.
- **If the YouTube Title column says "NOT FOUND":** fix the Handle. You can find a channel's @handle under its name on YouTube.

The YouTube Title column shows what each row matched on YouTube, so you can spot a wrong match.

## Changing settings

Everything is in **`faith-clips/faithclips/config.py`**. To change something:

1. On GitHub, open the file.
2. Click the ✏️ pencil icon, make the change, and click **Commit changes**.

Things you might change:
- **Cheaper Claude:** change `CLAUDE_MODEL = "claude-opus-5-5"` to `"claude-sonnet-5-5"`. That's roughly half the cost.
- **More or fewer clips:** `CLIPS_PER_DAY`, `EMAIL_TOP`, and `MAX_CLAUDE_CALLS` (the cost cap).
- **Search phrases:** `DISCOVERY_SEARCHES`.
- **How established a new channel must be:** `DISCOVERED_MIN_SUBSCRIBERS`.

If you'd rather not edit code, ask Claude Code to make the change.

---

## If something breaks

**You'll be told.** If a run fails, you get an email titled **"Faith Clips Finder: something needs a look"** with a link to the run. GitHub also emails you about failed runs. The **Log** tab has one row per run, and its Notes column says what happened.

| What you see | What to do |
|---|---|
| No email at 7 AM | GitHub sometimes starts scheduled jobs 10–30 minutes late. If there's still nothing by 9:30, open **Actions** and look for a red ❌. Also check your Gmail spam folder. |
| Log says **"YouTube blocked transcript requests"** | YouTube sometimes blocks transcript requests from GitHub's servers. Shorts still come through, but long sermons get skipped. If it happens most days, see "Fix for blocked transcripts" below. |
| Log says **"quota ran out"** | You've hit YouTube's free daily limit, and it resets at midnight Pacific. Fewer `DISCOVERY_SEARCHES` will fix it for good. |
| Problem email mentions **credit**, **401** or **authentication** | Your Claude credit ran out or the key is wrong. Add credit at platform.claude.com, or replace the `ANTHROPIC_API_KEY` secret. |
| Problem email mentions **SpreadsheetNotFound** or **403** | The Sheet isn't shared with the robot's email as Editor (Step 2), or `SHEET_ID` is wrong. |
| Problem email mentions **Username and Password not accepted** | The Gmail app password is wrong or was revoked. Make a new one (Step 3) and replace `GMAIL_APP_PASSWORD`. |
| Log says a **feed failed** | That news site changed its feed address. The other sources keep working. Ask Claude Code to update `FEEDS` in config.py. |
| Run **Faith Clips - Check My Setup** anytime | It re-tests every key and tells you what's wrong. |

### Fix for blocked transcripts (optional, about $3–4 a month)

1. Sign up at **webshare.io**.
2. Buy the cheapest **Residential** proxy plan. Don't buy "Proxy Server" or "Static Residential".
3. In Webshare, go to **Proxy Settings** and copy the **Proxy Username** and **Proxy Password**.
4. Add them to GitHub Secrets (Step 5) as `WEBSHARE_PROXY_USERNAME` and `WEBSHARE_PROXY_PASSWORD`.

The next run uses them automatically.

---

## How it stays honest

- **Official sources only.** Your approved channels, plus discovered channels that pass every check:
  - over 20,000 subscribers
  - over a year old
  - an established video history
  - no repost or "clips" or "God's message" style names
  - no "no copyright intended" style descriptions
- **Quotes are checked by code**, not just by Claude. A quote that isn't word for word in the transcript means the clip is thrown out. Quoted words in hooks get the same check.
- **No endorsement claims.** Hooks never mention Gospelscribe or suggest the speaker wears or endorses it. The permission message says so plainly.
- **Christian content only, centered on Jesus.** Politics, culture war, scandal, prosperity pitches, AI or lip-synced content and edited quotes are all filtered out.
- **No repeats.** Every video it has judged goes in the Seen tab, and it is never reviewed again.

## Behind the scenes (for whoever helps you later)

- **Code:** `faith-clips/faithclips/`
- **Tests:** `faith-clips/tests/`. They run on every change through the "Faith Clips - Tests" workflow.
- **Workflows:** `.github/workflows/faith-clips-*.yml`
- **Scheduling:**
  - GitHub's clock is UTC with no daylight saving, so each job is scheduled twice, and the code only acts at the right Pacific time, once per day.
  - The daily job also re-enables both schedules, because GitHub pauses scheduled jobs in repos with no commits for 60 days.
- **Transcripts:** fetched with `youtube-transcript-api` (caption text only). Everything else uses the official YouTube Data API v3.
- **Claude:** `claude-opus-5-5` with structured JSON output and server-side refusal fallback (`fallbacks: "default"`). The quote checks are in `faithclips/claude.py` (`validate`).
