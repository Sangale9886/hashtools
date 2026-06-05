#!/usr/bin/env python3
"""Generate and mutate wordlists."""

import os
import string
import itertools
from modules.utils import Colors as C


LEET = str.maketrans("aAeEiIoOsStTbBgGqQ", "4433110055++886699")

SUFFIXES = [
    "1","2","12","21","123","1234","12345",
    "!","!!","@","#","$","!@#",
    "2020","2021","2022","2023","2024","2025",
    "01","02","007","99","00",
    "123!","1!","pass","pw",
]

PREFIXES = ["!", "@", "the", "my", "i", "1", "0"]

CHARSET_MAP = {
    "alpha":    string.ascii_lowercase,
    "alphanum": string.ascii_lowercase + string.digits,
    "num":      string.digits,
    "all":      string.ascii_letters + string.digits + string.punctuation,
}


def mutate(word: str):
    results = set()

    # Base transforms
    results.add(word)
    results.add(word.lower())
    results.add(word.upper())
    results.add(word.capitalize())
    results.add(word.swapcase())
    results.add(word[::-1])
    results.add(word.translate(LEET))
    results.add(word.translate(LEET).capitalize())

    # Suffixes
    for s in SUFFIXES:
        results.add(word + s)
        results.add(word.capitalize() + s)
        results.add(word.lower() + s)
        results.add(word.translate(LEET) + s)

    # Prefixes
    for p in PREFIXES:
        results.add(p + word)
        results.add(p + word.capitalize())

    # Doubled
    results.add(word + word)
    results.add(word.capitalize() + word.lower())

    # Title / toggle
    results.add(word.title())

    # Truncations
    if len(word) > 3:
        results.add(word[:-1])
        results.add(word[1:])

    return results


def generate_wordlist(base_words, input_file, mutate_flag,
                      brute, brute_len, brute_chars,
                      min_len, max_len, output_file):

    words = set()

    # Load from input file
    if input_file:
        if not os.path.exists(input_file):
            print(f"{C.RED}[!] Input file not found: {input_file}{C.RESET}")
            return
        with open(input_file, "r", errors="ignore") as f:
            for line in f:
                w = line.rstrip("\n")
                if w:
                    words.add(w)
                    if mutate_flag:
                        words.update(mutate(w))
        print(f"{C.YELLOW}[*] Loaded {len(words):,} words from {input_file}{C.RESET}")

    # Add base words
    if base_words:
        for w in base_words:
            words.add(w)
            if mutate_flag:
                words.update(mutate(w))

    # Brute-force combinations
    if brute:
        charset = CHARSET_MAP.get(brute_chars, string.ascii_lowercase)
        print(f"{C.YELLOW}[*] Generating brute-force combos (len 1-{brute_len}, charset={brute_chars})...{C.RESET}")
        count = 0
        for length in range(1, brute_len + 1):
            for combo in itertools.product(charset, repeat=length):
                words.add("".join(combo))
                count += 1
                if count % 500000 == 0:
                    print(f"  {C.DIM}Generated {count:,} combos...{C.RESET}", end="\r")
        print(f"  {C.DIM}Generated {count:,} combos.       {C.RESET}")

    # Length filter
    if min_len > 1:
        words = {w for w in words if len(w) >= min_len}
    if max_len > 0:
        words = {w for w in words if len(w) <= max_len}

    # Write output
    with open(output_file, "w") as f:
        for w in sorted(words):
            f.write(w + "\n")

    print(f"\n  {C.GREEN}{C.BOLD}[✓] Generated {len(words):,} unique words → {output_file}{C.RESET}\n")
    return len(words)


def cmd_wordlist(args):
    base  = args.words or []
    infile = getattr(args, "input", None)
    do_mut = getattr(args, "mutate", False)
    brute  = getattr(args, "brute", False)
    blen   = getattr(args, "length", 4)
    bchars = getattr(args, "chars", "alpha")
    minl   = getattr(args, "min_len", 1)
    maxl   = getattr(args, "max_len", 0)
    out    = getattr(args, "output", "wordlist.txt")
    stats  = getattr(args, "stats", False)

    if not base and not infile and not brute:
        print(f"{C.RED}[!] Provide --words, --input, or --brute{C.RESET}")
        return

    if base:
        print(f"{C.BOLD}[+] Base words:{C.RESET} {', '.join(base)}")
    if do_mut:
        print(f"{C.YELLOW}[*] Mutations enabled (leet, suffixes, prefixes, casing, reversals){C.RESET}")

    count = generate_wordlist(base, infile, do_mut, brute, blen, bchars, minl, maxl, out)

    if stats and count:
        print(f"{C.BOLD}[=] Stats:{C.RESET}")
        print(f"  Total unique words : {count:,}")
        print(f"  Output file        : {out}")
        size = os.path.getsize(out)
        print(f"  File size          : {size:,} bytes ({size/1024:.1f} KB)\n")
