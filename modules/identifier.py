#!/usr/bin/env python3
"""Identify hash types by pattern matching."""

import re
from modules.utils import Colors as C


# (regex, name, hashcat_mode, john_format, notes)
HASH_SIGNATURES = [
    # ── MD & SHA families ─────────────────────────────────────────────────
    (r"^[a-f0-9]{32}$",   "MD5",         0,    "raw-md5",    "Very common; used in legacy systems"),
    (r"^[a-f0-9]{32}$",   "MD4",         900,  "raw-md4",    "Used in older Windows NTLM"),
    (r"^[a-f0-9]{32}$",   "NTLM",        1000, "nt",         "Windows NT/LM hash"),
    (r"^[a-f0-9]{40}$",   "SHA-1",       100,  "raw-sha1",   "Common in older web apps"),
    (r"^[a-f0-9]{40}$",   "RIPEMD-160",  6000, "ripemd-160", "Cryptocurrency / PGP"),
    (r"^[a-f0-9]{56}$",   "SHA-224",     1300, "raw-sha224", "SHA-2 family"),
    (r"^[a-f0-9]{64}$",   "SHA-256",     1400, "raw-sha256", "Modern standard"),
    (r"^[a-f0-9]{64}$",   "SHA3-256",    17300,"raw-sha3-256","Newer SHA-3 family"),
    (r"^[a-f0-9]{64}$",   "BLAKE2s",     None, None,         "High-speed cryptographic hash"),
    (r"^[a-f0-9]{96}$",   "SHA-384",     10800,"raw-sha384", "SHA-2 family"),
    (r"^[a-f0-9]{128}$",  "SHA-512",     1700, "raw-sha512", "Strong; common in Linux shadow"),
    (r"^[a-f0-9]{128}$",  "SHA3-512",    17600,"raw-sha3-512","SHA-3 family"),
    (r"^[a-f0-9]{128}$",  "BLAKE2b",     None, None,         "High-speed cryptographic hash"),
    (r"^[a-f0-9]{128}$",  "Whirlpool",   6100, "whirlpool",  "ISO/IEC standard"),

    # ── Salted / formatted ────────────────────────────────────────────────
    (r"^\$1\$.{1,8}\$.{22}$",           "MD5-Crypt",       500,   "md5crypt",   "Linux /etc/shadow"),
    (r"^\$2[aby]\$.{56}$",              "bcrypt",          3200,  "bcrypt",     "Adaptive password hashing"),
    (r"^\$5\$.{0,16}\$.{43}$",          "SHA-256-Crypt",   7400,  "sha256crypt","Linux /etc/shadow"),
    (r"^\$6\$.{0,16}\$.{86}$",          "SHA-512-Crypt",   1800,  "sha512crypt","Linux /etc/shadow (default)"),
    (r"^\$y\$.{1,4}\$.{32}\$.{43}$",    "yescrypt",        None,  "yescrypt",   "Modern Linux shadow"),
    (r"^\$apr1\$.{1,8}\$.{22}$",        "Apache MD5-APR",  1600,  "md5crypt-apache","Apache htpasswd"),
    (r"^\$P\$[a-zA-Z0-9./]{31}$",       "PHPass (WordPress/phpBB)", 400, "phpass", "WordPress, phpBB3"),
    (r"^\$H\$[a-zA-Z0-9./]{31}$",       "PHPass (phpBB older)",400, "phpass",   "phpBB older"),
    (r"^\{SHA\}[A-Za-z0-9+/=]{28}$",    "SHA-1 Base64 (LDAP)",101, None,       "LDAP / OpenLDAP"),
    (r"^\{SSHA\}[A-Za-z0-9+/=]{40}$",   "Salted SHA-1 (LDAP)",111,None,        "LDAP salted SHA-1"),

    # ── Database / application specific ──────────────────────────────────
    (r"^\*[A-F0-9]{40}$",               "MySQL 4.1+ (SHA-1)", 300,"mysql-sha1", "MySQL authentication"),
    (r"^[a-f0-9]{16}$",                 "MySQL 3.x / Half-MD5",3200,None,       "Very old MySQL"),
    (r"^[a-zA-Z0-9./]{13}$",            "DES-Crypt",         1500,"descrypt",   "Classic Unix crypt"),
    (r"^[a-zA-Z0-9+/]{20}$",            "Cisco Type 7 / Base64",None,None,      "Cisco IOS"),
    (r"^\$cisco4\$",                     "Cisco Type 4",      None, None,       "Cisco IOS SHA-256 based"),
    (r"^[a-f0-9]{40}:[a-f0-9]{0,40}$",  "SHA-1 + Salt",      110,  "dynamic_26","Salted SHA-1 colon format"),
    (r"^[a-f0-9]{32}:[a-zA-Z0-9.]{0,40}$","MD5 + Salt",      10,   "dynamic_4","Salted MD5 colon format"),
    (r"^[a-f0-9]{32}:[0-9]{5}$",        "MD5 + Numeric Salt",10,   None,       "e.g. WebEdition CMS"),

    # ── Windows ───────────────────────────────────────────────────────────
    (r"^[a-f0-9]{32}:[a-f0-9]{32}$",    "LM:NTLM (pwdump)",  3000, "lm",       "Windows SAM dump format"),
    (r"^[a-zA-Z0-9+/]{16,}={0,2}$",     "Base64-encoded (possible)", None, None,"May be base64 wrapped hash"),

    # ── Tokens / checksums ────────────────────────────────────────────────
    (r"^[a-f0-9]{8}$",                  "CRC32 / Adler32",   11500,None,        "Checksum, not cryptographic"),
    (r"^[a-f0-9]{64}:[a-f0-9]{32,}$",   "SHA-256 + Salt",    1410, None,       "Salted SHA-256"),
]


