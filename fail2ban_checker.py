#!/usr/bin/env python3
import subprocess
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------
# SMTP Configuration
SMTP_SERVER = 'in-v3.mailjet.com'
SMTP_PORT = 587
SMTP_USER = 'YOUR_API_KEY'
SMTP_PASS = 'YOUR_API_SECRET'
SENDER_EMAIL = 'sender@your-domain.com'
RECEIVER_EMAIL = 'recipient@email.com'

# Configure subject tag
SUBJECT_TAG = "[SERVER-ALERT]"
# -----------------------------

def get_fail2ban_status():
    """Returns a dict with jail name -> (currently banned, banned IPs as sorted list)"""
    result = {}
    try:
        # Get list of jails
        output = subprocess.check_output(['sudo', 'fail2ban-client', 'status'], text=True)
        jail_line = [line for line in output.splitlines() if "Jail list:" in line]
        if not jail_line:
            return result
        jails = jail_line[0].split(":", 1)[1].strip().split(",")
        jails = [j.strip() for j in jails]

        # Get status for each jail
        for jail in jails:
            jail_status = subprocess.check_output(['sudo', 'fail2ban-client', 'status', jail], text=True)
            currently_banned = "0"
            banned_ips = []
            for line in jail_status.splitlines():
                if "Currently banned:" in line:
                    currently_banned = line.split(":")[1].strip()
                if "Banned IP list:" in line:
                    ips = line.split(":",1)[1].strip()
                    if ips:
                        banned_ips = sorted(ip.strip() for ip in ips.split())
            result[jail] = (currently_banned, banned_ips)
    except subprocess.CalledProcessError as e:
        print("Error retrieving Fail2Ban status:", e)
    return result

def send_email(body_text):
    """Send the Fail2Ban report via SMTP"""
    hostname = socket.gethostname()
    subject = f"{SUBJECT_TAG} Fail2Ban report for {hostname}"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body_text, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)

def main():
    status = get_fail2ban_status()
    if not status:
        print("No jails found or Fail2Ban not running.")
        return

    body_lines = []
    for jail, (banned_count, ip_list) in status.items():
        body_lines.append(f"=== {jail} ===")
        body_lines.append(f"Currently banned: {banned_count}")
        if ip_list:
            body_lines.append("Banned IPs:")
            for ip in ip_list:
                body_lines.append(f" - {ip}")
        else:
            body_lines.append("Banned IPs: None")
        body_lines.append("")  # leere Zeile zwischen Jails

    body_text = "\n".join(body_lines)
    send_email(body_text)

if __name__ == "__main__":
    main()
