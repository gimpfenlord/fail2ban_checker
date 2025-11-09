# Fail2Ban Email Reporter

A Python script that **monitors active Fail2Ban bans** and automatically sends email notifications.  
Each email includes:
- The current hostname in the subject
- All Fail2Ban jails with the number of currently banned IPs
- A sorted list of banned IPs (one IP per line)

Perfect for **centrally monitoring Fail2Ban activity** and receiving alerts.

---

## Features

- Checks all Fail2Ban jails
- Shows `Currently banned` + `Banned IPs` sorted
- Sends email via SMTP (TLS) with configurable server, user, and password
- Dynamic subject line including the hostname
- Easy to set up as a cronjob
- No sensitive data required
