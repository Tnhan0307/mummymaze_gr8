import os
import sys
import random
from statistics import mean

# Ensure project root is on sys.path (so `api.io...` imports work)
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.io.Lightning.maze.MazeGenerator import MazeGenerator


def win_cell(gen: MazeGenerator, exit_pos: dict, size: int):
    wx, wy = gen._exit_to_win_cell(exit_pos, size)
    if wx is None:
        return None
    return (int(wx), int(wy))


def validate_gate_key(gen: MazeGenerator, level: dict, size: int):
    """
    Returns:
      - None if no gate in level (not applicable)
      - True/False if gate exists (validity)
    Valid means:
      - key exists
      - when gate closed, target(win-cell) NOT reachable from start
      - key is reachable from start when gate closed
    """
    gate = level.get("gate")
    key = level.get("key")

    if not gate:
        return None  # N/A

    # Gate exists => key must exist for your intended puzzle
    if not key:
        return False

    try:
        start = (int(level["player"]["x"]), int(level["player"]["y"]))
        target = win_cell(gen, level.get("exit"), size)
        if target is None:
            return False

        gate_info = (int(gate["x"]), int(gate["y"]))
        key_pos = (int(key["x"]), int(key["y"]))
        walls = level.get("walls", [])

        reachable_closed = gen._reachable_set(start, walls, size, gate_info=gate_info, gate_open=False)

        choke_ok = (target not in reachable_closed)      # gate đóng => không tới win
        key_ok = (key_pos in reachable_closed)           # key nằm phía trước gate

        return bool(choke_ok and key_ok)

    except Exception:
        return False


def run_suite(N=50, sizes=(6, 8, 10), diffs=("easy", "medium", "hard"), seed=1337):
    random.seed(seed)

    gen = MazeGenerator()

    # stats[(diff, size)] = dict(...)
    stats = {}
    for d in diffs:
        for s in sizes:
            stats[(d, s)] = {
                "n": 0,
                "generated": 0,
                "solved": 0,
                "steps": [],
                "gate_present": 0,
                "gate_valid": 0,
                "gate_invalid": 0,
            }

    for d in diffs:
        for s in sizes:
            bucket = stats[(d, s)]
            for i in range(N):
                bucket["n"] += 1

                level = gen.generate_level(difficulty=d, maze_size=s)
                if not level:
                    continue
                bucket["generated"] += 1

                # Re-check solvability and compute steps
                path = gen._is_level_solvable(level, s)
                if path:
                    bucket["solved"] += 1
                    bucket["steps"].append(max(0, len(path) - 1))

                # Gate/key validity check
                gv = validate_gate_key(gen, level, s)
                if gv is None:
                    # no gate: do nothing
                    pass
                else:
                    bucket["gate_present"] += 1
                    if gv:
                        bucket["gate_valid"] += 1
                    else:
                        bucket["gate_invalid"] += 1

    # Print report
    print("=" * 72)
    print(f"GENERATOR HARNESS REPORT | N={N} per (diff,size) | seed={seed}")
    print("=" * 72)

    for d in diffs:
        print(f"\n--- Difficulty: {d} ---")
        for s in sizes:
            b = stats[(d, s)]
            gen_ok = b["generated"]
            solved = b["solved"]
            avg_steps = mean(b["steps"]) if b["steps"] else 0.0

            gate_p = b["gate_present"]
            gate_v = b["gate_valid"]
            gate_i = b["gate_invalid"]

            solved_rate = (solved / gen_ok * 100.0) if gen_ok else 0.0
            gate_valid_rate = (gate_v / gate_p * 100.0) if gate_p else 0.0

            print(f"Size {s}x{s}:")
            print(f"  Generated: {gen_ok}/{b['n']}")
            print(f"  Solved:    {solved}/{gen_ok}  ({solved_rate:.1f}%)")
            print(f"  Avg steps: {avg_steps:.2f}")
            print(f"  Gate present: {gate_p}/{gen_ok}")
            if gate_p:
                print(f"  Gate valid:   {gate_v}/{gate_p}  ({gate_valid_rate:.1f}%)")
                print(f"  Gate invalid: {gate_i}/{gate_p}")

    print("\nDone.")


if __name__ == "__main__":
    run_suite(
        N=50,                 # đổi số này nếu muốn nhanh/chậm
        sizes=(6, 8, 10),
        diffs=("easy", "medium", "hard"),
        seed=1337
    )
