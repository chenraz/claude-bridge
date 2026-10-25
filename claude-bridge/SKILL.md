---
name: claude-bridge
description: Use the customer's Claude Code subscription as an implementation partner from this desktop chat. Send tasks through the official local Claude Code CLI, review its replies, apply authorized changes and explain results simply. Use when asked to work through Claude; requires local commands and a signed-in Claude Code installation.
---

Keep this desktop chat as the interface. The user talks to you; you write technical
requests for Claude Code, review its replies and explain results in plain language.
If asked to use this workflow for the whole chat, retain that instruction for
subsequent app-development tasks until the user changes it. Do not launch a GUI or web server. Open a second session window only when the
user explicitly asks to inspect or resume the Claude Code conversation.

## Default: the customer's subscription
Resolve `scripts/bridge.py` relative to this SKILL.md. Use Python 3.10+.
At first use run `python3 <bridge.py> ensure-login` (Windows: `py -3`).
It checks official Claude Code authentication and, only if signed out, automatically
starts the official subscription browser login. Do not require the user to ask
for connection or type a terminal command. Tell them briefly that Claude sign-in
is opening, then let them complete it privately in the browser.

If `action_required` is `sign_in`, retain the user's development task and do not
claim it was sent. Check `status` after the browser step. While actively waiting,
space checks about 15 seconds apart, communicate useful progress, and stop after
five minutes if the user has not completed sign-in. If the turn has ended, continue
when the user returns. No timer or background job will automatically resume the
GPT chat. `ensure-login` avoids duplicate login launches for five minutes.

If the official CLI is missing, help install it from the official source when
authorized: https://code.claude.com/docs/en/setup. Use an available Python 3.10+.
If environment overrides, a different signed-in account, or an authentication
status error is reported, explain the issue instead of forcing a new login.
Normal host permission prompts still apply to launching commands and opening a
browser; never approve human-only access consent on the user's behalf.
Do not collect passwords, export OAuth tokens, read credential files or reuse their
subscription credential against the Messages API. A Claude chat subscription is
not an API key. Each customer signs in on their own computer.

Run status again after login and continue the pending task when connected. Do not request an API key or create .env in subscription
mode. The previous version's .env is ignored and can remain untouched. If environment
variables override subscription authentication, explain which variable names need
attention; never print their values or change credentials automatically. Do not
change the user's extra-usage or billing settings. Subscription quotas still apply.
No automatic switch to API billing is implemented by this helper.

## Work through Claude Code
1. Resolve the intended project directory. Write a concrete task to a temporary
   UTF-8 prompt file in the workspace, excluding secrets.
2. Run `python3 <bridge.py> ask --project <project-directory> --session main --prompt-file <task-file>`.
   Add repeated `--context-file <absolute-path>` only for relevant authorized
   project files. The helper sends the task, chosen context and saved session
   history through the unmodified official Claude Code CLI. Version 0.3 saves and
   resumes a native named Claude Code session, with its workspace set to the project. No direct API call is
   made in subscription mode.
3. Review the returned JSON. Claude Code runs in safe mode, with built-in and MCP
   tools disabled; it provides proposed code, and does not execute local actions.
   You apply reviewed changes with your own desktop tools, under the host's existing
   authorization and permission rules, and run meaningful checks. Send relevant
   failures back to Claude for correction. Never claim unperformed tests.
4. Reuse the project path and session for continuity. Sessions are scoped by absolute
   project path and saved under ~/.claude-bridge/sessions. Start another session with
   a project summary when history grows. Never distribute session files.
5. When the user asks to see the Claude session, run
   `python3 <bridge.py> session-info --project <project-directory> --session main`.
   Show the returned native session ID and terminal `resume_command`, and tell the
   user to run it from the project folder. Do not dump raw JSON conversation files.
   This resumes the actual saved local Claude Code conversation, with tools still
   disabled. It does not sync a chat to claude.ai. On supported macOS/Windows Claude
   Desktop installations, `claude --desktop --resume <native-session-id>` can open
   it in the desktop Code interface; do not promise that on Linux. If no native ID
   exists, explain that pre-0.3 history is imported on the next successful task.
6. Explain results in the user's language. After three unsuccessful corrections
   for the same issue, report the blocker and a concrete next step. If a quota or
   login error occurs, stop and explain; do not silently implement a fallback.

The helper starts no Claude agents or tool loops; it runs a single noninteractive
Claude Code task for each invocation. It does not alter Claude Code's binary or
normal authentication options. Never use `--bare`, which disables subscription login,
or any permission-bypass flag.

## Permissions
This skill cannot change the host's approval mode or approve human-only requests.
Continue authorized routine work without redundant questions; stop at actual host
approval blocks. No Claude Code file/command permission prompts arise in this
proposal-only mode because its tools are disabled. GPT still uses normal host
permissions when applying work. Never promise unlimited subscription usage.

## Optional API mode, only if explicitly requested
The helper retains `--backend api` for users who deliberately choose separately
billed API access. Place it before the subcommand. Only in that mode may you run
`init-config` to create ~/.claude-bridge/.env, without overwriting an existing file.
The user enters their own key privately in a local editor. Never read or print it.
API mode makes one Messages API request with no automatic retries. A timeout can
still be billed. Do not select API mode to get around subscription limits.
