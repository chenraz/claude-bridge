---
name: claude-bridge
description: Use the customer's Claude Code subscription as an implementation partner from this desktop chat. Send tasks through the official local Claude Code CLI, review its replies, apply authorized changes and explain results simply. Use when asked to work through Claude; requires local commands and a signed-in Claude Code installation.
---

Keep this desktop chat as the interface. The user talks to you; you write technical
requests for Claude Code, review its replies and explain results in plain language.
If asked to use this workflow for the whole chat, retain that instruction for
subsequent app-development tasks until the user changes it. Do not launch a GUI,
web server or second chat window.

## Default: the customer's subscription
Resolve `scripts/bridge.py` relative to this SKILL.md. Use Python 3.10+.
Run `python3 <bridge.py> status` (Windows: `py -3`). This checks official Claude Code
login and returns only sanitized metadata; it does not send a model prompt.

If the official CLI is missing, direct the customer to
https://code.claude.com/docs/en/setup. Help install from the official source when
authorized. The customer then runs `claude auth login` in their own terminal and
completes the official browser sign-in with their own Pro/Max subscription account.
Do not collect passwords, export OAuth tokens, read credential files or reuse their
subscription credential against the Messages API. A Claude chat subscription is
not an API key. Each customer signs in on their own computer.

Run status again after login. Do not request an API key or create .env in subscription
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
   history through the unmodified official Claude Code CLI. No direct API call is
   made in subscription mode.
3. Review the returned JSON. Claude Code runs in safe mode, with built-in and MCP
   tools disabled; it provides proposed code, and does not execute local actions.
   You apply reviewed changes with your own desktop tools, under the host's existing
   authorization and permission rules, and run meaningful checks. Send relevant
   failures back to Claude for correction. Never claim unperformed tests.
4. Reuse the project path and session for continuity. Sessions are scoped by absolute
   project path and saved under ~/.claude-bridge/sessions. Start another session with
   a project summary when history grows. Never distribute session files.
5. Explain results in the user's language. After three unsuccessful corrections
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
