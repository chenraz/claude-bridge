---
name: claude-bridge
description: Use Claude as an implementation partner from this local desktop chat. Send development tasks to Claude through the bundled API helper, review its replies, apply authorized changes and explain results simply. Use when the user asks to work through Claude; requires local command execution and network access.
---

Keep this desktop chat as the sole conversational interface. The user talks to you;
you compose technical requests for Claude and translate results into plain language.
Do not launch a GUI, browser chat or web server.

## Setup
The bundle is installed as a local skill. Resolve `scripts/bridge.py` relative to
this SKILL.md. Use Python 3.10+. Run `python3 <bridge.py> status` (Windows: `py -3`).
The default credential file is `~/.claude-bridge/.env`; it is separate from the
shareable skill. If not configured, run `python3 <bridge.py> init-config` to create
a private placeholder without overwriting existing credentials. Then explain the
reported absolute path where the user should enter their own key in a local editor. Never read, cat, print, attach or request the key in conversation.
`status` reports only whether it is set, not the secret. After the user saves their
key, run status again. It is a local check, not a live authentication test.

## Work through Claude
1. Establish the intended project directory from the current chat. Translate the
   user's requirements into a concrete implementation task. Write that task to a
   temporary UTF-8 prompt file inside the workspace, without secrets.
2. Call the helper, quoting paths with the host's normal safe shell conventions:
   `python3 <bridge.py> ask --project <project-directory> --session main --prompt-file <task-file>`.
   Add repeated `--context-file <absolute-path>` arguments for relevant project
   files only. The helper does not scan the project. Send only material authorized
   for this task; exclude secrets and unrelated customer data. Local session history
   and selected context are sent to Anthropic. Each customer uses their own API key.
3. Inspect the returned JSON. Claude provides proposals and code, not verified
   local actions. Review its work, apply changes using your own tools and existing
   user authorization, then run appropriate checks. Send failures back to Claude
   for corrections when helpful. The helper itself executes no model-generated code.
4. Keep using the same project path and session for continuity. Sessions are scoped
   by absolute project path. Use a new session for a different task or a summarized
   continuation when history grows. Do not read raw session files unless needed for
   troubleshooting; do not attach them to a customer distribution.
5. Explain the outcome simply in the user's language. Distinguish Claude's proposal
   from changes you applied and tests you actually ran. Handle API errors plainly.

## Permissions and costs
This skill does not introduce or change the desktop app's approval mode. Use the
host's existing file, command and network permissions. Claude cannot approve its
own requests, and you cannot grant approvals reserved for the human. Continue
routine authorized work without redundant confirmations. Stop at any real host
approval block and state what the user must approve; never bypass it or use an
unsafe execution flag. Ask the user to change host permission mode themselves if
needed. There are no Claude Code permission dialogs in this API workflow.

One helper invocation makes one API request, with no automatic retries. Review
`usage` and `stop_reason`; if truncated, request continuation instead of claiming
completion. API usage is separately billed. Do not loop indefinitely: after three
unsuccessful correction attempts for the same issue, report the blocker and a
concrete next step. Never promise a dollar cap; account spending controls are set
in Claude Console. Do not replace Claude with your own implementation silently if
the API is unavailable; explain the limitation and let the user choose.