def identify_hash(h: str, verbose: bool = False):
    h = h.strip()
    found = []
    for pattern, name, hc_mode, john_fmt, notes in HASH_SIGNATURES:
        if re.fullmatch(pattern, h, re.IGNORECASE):
            # avoid exact dupes
            if name not in [f[0] for f in found]:
                found.append((name, hc_mode, john_fmt, notes))

    return found


def cmd_identify(args):
    h       = args.hash.strip()
    verbose = getattr(args, "verbose", False)

    print(f"\n{C.BOLD}[+] Analyzing hash:{C.RESET}  {C.CYAN}{h}{C.RESET}")
    print(f"    Length: {len(h)} chars\n")

    results = identify_hash(h, verbose)

    if not results:
        print(f"  {C.RED}[?] Unknown or unsupported hash format{C.RESET}")
        print(f"  {C.DIM}    Tip: make sure the hash is hex-encoded and complete{C.RESET}\n")
        return

    print(f"  {'TYPE':<30}  {'HASHCAT':>8}  {'JOHN':<18}  NOTES")
    print(f"  {'─'*30}  {'─'*8}  {'─'*18}  {'─'*35}")

    for name, hc, john, notes in results:
        hc_str   = str(hc)   if hc   else "—"
        john_str = john      if john else "—"
        print(f"  {C.GREEN}{name:<30}{C.RESET}  "
              f"{C.YELLOW}{hc_str:>8}{C.RESET}  "
              f"{C.MAGENTA}{john_str:<18}{C.RESET}  "
              f"{C.DIM}{notes}{C.RESET}")

    print()
    if verbose:
        print(f"  {C.BOLD}Hashcat usage example:{C.RESET}")
        best = results[0]
        if best[1]:
            print(f"  {C.DIM}hashcat -m {best[1]} {h} wordlist.txt{C.RESET}")
        print(f"\n  {C.BOLD}John the Ripper example:{C.RESET}")
        if best[2]:
            print(f"  {C.DIM}john --format={best[2]} --wordlist=wordlist.txt hash.txt{C.RESET}")
        print()
