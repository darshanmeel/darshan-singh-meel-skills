# Claude Code global setup

- `claude-global/`: full version · `claude-global-panini/`: compressed (sūtra) version. Install one: zip its contents and `unzip -o <zip> -d ~/.claude/`, then restart Claude Code.
- Skill-usage log (once): `python3 ~/.claude/hooks/install-skill-log.py`
- Notebook cells run by Claude: `pip install nbclient nbformat ipykernel` + a database connector.
- Docs v2 layout check: `pip install playwright && playwright install chromium`.
- `docs-v2-upgrade-prompt.md`: paste into Claude Code (Opus) to finish docs-v2 (what's done, what's pending).
- `context-prompt.md`: paste at the start of a new chat so Claude knows this whole setup, my preferences, and what is pending.

## License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE))
- MIT License ([LICENSE-MIT](LICENSE-MIT))

at your option.
