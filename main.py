"""Dope-AI Phase 1: Gmail + Calendar + Gemini.

  python main.py brief    -> morning brief (meetings + important unread mail)
  python main.py drafts   -> AI reply drafts, saved to Gmail Drafts after your OK
"""
import sys
from dotenv import load_dotenv

load_dotenv()

import brain, gmail_client, calendar_client  # noqa: E402


def brief():
    events = calendar_client.today_events()
    mails = gmail_client.unread(10)
    mail_txt = "\n\n".join(
        f"From: {m['from']}\nSubject: {m['subject']}\n{m['body'][:500]}" for m in mails
    ) or "No unread mail."
    prompt = (
        "Write a short morning brief in simple English.\n"
        f"TODAY'S EVENTS:\n{chr(10).join(events) or 'None'}\n\n"
        f"UNREAD EMAILS:\n{mail_txt}\n\n"
        "List: 1) meetings, 2) the most important emails and why, 3) what to do first."
    )
    print(brain.ask(prompt))


def drafts():
    mails = gmail_client.unread(5)
    if not mails:
        print("No unread mail.")
        return
    for m in mails:
        print("=" * 60)
        print(f"From: {m['from']}\nSubject: {m['subject']}\n")
        reply = brain.ask(
            "Write a short, polite reply to this email. If no reply is needed, "
            f"answer exactly NO_REPLY.\n\nEmail:\n{m['body']}"
        )
        if reply.strip() == "NO_REPLY":
            print("(no reply needed)")
            continue
        print("--- Draft ---\n" + reply)
        if input("\nSave to Gmail Drafts? [y/N] ").strip().lower() == "y":
            gmail_client.save_draft(m, reply)
            print("Saved (not sent).")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"brief": brief, "drafts": drafts}.get(cmd, lambda: print(__doc__))()
