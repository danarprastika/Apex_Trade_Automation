#!/usr/bin/env bash
set -euo pipefail

SSH_PORT="${SSH_PORT:-22}"

echo "[*] Updating packages..."
apt-get update
apt-get upgrade -y

echo "[*] Installing UFW, Fail2Ban, and Nginx..."
apt-get install -y ufw fail2ban nginx

echo "[*] Configuring UFW..."
ufw default deny incoming
ufw default allow outgoing
ufw allow "${SSH_PORT}/tcp"
ufw allow http
ufw allow https

echo "[*] Enabling UFW..."
ufw --force enable

echo "[*] Configuring Fail2Ban..."
cat >/etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
port = ${SSH_PORT}
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
EOF

systemctl restart fail2ban
systemctl enable fail2ban

echo "[*] Security hardening complete."
