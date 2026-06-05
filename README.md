# 🔐 HashTools v2.0
> Ultimate Hash & Password Tool for Forensics, CTF, and Security Research

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-557C94?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A professional-grade command-line tool for **digital forensics**, **CTF competitions**, and **authorized penetration testing**. No external dependencies required for core features.

---

## ⚠️ Legal Disclaimer

> This tool is intended for **authorized security testing**, **forensics investigations**, **CTF competitions**, and **educational research only**.  
> Using this tool against systems or accounts you do not own or have explicit written permission to test is **illegal**.  
> The author is not responsible for any misuse.

---

## Features

| Module | Description |
|--------|-------------|
| `hash` | Hash any string with 15+ algorithms simultaneously |
| `crack` | Crack hashes via wordlist, rule-based mutations, or brute-force |
| `wordlist` | Generate and mutate professional wordlists |
| `identify` | Identify 30+ hash types with Hashcat/John modes |
| `analyze` | Analyze hash files — stats, duplicates, batch crack, reports |

### Supported Algorithms
`md5` · `md4` · `ntlm` · `sha1` · `sha224` · `sha256` · `sha384` · `sha512` · `sha3_256` · `sha3_512` · `sha3_224` · `sha3_384` · `ripemd160` · `blake2s` · `blake2b`

### Identified Hash Types (30+)
MD5, MD4, NTLM, SHA-1, SHA-224/256/384/512, SHA3, BLAKE2, RIPEMD-160, bcrypt, MD5-Crypt, SHA-256/512-Crypt, yescrypt, PHPass (WordPress), MySQL 3/4, LM:NTLM (pwdump), Apache MD5, LDAP SHA/SSHA, DES-Crypt, Cisco and more.

---

## Installation

```bash
git clone https://github.com/yourusername/hashtools.git
cd hashtools
chmod +x install.sh
sudo ./install.sh
```

**Manual install:**
```bash
git clone https://github.com/yourusername/hashtools.git
cd hashtools
pip3 install -r requirements.txt --break-system-packages
python3 hashtools.py --help
```

---

## Usage

### Hash a string
```bash
# Hash with all 15 algorithms at once
python3 hashtools.py hash "password123"

# Hash with specific algorithms
python3 hashtools.py hash "secret" --algo md5,sha256,ntlm

# Hash with a salt
python3 hashtools.py hash "password" --algo sha256 --salt "randomsalt" --out results.txt

# Pipe mode
echo "password" | python3 hashtools.py hash --stdin --algo sha256
```

### Crack a hash
```bash
# Auto-detect algorithm + crack with rockyou
python3 hashtools.py crack --hash 5f4dcc3b5aa765d61d8327deb882cf99 \
    --wordlist /usr/share/wordlists/rockyou.txt

# Crack with mutation rules applied to each word (~30x more candidates)
python3 hashtools.py crack --hash <hash> \
    --wordlist /usr/share/wordlists/rockyou.txt --rules

# Crack with known algorithm
python3 hashtools.py crack --hash <sha256_hash> --algo sha256 \
    --wordlist wordlist.txt

# Crack a salted hash
python3 hashtools.py crack --hash <hash> --wordlist rockyou.txt \
    --salt "abc123" --salt-pos post

# Brute-force (short passwords)
python3 hashtools.py crack --hash <hash> --brute --length 5 --chars alphanum

# Batch crack an entire hash file and save results
python3 hashtools.py crack --file hashes.txt \
    --wordlist /usr/share/wordlists/rockyou.txt --out cracked.txt
```

### Generate wordlists
```bash
# Mutate base words (leet speak, casing, suffixes, prefixes, reversals)
python3 hashtools.py wordlist --words admin root password --mutate -o custom.txt

# Mutate an existing wordlist
python3 hashtools.py wordlist --input rockyou.txt --mutate -o mutated.txt

# Brute-force wordlist (all 3-char alphanumeric combos)
python3 hashtools.py wordlist --brute --length 3 --chars alphanum -o bf.txt

# Combined: mutate + brute with length filter + stats
python3 hashtools.py wordlist --words admin --mutate --brute --length 3 \
    --min-len 4 --max-len 12 -o final.txt --stats
```

### Identify a hash
```bash
# Identify a hash type
python3 hashtools.py identify --hash 5f4dcc3b5aa765d61d8327deb882cf99

# Verbose output with Hashcat/John usage examples
python3 hashtools.py identify --hash '$2b$12$...' --verbose
```

### Analyze a hash file
```bash
# Stats and type breakdown
python3 hashtools.py analyze --file hashes.txt

# Analyze + try to crack all at once
python3 hashtools.py analyze --file hashes.txt \
    --wordlist /usr/share/wordlists/rockyou.txt

# Save full report
python3 hashtools.py analyze --file hashes.txt --report report.txt
python3 hashtools.py analyze --file hashes.txt --report report.json
```

---

## Chaining with other Kali tools

```bash
# Extract hashes from /etc/shadow and crack
sudo cat /etc/shadow | awk -F: '{print $2}' | grep -v '!' | grep -v '*' > shadow_hashes.txt
python3 hashtools.py analyze --file shadow_hashes.txt --wordlist /usr/share/wordlists/rockyou.txt

# Pipe output into hashtools
cat hashes.txt | xargs -I{} python3 hashtools.py identify --hash {}

# Use with grep to filter specific hash types
python3 hashtools.py analyze --file dump.txt --report report.json
```

---

## Mutation Rules

When using `--rules` or `--mutate`, each word gets ~30 transformations applied:

| Rule | Example (input: `admin`) |
|------|--------------------------|
| Lowercase | `admin` |
| Uppercase | `ADMIN` |
| Capitalize | `Admin` |
| Leet speak | `4dm1n` |
| Reversed | `nimda` |
| + numbers | `admin123`, `admin2024` |
| + symbols | `admin!`, `admin@`, `!admin` |
| Doubled | `adminadmin` |
| Capitalize + symbol | `Admin!`, `Admin123` |
| Leet + symbol | `4dm1n!` |

---

## File Formats

**Hash file (`hashes.txt`):** One hash per line
```
5f4dcc3b5aa765d61d8327deb882cf99
5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8
$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36lGo0hqRDCyS
```

**pwdump format:**
```
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

---

## Wordlist Resources (for Kali)

```bash
# RockYou (most popular, 14M passwords)
/usr/share/wordlists/rockyou.txt

# SecLists (install)
sudo apt install seclists
ls /usr/share/seclists/Passwords/

# Install all wordlists
sudo apt install wordlists
```

---

## Project Structure

```
hashtools/
├── hashtools.py          # Main CLI entry point
├── modules/
│   ├── __init__.py
│   ├── utils.py          # Shared utilities, algorithms, colors
│   ├── hasher.py         # Hash command
│   ├── cracker.py        # Crack command (wordlist + brute-force)
│   ├── wordlist.py       # Wordlist generation + mutations
│   ├── identifier.py     # Hash type identification (30+ types)
│   └── analyzer.py       # Hash file analysis + reporting
├── wordlists/            # Store custom wordlists here
├── reports/              # Output reports directory
├── tests/                # Unit tests
├── install.sh            # Automated Kali installer
├── requirements.txt
└── README.md
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

**Use responsibly. Only on systems you own or have written permission to test.**
