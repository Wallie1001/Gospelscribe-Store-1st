"""Morning email through Gmail (app password)."""
import html
import smtplib
import ssl
from email.message import EmailMessage

GOLD = "#C9A24D"
INK = "#15110E"
PARCHMENT = "#E8DCC4"
BRONZE = "#6B5A48"
CRIMSON = "#8E1F1F"


def send(gmail_address: str, app_password: str, to: str, subject: str, html_body: str, text_body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"Faith Clips Finder <{gmail_address}>"
    msg["To"] = to
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(gmail_address, app_password.replace(" ", ""))
        s.send_message(msg)


def _shell(title: str, inner: str, link_url: str,
           link_text: str = "Open the full sheet (all clips, captions, permission messages)") -> str:
    return f"""<!doctype html><html><body style="margin:0;background:{INK};">
<div style="max-width:560px;margin:0 auto;padding:20px 16px;font-family:Georgia,'Times New Roman',serif;color:{PARCHMENT};background:{INK};">
<div style="color:{GOLD};font-size:13px;letter-spacing:2px;text-transform:uppercase;">Gospelscribe · Faith Clips</div>
<h1 style="font-weight:normal;font-size:24px;margin:6px 0 18px;color:{PARCHMENT};">{html.escape(title)}</h1>
{inner}
<p style="margin:24px 0 0;"><a href="{html.escape(link_url)}" style="color:{GOLD};">{html.escape(link_text)}</a></p>
<p style="font-size:12px;color:{BRONZE};margin-top:18px;">Links and timestamps only. Watch each clip before posting, credit the speaker, and ask permission unless you're stitching their own post.</p>
</div></body></html>"""


def daily_email(clips: list[dict], date: str, sheet_url: str) -> tuple[str, str, str]:
    """(subject, html, text) for the top clips (rows from the Clips tab)."""
    if not clips:
        subject = f"Faith Clips {date}: no new clips today"
        body = ("<p style='font-size:16px;line-height:1.5;'>Nothing passed the filters today. "
                "That happens on quiet news days. The finder ran fine; check the Log tab for details.</p>")
        return subject, _shell("No new clips today", body, sheet_url), \
            f"No new clips passed the filters on {date}. Sheet: {sheet_url}"

    cards, lines = [], []
    for i, c in enumerate(clips, 1):
        quote = c.get("Exact Quote") or "(no captions: watch to hear it)"
        link = c.get("Video Link (timestamped)", "")
        cards.append(f"""
<div style="border:1px solid {BRONZE};border-radius:10px;padding:14px 14px 12px;margin:0 0 14px;">
  <div style="font-size:12px;color:{GOLD};letter-spacing:1px;text-transform:uppercase;">#{i} · Score {html.escape(str(c.get('Score','')))} · {html.escape(c.get('Type',''))}</div>
  <div style="font-size:19px;margin:4px 0 2px;">{html.escape(c.get('Speaker',''))}</div>
  <div style="font-size:13px;color:{BRONZE};margin-bottom:10px;">{html.escape(c.get('Source Channel',''))} · {html.escape(c.get('Start',''))}–{html.escape(c.get('End',''))}</div>
  <div style="font-size:16px;line-height:1.45;font-style:italic;border-left:3px solid {CRIMSON};padding-left:10px;margin:0 0 10px;">“{html.escape(quote)}”</div>
  <div style="font-size:15px;margin:0 0 12px;"><span style="color:{GOLD};">Hook:</span> {html.escape(c.get('Hook 1',''))}</div>
  <div style="font-size:13px;color:{BRONZE};margin:0 0 12px;">Pairs with: {html.escape(c.get('Piece Pairing',''))}</div>
  <a href="{html.escape(link)}" style="display:inline-block;background:{GOLD};color:{INK};text-decoration:none;padding:10px 16px;border-radius:6px;font-size:15px;">Watch at {html.escape(c.get('Start',''))} ▶</a>
</div>""")
        lines.append(f"{i}. {c.get('Speaker','')} ({c.get('Source Channel','')})\n   {link}\n"
                     f"   Quote: {quote}\n   Hook: {c.get('Hook 1','')}\n")
    subject = f"Faith Clips {date}: top {len(clips)} — {clips[0].get('Speaker','')}"
    return (subject, _shell(f"Today's top {len(clips)} clips", "".join(cards), sheet_url),
            "\n".join(lines) + f"\nFull sheet: {sheet_url}")


def problem_email(what: str, detail: str, run_url: str) -> tuple[str, str, str]:
    subject = "Faith Clips Finder: something needs a look"
    body = (f"<p style='font-size:16px;line-height:1.5;'>{html.escape(what)}</p>"
            f"<pre style='white-space:pre-wrap;font-size:12px;color:{BRONZE};'>{html.escape(detail[:3000])}</pre>"
            f"<p style='font-size:15px;'>The README's \"If something breaks\" section says what to do.</p>")
    return (subject, _shell("Something needs a look", body, run_url, "Open this run on GitHub"),
            f"{what}\n\n{detail[:3000]}\n\n{run_url}")
