"""Create an independent player workspace for the Copilot CLI workshop."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


PROMPT = """# Start here: Moonflower agent workshop

You are playing an unfamiliar, slow, turn-based terminal puzzle called Moonflower.
Your role is to PLAY the game, not build a solver or modify any game code.

Before playing, load your /moonflower-player skill and read the rules available via
moonflower guide. Interact only with moonflower start, moonflower look,
moonflower sun, moonflower rain, moonflower wind, moonflower replay, and
moonflower results. You may edit your own skill markdown **between games**.

Do not inspect the game's source or installed Python package, run a debugger,
search the internet for rules, or write scripts to calculate game solutions.

Begin with level 1 seed 11. Each time you choose a move, briefly record your
prediction of the result and then compare it to what actually happened.
After a game, reflect and improve your SKILL.md only with evidence-backed insights.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", help="New independent player directory")
    parser.add_argument("--force", action="store_true", help="Overwrite the existing starter skill")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    src = root / "skills" / "garden-player" / "SKILL.md"
    dest = Path(args.workspace).expanduser().resolve()
    if dest == root or root in dest.parents:
        parser.error("Choose a workspace outside the Moonflower source repository.")
    skill = dest / ".github" / "skills" / "moonflower-player" / "SKILL.md"
    if skill.exists() and not args.force:
        parser.error(f"Skill already exists at {skill}; refusing to reset learning without --force.")
    skill.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, skill)
    prompt = dest / "START_HERE.md"
    if not prompt.exists() or args.force:
        prompt.write_text(PROMPT, encoding="utf-8")
    print(f"Player workspace: {dest}")
    print(f"Skill: {skill}")
    print("Next: cd into this workspace, launch 'copilot', and follow START_HERE.md.")
    print("For independent sessions, set MOONFLOWER_HOME in each player's environment.")


if __name__ == "__main__":
    main()
