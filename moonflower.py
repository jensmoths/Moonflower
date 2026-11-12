"""Moonflower: a deterministic, turn-based discovery game for terminal agents.

No third-party dependencies. Play with: python moonflower.py start --level 1 --seed 11
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import random
import sys
from datetime import datetime, timezone

VERSION = 1
# board size, target count, scramble turns, moonflower count, move budget
LEVELS = {
    1: (3, 4, 2, 0, 8),
    2: (3, 5, 3, 0, 10),
    3: (4, 7, 4, 0, 14),
    4: (3, 5, 4, 2, 14),
    5: (4, 8, 5, 4, 18),
    6: (4, 11, 7, 5, 24),
}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def home_dir(arg=None):
    return Path(arg or os.environ.get("MOONFLOWER_HOME") or ".moonflower").expanduser()


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_session(home):
    path = home / "session.json"
    if not path.exists():
        raise ValueError("No current game. Use: moonflower start --level 1 --seed 11")
    try:
        session = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Cannot read session: {exc}") from exc
    if session.get("version") != VERSION:
        raise ValueError("Incompatible saved game version.")
    return session


def cell_index(name, size):
    name = name.strip().upper()
    if len(name) < 2 or not name[0].isalpha() or not name[1:].isdigit():
        raise ValueError(f"Invalid tile '{name}'. Use A1, B2, etc.")
    col, row = ord(name[0]) - ord("A"), int(name[1:]) - 1
    if not (0 <= col < size and 0 <= row < size):
        raise ValueError(f"Tile '{name}' is outside the {size}x{size} board.")
    return row * size + col


def cell_name(index, size):
    return f"{chr(ord('A') + index % size)}{index // size + 1}"


def apply_action(cells, species, size, action, position):
    """Return a fresh board. The rules live here, not in player-facing help."""
    values = list(cells)
    if action == "wind":
        if not 0 <= position < size:
            raise ValueError("Invalid wind row.")
        begin = position * size
        row = values[begin : begin + size]
        values[begin : begin + size] = row[-1:] + row[:-1]
    elif action in ("sun", "rain"):
        if not 0 <= position < size * size:
            raise ValueError("Invalid tile.")
        affected = [position]
        if action == "sun" and position >= size:
            affected.append(position - size)
        if action == "rain":
            if position % size > 0:
                affected.append(position - 1)
            if position % size < size - 1:
                affected.append(position + 1)
        for index in affected:
            direction = -1 if action == "sun" and species[index] == "M" else 1
            values[index] = (values[index] + direction) % 3
    else:
        raise ValueError(f"Unknown action: {action}")
    return values


def progress(cells, targets):
    return sum(cells[index] == 2 for index in targets)


def generate_game(level, seed, profile="practice"):
    if level not in LEVELS:
        raise ValueError("Level must be between 1 and 6.")
    size, target_count, scrambles, moons, budget = LEVELS[level]
    rng = random.Random(f"moonflower-v1:{level}:{seed}")
    squares = size * size
    species = ["G"] * squares
    moon_positions = rng.sample(range(squares), moons)
    for index in moon_positions:
        species[index] = "M"
    targets = rng.sample(range(squares), target_count)
    if moons and not set(targets).intersection(moon_positions):
        targets[0] = moon_positions[0]
    targets = sorted(targets)
    solved = [rng.randrange(3) for _ in range(squares)]
    for index in targets:
        solved[index] = 2

    for _ in range(100):
        cells = list(solved)
        scramble = []
        for _ in range(scrambles):
            action = rng.choice(("sun", "rain") if level == 1 else ("sun", "rain", "wind"))
            position = rng.randrange(size if action == "wind" else squares)
            cells = apply_action(cells, species, size, action, position)
            scramble.append((action, position))
        if progress(cells, targets) < target_count:
            break
    else:
        raise RuntimeError("Could not produce a non-solved puzzle.")

    # Inversion is possible within the budget: growth takes two inverse turns,
    # while wind takes (size-1). Only exposed to the local test helper.
    inverse = []
    for action, position in reversed(scramble):
        inverse.extend([(action, position)] * (size - 1 if action == "wind" else 2))
    assert len(inverse) <= budget
    assert _run_actions(cells, species, size, inverse) == solved

    return {
        "version": VERSION,
        "level": level,
        "seed": seed,
        "profile": profile,
        "size": size,
        "species": species,
        "targets": targets,
        "cells": cells,
        "initial_cells": list(cells),
        "moves": [],
        "budget": budget,
        "outcome": "active",
        "created_at": utc_now(),
    }


def _run_actions(cells, species, size, actions):
    for action, position in actions:
        cells = apply_action(cells, species, size, action, position)
    return cells


def render(session, cells=None, turn=None, outcome=None):
    values = session["cells"] if cells is None else cells
    used = len(session["moves"]) if turn is None else turn
    status = session["outcome"] if outcome is None else outcome
    size = session["size"]
    targets = set(session["targets"])
    header = "       " + "   ".join(chr(ord("A") + column) for column in range(size))
    lines = [header]
    for row in range(size):
        chunks = []
        for col in range(size):
            index = row * size + col
            chunks.append(f"{session['species'][index]}{values[index]}{'*' if index in targets else ' '}")
        lines.append(f"   {row + 1}   " + " ".join(chunks))
    done = progress(values, targets)
    lines.extend([
        "",
        f"Targets blooming: {done}/{len(targets)} | Moves: {used}/{session['budget']} | Status: {status.upper()}",
        "Legend: G=garden plant, M=unfamiliar plant, 0=seed, 1=sprout, 2=bloom, *=target",
        "Goal: all * targets must bloom (2) at the same time. Other tiles do not matter.",
    ])
    if session["level"] >= 4:
        lines.append("A new species (M) has appeared. Its responses may surprise you.")
    if status == "active":
        lines.append("Actions: sun B2 | rain A1 | wind 2")
    if status == "won":
        lines.append("SUCCESS — the garden is blooming!")
    elif status == "lost":
        lines.append("OUT OF MOVES — reflect, then start a new seed.")
    return "\n".join(lines)


def public_state(session):
    size = session["size"]
    return {
        "level": session["level"],
        "seed": session["seed"],
        "profile": session["profile"],
        "size": size,
        "board": [
            {
                "cell": cell_name(i, size),
                "species": session["species"][i],
                "stage": session["cells"][i],
                "target": i in session["targets"],
            }
            for i in range(size * size)
        ],
        "targets_blooming": progress(session["cells"], session["targets"]),
        "targets_total": len(session["targets"]),
        "moves_used": len(session["moves"]),
        "move_budget": session["budget"],
        "status": session["outcome"],
        "available_actions": ["sun CELL", "rain CELL", "wind ROW"],
    }


def append_result(home, session):
    home.mkdir(parents=True, exist_ok=True)
    record = {
        "level": session["level"],
        "seed": session["seed"],
        "profile": session["profile"],
        "outcome": session["outcome"],
        "moves": len(session["moves"]),
        "budget": session["budget"],
        "targets_blooming": progress(session["cells"], session["targets"]),
        "targets_total": len(session["targets"]),
        "finished_at": utc_now(),
    }
    with (home / "results.jsonl").open("a", encoding="utf-8") as output:
        output.write(json.dumps(record) + "\n")


def start(args, home):
    previous = None
    if (home / "session.json").exists():
        previous = load_session(home)
    if previous and previous["outcome"] == "active" and not args.force:
        raise ValueError("A game is in progress. Finish it or pass --force to abandon it.")
    if previous and previous["outcome"] == "active" and args.force:
        previous["outcome"] = "abandoned"
        append_result(home, previous)
    session = generate_game(args.level, args.seed, args.profile)
    _save_json(home / "session.json", session)
    print(f"MOONFLOWER | level {args.level} | seed {args.seed} | {args.profile}")
    print(render(session))


def move(args, home):
    session = load_session(home)
    if session["outcome"] != "active":
        raise ValueError("This game has ended. Start a new game with 'moonflower start'.")
    action = args.command
    position = int(args.target) - 1 if action == "wind" else cell_index(args.target, session["size"])
    if action == "wind" and not 0 <= position < session["size"]:
        raise ValueError(f"Row must be between 1 and {session['size']}.")
    before = list(session["cells"])
    after = apply_action(before, session["species"], session["size"], action, position)
    session["cells"] = after
    session["moves"].append({
        "turn": len(session["moves"]) + 1,
        "action": action,
        "target": str(args.target).upper(),
        "before": before,
        "after": after,
    })
    if progress(after, session["targets"]) == len(session["targets"]):
        session["outcome"] = "won"
    elif len(session["moves"]) >= session["budget"]:
        session["outcome"] = "lost"
    _save_json(home / "session.json", session)
    if session["outcome"] != "active":
        append_result(home, session)
    print(f"TURN {len(session['moves'])}: {action.upper()} {str(args.target).upper()}")
    print(render(session))


def replay(args, home):
    session = load_session(home)
    turns = session["moves"]
    if args.last is not None:
        turns = turns[-args.last:] if args.last else []
    print(f"MOONFLOWER REPLAY | level {session['level']} | seed {session['seed']}")
    if not args.last or not turns:
        print("INITIAL BOARD")
        print(render(session, session["initial_cells"], turn=0, outcome="active"))
    for turn in turns:
        print(f"\nTURN {turn['turn']}: {turn['action'].upper()} {turn['target']}")
        print(render(session, turn["after"], turn=turn["turn"],
                     outcome=session["outcome"] if turn["turn"] == len(session["moves"]) else "active"))


def results(args, home):
    path = home / "results.jsonl"
    entries = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(json.loads(line))
    if args.json:
        print(json.dumps(entries, indent=2))
        return
    if not entries:
        print("No completed games yet.")
        return
    for profile in ("practice", "evaluation"):
        group = [item for item in entries if item["profile"] == profile and item["outcome"] != "abandoned"]
        if not group:
            continue
        wins = [item for item in group if item["outcome"] == "won"]
        average = sum(item["moves"] for item in wins) / len(wins) if wins else 0
        print(f"{profile.upper()}: {len(wins)}/{len(group)} won ({100 * len(wins) / len(group):.0f}%), average winning moves: {average:.1f}")
    abandoned = sum(item["outcome"] == "abandoned" for item in entries)
    if abandoned:
        print(f"Abandoned runs: {abandoned} (excluded from win rate)")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="moonflower",
        description="A slow, terminal-native puzzle game for agents learning through experience.",
        epilog="Use 'moonflower guide' for controls and workshop tips.",
    )
    parser.add_argument("--home", help="Directory for save state and results (default: .moonflower)")
    sub = parser.add_subparsers(dest="command", required=True)
    new = sub.add_parser("start", help="Start a seeded, solvable puzzle")
    new.add_argument("--level", type=int, choices=sorted(LEVELS), default=1)
    new.add_argument("--seed", type=int, default=11)
    new.add_argument("--profile", choices=("practice", "evaluation"), default="practice")
    new.add_argument("--force", action="store_true", help="Abandon current game")
    look = sub.add_parser("look", help="Show current board")
    look.add_argument("--json", action="store_true", help="Structured observation")
    for action in ("sun", "rain", "wind"):
        turn = sub.add_parser(action, help=f"Use {action} on a tile or row")
        turn.add_argument("target", help="A1 / B2 for sun/rain; 1 / 2 for wind")
    replay_cmd = sub.add_parser("replay", help="Review move-by-move changes")
    replay_cmd.add_argument("--last", type=int, default=None, help="Only show the last N turns")
    report = sub.add_parser("results", help="Aggregate completed games")
    report.add_argument("--json", action="store_true")
    sub.add_parser("guide", help="Show player-facing rules without hidden mechanics")

    args = parser.parse_args(argv)
    home = home_dir(args.home)
    try:
        if args.command == "start":
            start(args, home)
        elif args.command == "look":
            session = load_session(home)
            print(json.dumps(public_state(session), indent=2) if args.json else render(session))
        elif args.command in ("sun", "rain", "wind"):
            move(args, home)
        elif args.command == "replay":
            if args.last is not None and args.last < 0:
                raise ValueError("--last must be nonnegative")
            replay(args, home)
        elif args.command == "results":
            results(args, home)
        elif args.command == "guide":
            print("MOONFLOWER: Reach bloom stage (2) on every marked * tile simultaneously.\n"
                  "Plants have stages 0 (seed), 1 (sprout), and 2 (bloom).\n"
                  "Three actions: sun CELL, rain CELL, wind ROW. Each costs one turn.\n"
                  "The effects are intentionally undocumented; discover them by experimentation.\n"
                  "Use look, replay, and results to examine progress.\n"
                  "Levels 4–6 introduce unfamiliar M plants that may behave differently.\n"
                  "No timer. No undo. No need to write a bot or modify any game code.")
        return 0
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
