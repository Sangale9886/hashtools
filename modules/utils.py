#!/usr/bin/env python3
import sys, time, hashlib

class Colors:
    RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"
    CYAN="\033[96m"; MAGENTA="\033[95m"; BLUE="\033[94m"
    WHITE="\033[97m"; BOLD="\033[1m"; DIM="\033[2m"; RESET="\033[0m"

C = Colors

def _ntlm(data):
    return hashlib.new("md4", data.decode("utf-8").encode("utf-16-le")).hexdigest()

def _make(algo):
    def _h(data): return hashlib.new(algo, data).hexdigest()
    return _h

ALGORITHMS = {
    "md5":      lambda d: hashlib.md5(d).hexdigest(),
    "sha1":     lambda d: hashlib.sha1(d).hexdigest(),
    "sha256":   lambda d: hashlib.sha256(d).hexdigest(),
    "sha512":   lambda d: hashlib.sha512(d).hexdigest(),
    "sha3_256": _make("sha3_256"),
    "sha3_512": _make("sha3_512"),
    "blake2s":  lambda d: hashlib.blake2s(d).hexdigest(),
    "blake2b":  lambda d: hashlib.blake2b(d).hexdigest(),
    "ripemd160":_make("ripemd160"),
    "ntlm":     _ntlm,
    "md4":      _make("md4"),
}

LENGTH_TO_ALGO = {
    32:["md5","md4","ntlm"], 40:["sha1","ripemd160"],
    64:["sha256","sha3_256"], 128:["sha512","sha3_512","blake2b"],
}

def compute_hash(text, algo, salt="", salt_pos="post"):
    data=(salt+text if salt_pos=="pre" else text+salt).encode("utf-8")
    fn=ALGORITHMS.get(algo)
    if not fn: raise ValueError(f"Unknown: {algo}")
    return fn(data)

def auto_detect_algos(h):
    return LENGTH_TO_ALGO.get(len(h.strip()), [])

def banner():
    print(f"{C.CYAN}{C.BOLD}\n  HashTools v2.0\n{C.RESET}")

class Progress:
    def __init__(self, label=""):
        self.start=time.time(); self.count=0; self.label=label; self._last=0
    def tick(self, n=1):
        self.count+=n
        now=time.time()
        if now-self._last>=0.4:
            elapsed=now-self.start or 0.001
            sys.stdout.write(f"\r[~] {self.label} {self.count:,} tried ({self.count/elapsed:,.0f}/s)   ")
            sys.stdout.flush(); self._last=now
    def done(self):
        elapsed=time.time()-self.start or 0.001
        sys.stdout.write(f"\r[✓] Done: {self.count:,} in {elapsed:.1f}s\n")
        sys.stdout.flush()
