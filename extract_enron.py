import os
from email import policy
from email.parser import BytesParser
import csv

# ---------------- CONFIG ----------------
ENRON_DIR = r"C:\ProjectFYP2\enron_mail_20150507\maildir"  # your maildir
OUTPUT_CSV = "enron_legit.csv"

# ---------------- PROCESS EMAILS ----------------
emails = []

print("Scanning folder (this may take a while)...")

for root, dirs, files in os.walk(ENRON_DIR):  # recursive walk
    for file in files:
        file_path = os.path.join(root, file)
        try:
            with open(file_path, "rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)
            
            subject = msg.get("subject") or ""
            body = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode(errors="replace")
            else:
                body = msg.get_payload(decode=True).decode(errors="replace")
            
            emails.append([subject, body, "legitimate"])
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

# ---------------- SAVE CSV ----------------
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["subject", "body", "label"])
    writer.writerows(emails)

print(f"Finished! Extracted {len(emails)} emails to {OUTPUT_CSV}")
