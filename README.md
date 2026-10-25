# Desktop Code Bridge

Use your own **Claude Code subscription** from your local GPT/Codex desktop chat.
You describe the app; GPT sends tasks to the official Claude Code CLI, reviews the
proposed code, applies authorized changes and explains the result. No second GUI.

The package ID and repository remain `claude-bridge` for existing installations.
**Version 0.4.0 adds automatic browser sign-in when the customer is disconnected.**

## Install through the desktop interface

In **Plugins > Add marketplace**, enter:

- **Source:** `https://github.com/chenraz/claude-bridge`
- **Git ref:** `main`
- **Sparse paths:** completely empty.

Select **Add marketplace**, then install **Desktop Code Bridge** from **Chenraz Tools**.
If upgrading, refresh/sync the marketplace and update or reinstall the plugin.
Open a new local chat so the new skill instructions are loaded.

Alternative standalone skill installation:

```text
Use $skill-installer to install the skill from:
https://github.com/chenraz/claude-bridge/tree/main/claude-bridge
```

Use one installation route to avoid duplicate skills.

## Start using it: sign-in opens automatically

After installation, plugin setup checks the connection. If the desktop app does
not run setup immediately, the first bridge request performs the same check.
A valid Claude Code subscription login is reused. If signed out, the bridge starts
the official Claude Code browser sign-in automatically. Complete that browser
step with your own subscription account, then the assistant checks the connection.
No API key, .env, password in chat or user-typed terminal command is needed.

In your local desktop chat, write:

```text
Use Claude Bridge for all app-development work in this chat. Build my app: ...
```

**Prerequisites:** official Claude Code CLI, Python 3.10+, local command tools and
network access. If Claude Code is missing, ask the assistant to help install it
from [Anthropic's official source](https://code.claude.com/docs/en/setup).
The bridge does not install it silently or bypass host permission approvals.

Browser sign-in waits up to five minutes and duplicate launches are suppressed.
If the browser does not open or login times out, tell the assistant; it can check
status and troubleshoot. It does not capture authorization codes or passwords.
An existing different account or provider override is reported rather than changed.
The host can still require approval to run commands. A chat that has ended does
not automatically wake up when login completes; return to the chat to continue.

[מדריך קצר בעברית (PDF)](docs/guide-he.pdf)

## Existing API users

The old `~/.claude-bridge/.env` file is **ignored by subscription mode**. You do not
need to delete it. Authentication/provider environment overrides such as
`ANTHROPIC_API_KEY` are detected; the bridge stops and explains what to review
instead of silently billing the API. Variable values are never returned.

The helper retains optional, separately billed API mode for users who explicitly
choose it, by putting `--backend api` before the subcommand. Only this mode uses
`.env`, `init-config` and `setup-token`. Subscription mode never calls the Messages
API directly and never reads or exports Claude Code's OAuth credential files.

## Permissions, usage and privacy

The unmodified official Claude Code binary runs in **safe mode**, with built-in
tools and MCP tools disabled. It produces code proposals; GPT reviews and applies
them using the desktop app's existing permissions. No approval-bypass flags are
used. Do not use `--bare`: it disables subscription login.

The helper invokes Claude Code without tools or subagents. It sends the task,
explicitly selected context and saved conversation history over stdin. Claude Code
runs in the selected project with safe mode and tools disabled. The helper saves its own plain
text JSON history under `~/.claude-bridge/sessions`, scoped by project path.
Never share those histories or send secrets in a prompt.

Normal **Claude subscription limits** apply. The helper performs no API fallback
and no automatic retries. It does not change the customer's account billing or
extra-usage settings. If extra usage is enabled on the account, those account
settings still apply; review them in Claude to control spending.

## View the real Claude Code conversation

After a successful subscription task, the result contains a `native_session` object
with a native UUID and an exact terminal reopen command. Ask the desktop assistant:

```text
Show me the Claude Code session for this project.
```

The assistant runs:

```sh
python3 claude-bridge/scripts/bridge.py session-info --project /your/project --session main
```

Run the returned `resume_command` in a terminal from the project folder. Native
sessions are named `Bridge: PROJECT / SESSION` and saved by official Claude Code;
subsequent bridge tasks use `--resume` with the same UUID. The helper no longer uses
`--no-session-persistence`. A bridge name such as `main` is still distinct from the
native UUID; use the returned command rather than guessing `claude --resume main`.

On supported macOS/x64 Windows with Claude Desktop, the official CLI also supports
`claude --desktop --resume NATIVE_UUID`. Local terminal sessions do not become
ordinary conversations on claude.ai; Linux users should use the terminal command.

For bridge conversations created before 0.3, the next successful task imports the
saved bridge history into a new native session. There is no retroactive native
transcript until that task succeeds. Keep one process writing to a session at a
time; close an interactive resumed session before sending another bridge task.

The native transcript now persists under Claude Code's own local storage as well
as bridge history. Do not distribute either. A timeout may leave a partial native
turn; no automatic retry is made. Reopen the session to inspect it before retrying.

## Development and verification

Python standard library only:

```sh
python3 -m unittest discover -s tests -v
python3 claude-bridge/scripts/bridge.py status
```

The API backend's `--max-tokens` only applies to API mode. Claude Code uses its own
response limits. Local persistence caps conversation turns and selected context.

The tests cover session isolation, credential exclusions, API behavior, subscription
login checks, CLI arguments, absence of API fallback and marketplace packaging.

References: [subscription login](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan),
[programmatic CLI](https://code.claude.com/docs/en/headless),
[third-party product conditions](https://code.claude.com/docs/en/legal-and-compliance),
[OpenAI skills](https://learn.chatgpt.com/docs/build-skills).
