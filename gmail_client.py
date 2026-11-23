"""Gmail via IMAP + App Password. Reads mail, saves reply DRAFTS. Never sends."""
import os, imaplib, email, time
from email.header import decode_header, make_header
from email.mime.text import MIMEText
from email.utils import parseaddr

# Senders containing these words are treated as automated and skipped.
SKIP = ("noreply", "no-reply", "donotreply", "do-not-reply", "notification",
        "alerts", "jobalerts", "newsletter", "mailer-daemon")


def _connect():
    user, pw = os.getenv("GMAIL_ADDRESS"), os.getenv("GMAIL_APP_PASSWORD")
    if not user or not pw:
        raise SystemExit("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env")
    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login(user, pw.replace(" ", ""))
    return m


def _dec(v):
    return str(make_header(decode_header(v or "")))


def _body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                p = part.get_payload(decode=True) or b""
                return p.decode(part.get_content_charset() or "utf-8", "ignore")
        return ""
    p = msg.get_payload(decode=True) or b""
    return p.decode(msg.get_content_charset() or "utf-8", "ignore")


def _automated(sender: str) -> bool:
    s = sender.lower()
    return any(w in s for w in SKIP)


def unread(max_results=10, skip_automated=True):
    m = _connect()
    m.select("INBOX", readonly=True)  # readonly: mails stay unread
    _, data = m.search(None, "UNSEEN")
    ids = data[0].split()[-60:]  # look at latest 60 unread
    out = []
    for i in reversed(ids):
        _, d = m.fetch(i, "(BODY.PEEK[])")
        msg = email.message_from_bytes(d[0][1])
        sender = _dec(msg["From"])
        if skip_automated and _automated(sender):
            continue
        out.append({
            "from": sender,
            "subject": _dec(msg["Subject"]),
            "message_id": msg["Message-ID"] or "",
            "body": _body(msg)[:3000],
        })
        if len(out) >= max_results:
            break
    m.logout()
    return out


def save_draft(mail, reply_text):
    msg = MIMEText(reply_text)
    msg["From"] = os.getenv("GMAIL_ADDRESS")
    msg["To"] = parseaddr(mail["from"])[1]
    s = mail["subject"]
    msg["Subject"] = s if s.lower().startswith("re:") else f"Re: {s}"
    if mail["message_id"]:
        msg["In-Reply-To"] = mail["message_id"]
        msg["References"] = mail["message_id"]
    m = _connect()
    m.append("[Gmail]/Drafts", "\\Draft", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    m.logout()
