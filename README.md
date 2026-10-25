# Claude Bridge

Work with Claude from your existing local Codex desktop chat. You talk to GPT;
GPT sends implementation tasks to Claude, reviews the replies, applies authorized
changes, runs available checks and explains the results. No separate GUI or server.

## Install from GitHub

In a **local Codex desktop chat**, send:

```text
Use $skill-installer to install the skill from:
https://github.com/chenraz/claude-bridge/tree/main/claude-bridge
```

Start a new chat if the skill is not visible; restart the app if needed. Then send:

```text
Use $claude-bridge. Set up my local configuration, then help me build my app.
```

The skill runs its bundled `init-config` command to create a placeholder credential
file and reports its exact location. It never overwrites an existing file.

**Requirements:** Python 3.10+, local file/command tools and network access in the
host app, and your own funded Claude API account. Installing the skill does not
install Python. The assistant can use a compatible bundled Python if available.
A file-upload-only chat cannot run this helper.

## Add your own Claude API key

Create a key in [Claude Console](https://platform.claude.com/settings/keys).
Open the local file in a text editor:

- Windows: `%USERPROFILE%\.claude-bridge\.env`
- macOS/Linux: `~/.claude-bridge/.env`

Replace the placeholder, keep the filename exactly `.env`, then save:

```dotenv
ANTHROPIC_API_KEY=PASTE_YOUR_KEY_HERE
CLAUDE_MODEL=claude-sonnet-5-5
```

The path printed by the helper is authoritative. **Never paste the key into chat,
commit it, or send it to the distributor.** Each customer uses their own key.
Optional: set `ANTHROPIC_WORKSPACE_ID` if your key needs an explicit workspace.
Environment variables override file values.

Tell GPT you saved the key. It can run `status` without displaying the key.
The first real task verifies API access and incurs API usage.

[מדריך התקנה קצר בעברית (PDF)](docs/guide-he.pdf)

## Permissions and limitations

Claude generates proposals and code; the helper itself executes no generated
code and has no file-edit tools. GPT reviews and applies changes with the desktop
app's existing permissions. This skill cannot change approval modes or approve
human-only requests. There are no Claude Code permission dialogs: this uses the API.

API calls are billed separately from a Claude chat subscription. Each helper call
makes one API request with no automatic retries. The default output limit is 4096
tokens. Set account spending controls in Claude Console; this is not a dollar cap.
Live Claude access was not tested with a real key before publication.

Task text, explicitly selected project context and the session history are sent
to Anthropic. Local history is plain-text JSON in `~/.claude-bridge/sessions` and
is separated by project path. Credential files are excluded from context by the
helper, but users and GPT must still avoid putting secrets in task text.

The `.env` file is plain text. New files are mode 600 on Linux/macOS; on Windows,
normal inherited account permissions apply. Store it in a private user directory.

## Development

Python standard library only. Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

The tests use mocked API responses and temporary fake keys. They check history
isolation, failure recovery, selected context, credential exclusions, configuration
creation, secret-free status output and the single-request API payload.

The helper also supports `--env-file` and `--state-dir` before its subcommand.
Run `python3 claude-bridge/scripts/bridge.py --help` for details.

Installation references: [OpenAI skills documentation](https://learn.chatgpt.com/docs/build-skills).
API references: [Messages API](https://platform.claude.com/docs/en/api/messages/create),
[models](https://platform.claude.com/docs/en/models/overview).
