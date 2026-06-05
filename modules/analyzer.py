#!/usr/bin/env python3
"""Analyze hash files: stats, duplicates, type breakdown, batch crack."""

import os
import re
import json
from collections import Counter
from modules.utils import Colors as C
from modules.identifier import identify_hash
from modules.cracker import crack_one, auto_detect_algos


def cmd_analyze(args):
    path    = args.file
    wordlist = getattr(args, "wordlist", None)
    report  = getattr(args, "report", None)

    if not os.path.exists(path):
        print(f"{C.RED}[!] File not found: {path}{C.RESET}")
        return

    with open(path, "r", errors="ignore") as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    total     = len(raw_lines)
    unique    = len(set(raw_lines))
    dupes     = total - unique

    print(f"\n{C.BOLD}[+] Analyzing:{C.RESET} {path}")
    print(f"    Total lines : {total:,}")
    print(f"    Unique      : {unique:,}")
    print(f"    Duplicates  : {dupes:,}\n")

    # Type breakdown
    type_counter = Counter()
    typed_hashes = {}   # type -> [hashes]

    for h in set(raw_lines):
        results = identify_hash(h)
        if results:
            t = results[0][0]
        else:
            t = f"Unknown (len={len(h)})"
        type_counter[t] += 1
        typed_hashes.setdefault(t, []).append(h)

    print(f"  {'HASH TYPE':<35}  {'COUNT':>6}  {'HASHCAT':>8}")
    print(f"  {'─'*35}  {'─'*6}  {'─'*8}")

    from modules.identifier import HASH_SIGNATURES
    for htype, count in type_counter.most_common():
        hc = "—"
        for _, name, hc_mode, _, _ in HASH_SIGNATURES:
            if name == htype and hc_mode:
                hc = str(hc_mode)
                break
        print(f"  {C.YELLOW}{htype:<35}{C.RESET}  {count:>6}  {C.CYAN}{hc:>8}{C.RESET}")

    print()

    # Optional batch crack
    cracked_map = {}
    if wordlist:
        if not os.path.exists(wordlist):
            print(f"{C.RED}[!] Wordlist not found: {wordlist}{C.RESET}")
        else:
            print(f"{C.BOLD}[+] Batch cracking with:{C.RESET} {wordlist}\n")
            for h in set(raw_lines):
                algos = auto_detect_algos(h)
                if not algos:
                    continue
                algo = algos[0]
                result = crack_one(h, algo, wordlist, False, "", "post")
                if result:
                    cracked_map[h] = result
                    print(f"  {C.GREEN}[✓]{C.RESET} {h[:32]}  =>  {C.GREEN}{result}{C.RESET}")

            print(f"\n  Cracked {len(cracked_map)}/{unique} hashes.\n")

    # Save report
    if report:
        ext = os.path.splitext(report)[1].lower()
        if ext == ".json":
            data = {
                "file": path,
                "total": total,
                "unique": unique,
                "duplicates": dupes,
                "type_breakdown": dict(type_counter),
                "cracked": cracked_map,
            }
            with open(report, "w") as f:
                json.dump(data, f, indent=2)
        else:
            with open(report, "w") as f:
                f.write(f"HashTools v2.0 - Analysis Report\n{'='*50}\n\n")
                f.write(f"File       : {path}\n")
                f.write(f"Total      : {total}\n")
                f.write(f"Unique     : {unique}\n")
                f.write(f"Duplicates : {dupes}\n\n")
                f.write(f"Type Breakdown:\n{'-'*40}\n")
                for htype, count in type_counter.most_common():
                    f.write(f"  {htype:<35}  {count}\n")
                if cracked_map:
                    f.write(f"\nCracked Hashes:\n{'-'*40}\n")
                    for h, pt in cracked_map.items():
                        f.write(f"  {h}  =>  {pt}\n")
        print(f"{C.GREEN}[✓] Report saved to {report}{C.RESET}\n")
