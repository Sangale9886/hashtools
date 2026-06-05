#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║              HashTools - Ultimate Hash & Password Tool       ║
║         Forensics | CTF | Security Research | Pentesting     ║
║                        Version 2.0                           ║
╚══════════════════════════════════════════════════════════════╝
"""

import argparse
import sys
import os

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))

from modules.hasher     import cmd_hash
from modules.cracker    import cmd_crack
from modules.wordlist   import cmd_wordlist
from modules.identifier import cmd_identify
from modules.analyzer   import cmd_analyze
from modules.utils      import banner, Colors as C


def main():
    banner()

    parser = argparse.ArgumentParser(
        prog="hashtools",
        description="HashTools v2.0 - Ultimate Hash & Forensics Tool",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"""
{C.CYAN}COMMANDS:{C.RESET}
  hash      Hash any string with 15+ algorithms
  crack     Crack hashes (wordlist, hybrid, brute-force)
  wordlist  Generate and mutate wordlists
  identify  Identify hash type from pattern
  analyze   Analyze a hash file (stats, duplicates, batch crack)

{C.CYAN}EXAMPLES:{C.RESET}
  hashtools.py hash "password" --algo all
  hashtools.py hash "secret"   --algo md5,sha256,ntlm
  hashtools.py crack --hash 5f4dcc3b5aa765d61d8327deb882cf99 --wordlist rockyou.txt
  hashtools.py crack --file hashes.txt --wordlist rockyou.txt --rules
  hashtools.py crack --hash <hash> --brute --length 5 --chars alphanum
  hashtools.py wordlist --words admin root --mutate --output wl.txt
  hashtools.py wordlist --words password --brute --length 4
  hashtools.py identify --hash '$2b$12$...'
  hashtools.py analyze  --file hashes.txt
        """
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # ── HASH ──────────────────────────────────────────────────
    p_hash = sub.add_parser("hash", help="Hash a string with multiple algorithms")
    p_hash.add_argument("text", nargs="?", help="String to hash (or use --stdin)")
    p_hash.add_argument("--algo", default="all",
                        help="Algorithms: all | md5,sha1,sha256,sha512,ntlm,sha3_256,... (comma-separated)")
    p_hash.add_argument("--salt", default="", help="Optional salt prepended to input")
    p_hash.add_argument("--stdin", action="store_true", help="Read input from stdin (pipe mode)")
    p_hash.add_argument("--out",   help="Save results to file")

    # ── CRACK ─────────────────────────────────────────────────
    p_crack = sub.add_parser("crack", help="Crack hashes via wordlist or brute-force")
    src = p_crack.add_mutually_exclusive_group(required=True)
    src.add_argument("--hash",  metavar="HASH",  help="Single hash to crack")
    src.add_argument("--file",  metavar="FILE",  help="File containing hashes (one per line)")
    p_crack.add_argument("--wordlist", metavar="FILE", help="Wordlist file path")
    p_crack.add_argument("--algo", default="auto",
                         choices=["auto","md5","sha1","sha256","sha512","ntlm",
                                  "sha3_256","sha3_512","sha224","sha384",
                                  "ripemd160","blake2b","blake2s"],
                         help="Hash algorithm (default: auto-detect)")
    p_crack.add_argument("--rules",  action="store_true", help="Apply mutation rules to each word")
    p_crack.add_argument("--salt",   default="", help="Salt to append/prepend when hashing")
    p_crack.add_argument("--salt-pos", choices=["pre","post"], default="post",
                         help="Salt position (default: post)")
    p_crack.add_argument("--brute",  action="store_true", help="Enable brute-force mode")
    p_crack.add_argument("--length", type=int, default=4, help="Max brute-force length (default: 4)")
    p_crack.add_argument("--chars",  default="alphanum",
                         choices=["alpha","alphanum","num","lower","upper","all"],
                         help="Charset for brute-force")
    p_crack.add_argument("--out",    help="Save cracked results to file")

    # ── WORDLIST ──────────────────────────────────────────────
    p_wl = sub.add_parser("wordlist", help="Generate and mutate wordlists")
    p_wl.add_argument("--words",  nargs="+", help="Base words to mutate")
    p_wl.add_argument("--input",  help="Input wordlist to mutate")
    p_wl.add_argument("--mutate", action="store_true", help="Apply all mutation rules")
    p_wl.add_argument("--brute",  action="store_true", help="Add brute-force combos")
    p_wl.add_argument("--length", type=int, default=4, help="Max brute-force length (default: 4)")
    p_wl.add_argument("--chars",  default="alpha",
                       choices=["alpha","alphanum","num","all"],
                       help="Brute-force charset")
    p_wl.add_argument("--min-len", type=int, default=1, help="Minimum word length filter")
    p_wl.add_argument("--max-len", type=int, default=0, help="Maximum word length filter (0=off)")
    p_wl.add_argument("-o","--output", default="wordlist.txt", help="Output file")
    p_wl.add_argument("--stats",  action="store_true", help="Show wordlist stats after generation")

    # ── IDENTIFY ──────────────────────────────────────────────
    p_id = sub.add_parser("identify", help="Identify hash type")
    p_id.add_argument("--hash", required=True, metavar="HASH", help="Hash to identify")
    p_id.add_argument("--verbose", action="store_true", help="Show confidence scores")

    # ── ANALYZE ───────────────────────────────────────────────
    p_an = sub.add_parser("analyze", help="Analyze a hash file")
    p_an.add_argument("--file", required=True, help="Hash file to analyze")
    p_an.add_argument("--wordlist", help="Optional: try to crack while analyzing")
    p_an.add_argument("--report", help="Save HTML/TXT report to file")

    args = parser.parse_args()

    if   args.command == "hash":     cmd_hash(args)
    elif args.command == "crack":    cmd_crack(args)
    elif args.command == "wordlist": cmd_wordlist(args)
    elif args.command == "identify": cmd_identify(args)
    elif args.command == "analyze":  cmd_analyze(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
