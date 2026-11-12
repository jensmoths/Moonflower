# 🌙 Moonflower

**A slow, turn-based terminal puzzle designed for AI agents to learn by playing.**

There is no bot to write, no web browser, no API key, and no time pressure. The player (human or Copilot CLI) sees a small ASCII garden, issues one action, observes the outcome, and can record what it learned. At level 4, a new plant species appears and challenges the strategy it developed on earlier levels.

## Play in 30 seconds

Requires **Python 3.9+**; no third-party packages.

```bash
python moonflower.py guide
python moonflower.py start --level 1 --seed 11
python moonflower.py look
python moonflower.py sun B2
python moonflower.py rain A1
python moonflower.py wind 2
python moonflower.py replay
python moonflower.py results
```

Each command exits after printing a readable board. Session state is saved under `.moonflower/`, so a CLI agent can issue commands in separate terminal calls and continue the same game. Move results are deterministic and immediate.

Alternatively, install the `moonflower` command with `python -m pip install .` and replace `python moonflower.py` with `moonflower` in all examples.

### How to read the board

```text
       A   B   C
   1   G2  G1* G0
   2   G0* G2* M1*
   3   G1  G2  M0

Targets blooming: 1/3 | Moves: 2/14 | Status: ACTIVE
```

- `G` = ordinary garden plant; `M` = unfamiliar species (introduced at level 4).
- `0` = seed, `1` = sprout, `2` = bloom.
- `*` = target. **All targets must be blooming at the same time.**
- `sun CELL`, `rain CELL`, `wind ROW` each cost one move.
- Effects are not documented in player help. Observe the board and form hypotheses.

The first three levels teach the game's physics. **Levels 4–6 introduce a new species** whose behavior makes some earlier assumptions fail. All levels are solvable within their move budgets, and replayable with `--seed`.

### Agent-friendly commands

| Command | Purpose |
| --- | --- |
| `python moonflower.py start --level 4 --seed 42` | Begin a reproducible game |
| `python moonflower.py look` | Inspect the current board |
| `python moonflower.py look --json` | Inspect a structured observation |
| `python moonflower.py sun B2` | Act on tile B2 |
| `python moonflower.py rain A1` | Act on tile A1 |
| `python moonflower.py wind 2` | Act on row 2 |
| `python moonflower.py replay --last 3` | Inspect recent moves and outcomes |
| `python moonflower.py results --json` | Machine-readable completed-game scores |
| `python moonflower.py start --force ...` | Abandon the current game (recorded as abandoned) |

An invalid move exits with code `2` and does not consume a turn. The session directory can be changed via `MOONFLOWER_HOME=/some/path` or `--home /some/path` **before** the subcommand. This lets workshop participants have independent sessions.

## Workshop: can Copilot improve its own skill?

See [the 60-minute workshop](workshop/WORKSHOP.md) and [starter agent skill](skills/garden-player/SKILL.md). The learning artifact is a `SKILL.md` maintained by the agent, **not a program or bot that plays the game**.

1. Run practice puzzles with only the CLI game screen.
2. After each run, inspect the replay and write down observed effects, exceptions, and tactics.
3. Revise `SKILL.md` with testable, general rules.
4. Introduce level 4 and watch the agent revise beliefs that no longer hold.
5. Compare the improved agent with a fresh agent using evaluation seeds and the same budget.

**Experimental integrity:** The game is open source, so a local coding agent *could* inspect this Python file and discover the rules. For a meaningful workshop, put the player in a separate working directory, expose only the installed `moonflower` command, and explicitly prohibit source inspection, debugging, code search, and internet lookups. This is a workshop boundary, **not a security boundary**: Python packages can still be inspected. A truly blind setup requires facilitator-controlled execution or isolated access to the executable interface.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

- `moonflower.py` — game engine, terminal UI, persistence, replay, scoring
- `tests/` — determinism, mechanics, persistence, and CLI checks
- `skills/garden-player/SKILL.md` — intentionally minimal agent instructions
- `workshop/WORKSHOP.md` — facilitator timeline and participant prompt
- `workshop/FACILITATOR.md` — spoiler rules, fairness, evaluation guidance

MIT licensed. No telemetry, accounts, downloads, or network access.
