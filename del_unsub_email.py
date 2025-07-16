# Ctrl (Cmd) + H to replace "unsubscribe" with "your keyword"

import imaplib # Works on Windows/Linux/Unix-like {pip install imaplib}
import email
from email.header import decode_header
import time
import psutil   # Works on Windows/Linux/Mac {pip install psutil}

# Your email credentials
EMAIL = "siromion@gmail.com"
PASSWORD = "jqjx ofbt usvx ndcw"
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def safe_decode_header(raw_header):
    """Decode an email header safely."""
    if not raw_header:
        return ""
    parts = decode_header(raw_header)
    decoded_str, encoding = parts[0]
    if isinstance(decoded_str, bytes):
        return decoded_str.decode(encoding if encoding else "utf-8", errors="ignore")
    return decoded_str or ""

def delete_emails_with_unsubscribe():
    try:
        # Track start time & memory
        start_time = time.perf_counter()
        process = psutil.Process()
        start_mem_mb = process.memory_info().rss / (1024 * 1024)  # in MB

        # Connect to the server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        # Search for all emails
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        total_emails = len(email_ids)

        print(f"Total emails found: {total_emails}")

        deleted_count = 0

        for eid in email_ids:
            res, msg_data = mail.fetch(eid, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # --- SAFE SUBJECT HANDLING ---
                    subject = safe_decode_header(msg["Subject"])

                    # --- SAFE BODY HANDLING ---
                    body_found = False
                    if msg.is_multipart():
                        for part in msg.walk():
                            ctype = part.get_content_type()
                            if ctype == "text/plain":
                                try:
                                    body = part.get_payload(decode=True)
                                    if body and b"unsubscribe" in body.lower():
                                        body_found = True
                                        break
                                except Exception:
                                    continue
                    else:
                        try:
                            body = msg.get_payload(decode=True)
                            if body and b"unsubscribe" in body.lower():
                                body_found = True
                        except Exception:
                            body_found = False

                    # --- DECISION ---
                    if "unsubscribe" in subject.lower() or body_found:
                        mail.store(eid, '+FLAGS', '\\Deleted')  # Mark for deletion
                        print(f"Deleted: {subject if subject else '(No Subject)'}")
                        deleted_count += 1

        # Permanently delete all flagged emails
        mail.expunge()
        mail.logout()

        # Track end time & memory
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        emails_per_second = total_emails / elapsed_time if elapsed_time > 0 else 0

        end_mem_mb = process.memory_info().rss / (1024 * 1024)
        mem_used_mb = end_mem_mb - start_mem_mb

        print("\n--- Efficiency Report ---")
        print(f"Deleted {deleted_count} of {total_emails} emails containing 'unsubscribe'")
        print(f"Elapsed Time: {elapsed_time:.2f} seconds")
        print(f"Processing Speed: {emails_per_second:.2f} emails/second")
        print(f"Approx. Memory Usage: {mem_used_mb:.2f} MB")

    except Exception as e:
        print("Error:", str(e))

# Run the script
delete_emails_with_unsubscribe()
