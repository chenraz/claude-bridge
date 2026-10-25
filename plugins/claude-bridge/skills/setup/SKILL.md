---
name: code-bridge-setup
description: Check the Desktop Code Bridge connection after installing this plugin and start official Claude subscription browser sign-in if needed.
---

Run the bundled helper at `../claude-bridge/scripts/bridge.py`, relative to this
folder, using Python 3.10+: `python3 <helper> ensure-login` (Windows: `py -3`).
If already connected, report ready and leave the login alone. If sign-in starts,
tell the customer to complete the official browser step, then check with the
helper's `status` command. Do not ask them to type terminal commands or supply
keys/passwords in chat. Do not approve authentication consent for them.
If Claude Code is missing, help install it from https://code.claude.com/docs/en/setup
when authorized, then run ensure-login. Preserve host approval requirements.
If connection is blocked by environment overrides, status errors, or a different
signed-in account, explain that issue instead of switching accounts automatically.
When connected, tell the customer to describe their app in this chat. Do not run
a model request just to check login. Do not poll indefinitely or launch duplicates.
