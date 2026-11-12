# Moonflower workshop — the agent that learns to play

**Audience:** developers using GitHub Copilot CLI. **Duration:** 60–75 minutes. **Resources:** Python 3.9+, a terminal, Copilot CLI, and this open-source game. No business data, hosted services, or bot programming.

## The experiment

Can an unchanged language model become a better player when it reviews its own games and edits a persistent `SKILL.md`? And can it adapt when a new plant species invalidates some of what it learned?

### Before participants arrive

- Facilitator: run `python -m unittest discover -s tests -v` and test the game in your shell.
- Put the game on the participant's `PATH` (or provide a command wrapper). If using `python moonflower.py`, provide that command without asking the agent to open the file.
- Ensure each team has its own `MOONFLOWER_HOME` and an independent, writable `SKILL.md` copy.
- Give the player only terminal action permissions. Keep implementation and facilitator notes out of its normal context.
- Freeze the evaluation seed list. Never use evaluation boards for practice or instruction updates.

### 0–10 minutes: first contact

Give Copilot this prompt:

> You are playing Moonflower, a turn-based terminal game. Your job is to **play**, not write a bot. You may run `moonflower guide`, `moonflower start`, `moonflower look`, `moonflower sun`, `moonflower rain`, `moonflower wind`, `moonflower replay`, and `moonflower results`. Do not read the game's source, inspect its installed package, search the web for rules, or write code to solve the game. Your strategy may be updated only in your own SKILL.md after a game. Start level 1 seed 11. Narrate your hypothesis before each move; prefer evidence over guesses.

If the command isn't installed, use `python /path/to/moonflower.py` before each subcommand.

### 10–30 minutes: discover the mechanics

Play levels 1, 2, and 3 with practice seeds `11`, `22`, and `33`, respectively. After each game, review moves and have Copilot propose a concise SKILL.md revision with:

- Discovered mechanics (each with supporting before/after observations)
- Planning heuristics, including situations where they might fail
- Rejected hypotheses and open questions

Ask teams not to look up the rules and not to modify the game source. The goal is **learning from experience**, not implementing a solver.

### 30–45 minutes: the twist 🌙

Start `moonflower start --level 4 --seed 44`. A new species appears. Let the agent act on its existing strategy before telling it to look for counterexamples. Ask it to update its skill and explain exactly which generalization failed.

If time allows, play level 5 on seed `55`.

### 45–60 minutes: evaluation and discussion

Have a **fresh** agent using the initial SKILL.md and an **improved** agent using the learned SKILL.md play separate sessions using the same levels and seeds: level 2 (`102`), level 4 (`104`), and level 5 (`105`). Give them identical move budgets and similar reasoning/token budgets. Use separate `MOONFLOWER_HOME` directories.

Record success rate, targets blooming at the final state, moves used on wins, and token/tool-call costs if available. Run more seeds if time permits; three games illustrate behavior but do **not** establish statistical significance.

### Discussion prompts

- Did the agent *test* hypotheses or just create plausible explanations?
- Did it learn game mechanics or merely memorize an action sequence?
- Did the twist cause a local revision or a wholesale reset of strategy?
- Did the richer skill improve generalization on previously unseen seeds?
- Was performance limited by planning, observation, or tool use?

## Scorecard

| Team | Version | Level / seed | Won? | Moves used | Targets blooming | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Example | Fresh | 4 / 104 | — | — | — | — |
| Example | Improved | 4 / 104 | — | — | — | — |

Avoid declaring a win from one lucky puzzle. Alternate which version plays first to reduce anchoring.
