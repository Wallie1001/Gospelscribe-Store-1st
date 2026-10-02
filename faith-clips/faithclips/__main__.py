"""Commands (GitHub Actions runs these for you):

  python -m faithclips run     find clips (6 AM job, or the "Run now" button)
  python -m faithclips email   send the morning email (7 AM job)
  python -m faithclips check   test every key and set up the Sheet
"""
import logging
import os
import sys
import traceback
from dataclasses import dataclass

from . import config, emailer, finder
from .util import at_or_after, now_pacific, today_pacific

log = logging.getLogger("faithclips")


@dataclass
class Settings:
    youtube_api_key: str
    anthropic_api_key: str
    google_service_account_json: str
    sheet_id: str
    gmail_address: str
    gmail_app_password: str
    email_to: str
    transcript_proxy_url: str
    webshare_user: str
    webshare_pass: str

    @classmethod
    def from_env(cls) -> "Settings":
        e = lambda k: os.environ.get(k, "").strip()
        gmail = e("GMAIL_ADDRESS")
        return cls(
            youtube_api_key=e("YOUTUBE_API_KEY"),
            anthropic_api_key=e("ANTHROPIC_API_KEY"),
            google_service_account_json=e("GOOGLE_SERVICE_ACCOUNT_JSON"),
            sheet_id=sheet_id_from(e("SHEET_ID")),
            gmail_address=gmail,
            gmail_app_password=e("GMAIL_APP_PASSWORD"),
            email_to=e("EMAIL_TO") or gmail,
            transcript_proxy_url=e("TRANSCRIPT_PROXY_URL"),
            webshare_user=e("WEBSHARE_PROXY_USERNAME"),
            webshare_pass=e("WEBSHARE_PROXY_PASSWORD"),
        )

    def missing(self) -> list[str]:
        required = {
            "YOUTUBE_API_KEY": self.youtube_api_key,
            "ANTHROPIC_API_KEY": self.anthropic_api_key,
            "GOOGLE_SERVICE_ACCOUNT_JSON": self.google_service_account_json,
            "SHEET_ID": self.sheet_id,
            "GMAIL_ADDRESS": self.gmail_address,
            "GMAIL_APP_PASSWORD": self.gmail_app_password,
        }
        return [k for k, v in required.items() if not v]


def sheet_id_from(value: str) -> str:
    """Accept either the ID or the whole Sheet link."""
    if "/d/" in value:
        return value.split("/d/")[1].split("/")[0]
    return value


