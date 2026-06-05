#!/usr/bin/env python3
"""Crack hashes via wordlist attack, rule-based mutations, or brute-force."""

import os
import sys
import string
import itertools
from modules.utils import ALGORITHMS, compute_hash, auto_detect_algos, Progress, Colors as C


# ── Mutation rules (like hashcat rules) ─────────────────────────────────────

LEET = str.maketrans("aAeEiIoOsStTbBgGqQ", "4433110055++886699")

def apply_rules(word: str):
    """Yield many mutations of a word."""
    yield word
    yield word.lower()
    yield word.upper()
    yield word.capitalize()
    yield word[::-1]
    yield word.translate(LEET)
    yield word + "1"
    yield word + "12"
    yield word + "123"
    yield word + "1234"
    yield word + "!"
    yield word + "@"
    yield word + "#"
    yield word + "!!"
    yield word + "123!"
    yield word + "2023"
    yield word + "2024"
    yield word + "2025"
    yield "!" + word
    yield word.capitalize() + "!"
    yield word.capitalize() + "1"
    yield word.capitalize() + "123"
    yield word.capitalize() + "2024"
    yield word.translate(LEET) + "!"
    yield word.translate(LEET) + "1"
    yield word + word
    yield word[0].upper() + word[1:] + "1"
    # double-char padding
    for c in "!@#$%":
        yield word + c
        yield c + word


# ── Charset map ──────────────────────────────────────────────────────────────

CHARSET_MAP = {
    "alpha":    string.ascii_lowercase,
    "alphanum": string.ascii_lowercase + string.digits,
    "num":      string.digits,
    "lower":    string.ascii_lowercase,
    "upper":    string.ascii_uppercase,
    "all":      string.ascii_letters + string.digits + string.punctuation,
}


# ── Core crack logic ─────────────────────────────────────────────────────────

def crack_one(target: str, algo: str, wordlist_path: str,
              use_rules: bool, salt: str, salt_pos: str) -> str | None:
    """Return the plaintext if found, else None."""
    fn      = ALGORITHMS[algo]
    prog    = Progress(f"{C.CYAN}{target[:20]}...{C.RESET}" if len(target) > 20 else f"{C.CYAN}{target}{C.RESET}")

    with open(wordlist_path, "r", errors="ignore") as f:
        for line in f:
            word = line.rstrip("\n")
            candidates = apply_rules(word) if use_rules else [word]
            for candidate in candidates:
                prog.tick()
                try:
                    digest = compute_hash(candidate, algo, salt, salt_pos)
                except Exception:
                    continue
                if digest == target:
                    prog.done()
                    return candidate

    prog.done()
    return None


def brute_force_one(target: str, algo: str, max_len: int,
                    charset: str, salt: str, salt_pos: str) -> str | None:
    """Brute-force a single hash up to max_len."""
    chars = CHARSET_MAP.get(charset, string.ascii_lowercase)
    prog  = Progress(f"Brute [{charset}] len 1-{max_len}")

    for length in range(1, max_len + 1):
        for combo in itertools.product(chars, repeat=length):
            word = "".join(combo)
            prog.tick()
            try:
                digest = compute_hash(word, algo, salt, salt_pos)
            except Exception:
                continue
            if digest == target:
                prog.done()
                return word

    prog.done()
    return None


# ── Command handler ──────────────────────────────────────────────────────────

def cmd_crack(args):
    salt     = getattr(args, "salt", "")
    salt_pos = getattr(args, "salt_pos", "post")
    out      = getattr(args, "out", None)
    results  = []

    # Collect hashes
    if args.hash:
        hashes = [args.hash.strip().lower()]
    else:
        if not os.path.exists(args.file):
            print(f"{C.RED}[!] Hash file not found: {args.file}{C.RESET}")
            return
        with open(args.file) as f:
            hashes = [line.strip().lower() for line in f if line.strip()]
        print(f"{C.BOLD}[+] Loaded {len(hashes):,} hashes from {args.file}{C.RESET}")

    # Validate wordlist if needed
    if not args.brute:
        if not args.wordlist:
            print(f"{C.RED}[!] Provide --wordlist or use --brute{C.RESET}")
            return
        if not os.path.exists(args.wordlist):
            print(f"{C.RED}[!] Wordlist not found: {args.wordlist}{C.RESET}")
            return
        wl_size = sum(1 for _ in open(args.wordlist, errors="ignore"))
        print(f"{C.BOLD}[+] Wordlist:{C.RESET} {args.wordlist} ({wl_size:,} words)")
        if args.rules:
            print(f"{C.YELLOW}[*] Rule mutations enabled (×~30 per word){C.RESET}")

    print()

    cracked = 0
    for target in hashes:
        if not target:
            continue

        # Resolve algorithm
        algo = args.algo
        if algo == "auto":
            candidates = auto_detect_algos(target)
            if not candidates:
                print(f"{C.RED}  [?] {target[:32]}  — cannot auto-detect algo, skipping{C.RESET}")
                continue
            algo = candidates[0]
            if len(candidates) > 1:
                print(f"{C.YELLOW}  [*] Multiple possible algos: {candidates} — trying {algo}{C.RESET}")

        if algo not in ALGORITHMS:
            print(f"{C.RED}  [!] Unsupported algorithm: {algo}{C.RESET}")
            continue

        print(f"{C.BOLD}  [>] Cracking:{C.RESET} {C.CYAN}{target}{C.RESET}  {C.DIM}[{algo.upper()}]{C.RESET}")

        plaintext = None

        if args.brute:
            plaintext = brute_force_one(target, algo, args.length,
                                        args.chars, salt, salt_pos)
        elif args.wordlist:
            plaintext = crack_one(target, algo, args.wordlist,
                                  args.rules, salt, salt_pos)

        if plaintext:
            print(f"  {C.GREEN}{C.BOLD}  [✓] CRACKED:{C.RESET}  {C.GREEN}{plaintext}{C.RESET}\n")
            results.append((target, algo, plaintext))
            cracked += 1
        else:
            print(f"  {C.RED}  [✗] Not found.{C.RESET}\n")
            results.append((target, algo, None))

    # Summary
    total = len([h for h in hashes if h])
    print(f"{C.BOLD}{'─'*60}{C.RESET}")
    print(f"{C.BOLD}[=] Results: {C.GREEN}{cracked} cracked{C.RESET} / {C.RED}{total - cracked} failed{C.RESET} / {total} total")
    print(f"{C.BOLD}{'─'*60}{C.RESET}\n")

    # Save output
    if out:
        with open(out, "w") as f:
            f.write(f"HashTools v2.0 - Crack Results\n{'='*50}\n\n")
            for h, algo, pt in results:
                status = pt if pt else "[NOT FOUND]"
                f.write(f"{h}  [{algo.upper()}]  =>  {status}\n")
            f.write(f"\nCracked: {cracked}/{total}\n")
        print(f"{C.GREEN}[✓] Results saved to {out}{C.RESET}\n")
