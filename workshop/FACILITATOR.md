# Facilitator notes — contains puzzle spoilers ⚠️

Do **not** give this file to the player agent during the discovery exercise.

## Hidden mechanics

- Stages cycle modulo 3: seed `0` → sprout `1` → bloom `2` → seed `0`.
- **Sun** on a tile changes that tile and the tile directly **north** (if one exists). Ordinary garden plants move +1 stage. Moonflowers (`M`) move **-1** stage under Sun.
- **Rain** on a tile advances that tile and its immediate horizontal neighbors +1 stage. Moonflowers still move +1 under Rain.
- **Wind** on a row shifts the *growth-stage values* one square to the right, wrapping at the edge. The species stay rooted in the same coordinates.
- Only starred tiles count toward the win condition; all must be stage 2 simultaneously.

## Twist

Levels 1–3 have only ordinary plants (`G`), so generalizing Sun = +1 is reasonable. At level 4 Moonflowers (`M`) appear, and **at least one is always a target**. An agent that uses past experience uncritically is likely to make a mistake. A good agent changes its rule to be conditional on species.

## Why boards are solvable

The game starts with a complete winning board, then scrambles it with deterministic, invertible actions. Inverses: do Sun/Rain twice or Wind `(board width - 1)` times. The allowed move budget is at least as large as that constructed reverse path. The reverse path is never persisted in the player session.

## Keeping the evaluation honest

- Freeze practice and evaluation seeds before the workshop.
- Compare the **same seeds** for baseline and improved versions.
- Restrict the player to observation and actions; don't let it view source or this file. Local Python source isolation is a social/process control, not a hardened sandbox.
- Log prompts, game results, skill revisions, tool calls, and model settings.
- A skill file is prompt memory, **not** learning the model weights.
- Consider two evaluation tracks: level 2 for known rules and level 4+ for adaptation to novelty.
- Most importantly, prevent evaluator leakage: no adapting skills while doing the final evaluation.

## Troubleshooting

- `No current game`: run `start`.
- `A game is in progress`: finish it or `start --force` (recorded as abandoned).
- Invalid coordinate: rows are 1-based and columns are A, B, C, D depending on the board size.
- Use `look --json` if the agent struggles to parse the ASCII grid. The JSON observation does not reveal mechanics.
- If puzzles feel hard, repeat level 1 with different seeds and allow more reflection between rounds; don't silently change scoring.
