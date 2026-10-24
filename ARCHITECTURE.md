# Architecture

What this repository is, and the rule that keeps it safe to publish. When a change doesn't fit
this, change this file first, on purpose, in the same commit.

## The shape

This is the special `.github` repository for the `sh4i-yurei` account. GitHub uses its default
community health files, such as issue forms and the pull-request template, for every repository
on the account that has none of its own, including repositories created later. Nothing here runs
in production; the only code is the CI that validates the files.

## The pieces

| Piece | Owns | Must not |
|---|---|---|
| Issue forms and their config | The forms every repository without its own offers, each adding its own `type:` label | Name anything specific to one repository |
| Pull-request template | The sections every pull request fills in | Assume a kind of project, such as infrastructure |
| `.github/workflows/` | Validating the forms against GitHub's own schemas, and linting the workflows | Need a secret |
| `README.md` | What this repository is for | Link anything private |

## Rules

- **This repository is public.** It never names a private repository, a host, or any other
  piece of the estate. Labels, board mappings and anything else that would are kept in private
  configuration.
- **Every file is worded for any kind of repository:** a website, a service, infrastructure code,
  tooling or a game.
- **Call the authoritative tool.** Forms are validated against GitHub's schemas through
  `check-jsonschema`, pinned to a version, never against a hand-written check.
