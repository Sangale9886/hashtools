#!/usr/bin/env python3
"""Hash a string with multiple algorithms."""

import sys
from modules.utils import ALGORITHMS, compute_hash, Colors as C


def cmd_hash(args):
    # Get input text
    if getattr(args, "stdin", False):
        text = sys.stdin.read().rstrip("\n")
    elif args.text:
        text = args.text
    else:
        print(f"{C.RED}[!] Provide text to hash or use --stdin{C.RESET}")
        return

    salt    = getattr(args, "salt", "")
    algo_in = args.algo.lower().strip()
    out     = getattr(args, "out", None)

    # Resolve algorithm list
    if algo_in == "all":
        algos = list(ALGORITHMS.keys())
    else:
        algos = [a.strip() for a in algo_in.split(",")]

    # Validate
    invalid = [a for a in algos if a not in ALGORITHMS]
    if invalid:
        print(f"{C.RED}[!] Unknown algorithm(s): {', '.join(invalid)}{C.RESET}")
        print(f"    Available: {', '.join(ALGORITHMS.keys())}")
        return

    # Print header
    salt_disp = f"  salt={C.MAGENTA}{salt}{C.RESET}" if salt else ""
    print(f"\n{C.BOLD}[+] Input:{C.RESET}  {C.CYAN}{text}{C.RESET}{salt_disp}\n")
    print(f"  {'ALGORITHM':<14}  {'DIGEST'}")
    print(f"  {'─'*14}  {'─'*70}")

    lines = []
    for algo in algos:
        try:
            digest = compute_hash(text, algo, salt)
            print(f"  {C.YELLOW}{algo.upper():<14}{C.RESET}  {digest}")
            lines.append(f"{algo.upper():<14}  {digest}")
        except Exception as e:
            print(f"  {C.RED}{algo.upper():<14}{C.RESET}  ERROR: {e}")

    print()

    if out:
        with open(out, "w") as f:
            f.write(f"Input: {text}\n")
            if salt:
                f.write(f"Salt:  {salt}\n")
            f.write("\n")
            for line in lines:
                f.write(line + "\n")
        print(f"{C.GREEN}[✓] Results saved to {out}{C.RESET}\n")