def run_url() -> str:
    server, repo, run_id = (os.environ.get(k, "") for k in ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID"))
    return f"{server}/{repo}/actions/runs/{run_id}" if repo else "https://github.com"


def scheduled() -> bool:
    return os.environ.get("GITHUB_EVENT_NAME") == "schedule"


def send(s: Settings, parts: tuple[str, str, str]):
    subject, html_body, text_body = parts
    emailer.send(s.gmail_address, s.gmail_app_password, s.email_to, subject, html_body, text_body)
    log.info("email sent to %s: %s", s.email_to, subject)


def top_clips(rows: list[dict]) -> list[dict]:
    def score(r):
        try:
            return float(r.get("Score") or 0)
        except ValueError:
            return 0.0
    return sorted(rows, key=score, reverse=True)[: config.EMAIL_TOP]


def already(sheet, run_type: str) -> bool:
    return any(r.get("Run Type") == run_type for r in sheet.runs_on(today_pacific()))


def send_daily_email(s: Settings, sheet, rows: list[dict], run_type: str = "email"):
    date = today_pacific()
    send(s, emailer.daily_email(top_clips(rows), date, sheet.url))
    sheet.log_run([date, now_pacific().strftime("%H:%M"), run_type, "", "", "", "", "",
                   f"emailed {min(len(rows), config.EMAIL_TOP)} clips to {s.email_to}"])


def report_problem(s: Settings, what: str):
    detail = traceback.format_exc()
    log.error("%s\n%s", what, detail)
    if s.gmail_address and s.gmail_app_password:
        try:
            send(s, emailer.problem_email(what, detail, run_url()))
        except Exception:
            log.exception("could not send the problem email either")


def cmd_run(s: Settings) -> int:
    from .sheet import Sheet
    now = now_pacific()
    if scheduled():
        if not at_or_after(now, config.FINDER_EARLIEST):
            log.info("It's %s Pacific, before the 6 AM run time (daylight-saving double schedule). Skipping.", now.strftime("%H:%M"))
            return 0
        sheet = Sheet(s.google_service_account_json, s.sheet_id)
        sheet.setup()
        if already(sheet, "daily"):
            log.info("Today's daily run already happened. Skipping.")
            return 0
    try:
        result = finder.run(s, "daily" if scheduled() else "manual")
    except Exception:
        report_problem(s, "The daily clip search stopped with an error.")
        return 1

    sheet = Sheet(s.google_service_account_json, s.sheet_id)
    if scheduled():
        # Finished after 7 AM (GitHub can start late)? Send the email now.
        if at_or_after(now_pacific(), config.EMAIL_AT) and not already(sheet, "email"):
            send_daily_email(s, sheet, sheet.clips_for_date(result.date))
    elif os.environ.get("SEND_EMAIL", "yes").lower() in ("yes", "true", "1"):
        send(s, emailer.daily_email(top_clips(result.clips), result.date, sheet.url))
    return 0


def cmd_email(s: Settings) -> int:
    from .sheet import Sheet
    now = now_pacific()
    sheet = Sheet(s.google_service_account_json, s.sheet_id)
    sheet.setup()
    if scheduled():
        if not at_or_after(now, config.EMAIL_EARLIEST):
            log.info("It's %s Pacific, too early for the 7 AM email. Skipping.", now.strftime("%H:%M"))
            return 0
        if already(sheet, "email"):
            log.info("Today's email already went out. Skipping.")
            return 0
        if not already(sheet, "daily") and not at_or_after(now, config.EMAIL_WAIT_UNTIL):
            log.info("Today's search hasn't finished yet; it will send the email itself when done.")
            return 0
    try:
        send_daily_email(s, sheet, sheet.clips_for_date(today_pacific()))
    except Exception:
        report_problem(s, "The morning email could not be sent.")
        return 1
    return 0


def cmd_check(s: Settings) -> int:
    """Test every key, one at a time, and say exactly what's wrong in plain words."""
    ok = True

    def line(passed: bool, label: str, fix: str = ""):
        nonlocal ok
        ok = ok and passed
        print(("✅ " if passed else "❌ ") + label + ("" if passed else f"\n   → {fix}"))

    missing = s.missing()
    line(not missing, "All required secrets are filled in",
         "Missing: " + ", ".join(missing) + ". Add them in GitHub → Settings → Secrets and variables → Actions.")

    # YouTube
    yt = None
    try:
        from .youtube import YouTube
        yt = YouTube(s.youtube_api_key)
        found = yt.channel_by_handle("@lifechurch")
        line(found is not None, "YouTube key works", "The key worked but a test lookup came back empty. Try again later.")
    except Exception as e:
        line(False, "YouTube key works", f"{e}. Check README step 1 (enable YouTube Data API v3, copy the key).")

    # Google Sheet
    sheet = None
    try:
        from .sheet import Sheet
        sheet = Sheet(s.google_service_account_json, s.sheet_id)
        created = sheet.setup()
        line(True, "Google Sheet opens" + (f" (created tabs: {', '.join(created)})" if created else ""))
    except Exception as e:
        email = ""
        try:
            import json
            email = json.loads(s.google_service_account_json).get("client_email", "")
        except Exception:
            pass
        line(False, "Google Sheet opens",
             f"{type(e).__name__}: {e}. Share the Sheet with {email or 'the service account email'} as Editor "
             "(README step 2), and check SHEET_ID.")

    # Channels (first run: fills the Channels tab)
    if sheet is not None and yt is not None and not missing:
        try:
            from .util import today_pacific as tp
            notes: list[str] = []
            rows = finder.sync_channels(sheet, yt, tp(), notes)
            matched = sum(1 for r in rows if r.get("Channel ID"))
            line(True, f"Channels tab ready: {matched} of {len(rows)} channels matched on YouTube")
            for n in notes:
                print("   ⚠️  " + n)
        except Exception as e:
            line(False, "Channels tab ready", str(e))

    # Claude
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=s.anthropic_api_key)
        r = client.messages.create(
            model=config.CLAUDE_MODEL, max_tokens=2000, output_config={"effort": "low"},
            messages=[{"role": "user", "content": "Reply with the single word: ready"}],
        )
        line(r.stop_reason in ("end_turn", "stop_sequence"), f"Claude key works ({config.CLAUDE_MODEL})")
    except Exception as e:
        line(False, "Claude key works",
             f"{type(e).__name__}: {e}. Check ANTHROPIC_API_KEY and that your Anthropic account has credit (README step 4).")

    # Email
    try:
        send(s, ("Faith Clips Finder: setup test ✅",
                 "<p>Your Faith Clips Finder can email you. Clips start arriving tomorrow at 7 AM Pacific.</p>",
                 "Your Faith Clips Finder can email you. Clips start arriving tomorrow at 7 AM Pacific."))
        line(True, f"Test email sent to {s.email_to}")
    except Exception as e:
        line(False, "Email works",
             f"{type(e).__name__}: {e}. Use a Gmail App Password, not your normal password (README step 3).")

    print("\nAll set! 🎉" if ok else "\nFix the ❌ items above, then run 'Check my setup' again.")
    return 0 if ok else 1


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    s = Settings.from_env()
    if cmd != "check" and s.missing():
        print("Missing secrets: " + ", ".join(s.missing()) + ". Run 'Check my setup' for help.")
        return 1
    return {"run": cmd_run, "email": cmd_email, "check": cmd_check}[cmd](s)


if __name__ == "__main__":
    sys.exit(main())
