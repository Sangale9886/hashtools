#!/bin/bash
# ============================================================
#   HashTools v2.0 - Installer for Kali Linux
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "  ██╗  ██╗ █████╗ ███████╗██╗  ██╗████████╗ ██████╗  ██████╗ ██╗     ███████╗"
echo "  ██║  ██║██╔══██╗██╔════╝██║  ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝"
echo "  ███████║███████║███████╗███████║   ██║   ██║   ██║██║   ██║██║     ███████╗"
echo "  ██╔══██║██╔══██║╚════██║██╔══██║   ██║   ██║   ██║██║   ██║██║     ╚════██║"
echo "  ██║  ██║██║  ██║███████║██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗███████║"
echo "  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝"
echo -e "${RESET}${YELLOW}  Installer v2.0${RESET}"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] Not running as root. Some features may require sudo.${RESET}"
fi

# Check Python 3
echo -e "${CYAN}[*] Checking Python 3...${RESET}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python 3 not found. Installing...${RESET}"
    apt-get install -y python3 python3-pip
else
    PY_VER=$(python3 --version)
    echo -e "${GREEN}[✓] Found: ${PY_VER}${RESET}"
fi

# Install pip dependencies
echo -e "${CYAN}[*] Installing Python dependencies...${RESET}"
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
pip3 install -r requirements.txt 2>/dev/null || \
pip install -r requirements.txt --break-system-packages 2>/dev/null

echo -e "${GREEN}[✓] Dependencies installed${RESET}"

# Make executable
chmod +x hashtools.py
echo -e "${GREEN}[✓] hashtools.py is now executable${RESET}"

# Optional: install globally
echo ""
read -p "$(echo -e ${YELLOW})[?] Install globally as 'hashtools' command? [y/N]: $(echo -e ${RESET})" REPLY
if [[ $REPLY =~ ^[Yy]$ ]]; then
    INSTALL_PATH="/usr/local/bin/hashtools"
    cp hashtools.py "$INSTALL_PATH"
    chmod +x "$INSTALL_PATH"
    echo -e "${GREEN}[✓] Installed to ${INSTALL_PATH}${RESET}"
    echo -e "${GREEN}    You can now run: hashtools hash \"password\"${RESET}"
else
    echo -e "${YELLOW}[*] Skipping global install. Run with: python3 hashtools.py${RESET}"
fi

# Check for rockyou.txt
echo ""
echo -e "${CYAN}[*] Checking for rockyou.txt...${RESET}"
ROCKYOU_PATHS=(
    "/usr/share/wordlists/rockyou.txt"
    "/usr/share/wordlists/rockyou.txt.gz"
)
FOUND_ROCKYOU=false
for P in "${ROCKYOU_PATHS[@]}"; do
    if [ -f "$P" ]; then
        echo -e "${GREEN}[✓] Found: $P${RESET}"
        FOUND_ROCKYOU=true
        # Decompress if needed
        if [[ "$P" == *.gz ]]; then
            echo -e "${YELLOW}[*] Decompressing...${RESET}"
            gunzip "$P"
            echo -e "${GREEN}[✓] Decompressed to ${P%.gz}${RESET}"
        fi
        break
    fi
done
if [ "$FOUND_ROCKYOU" = false ]; then
    echo -e "${YELLOW}[!] rockyou.txt not found.${RESET}"
    echo -e "${YELLOW}    On Kali: sudo apt install wordlists && gunzip /usr/share/wordlists/rockyou.txt.gz${RESET}"
fi

echo ""
echo -e "${GREEN}${BOLD}[✓] HashTools v2.0 installation complete!${RESET}"
echo ""
echo -e "${CYAN}Quick start:${RESET}"
echo -e "  python3 hashtools.py hash \"password\""
echo -e "  python3 hashtools.py identify --hash 5f4dcc3b5aa765d61d8327deb882cf99"
echo -e "  python3 hashtools.py crack --hash <hash> --wordlist /usr/share/wordlists/rockyou.txt"
echo -e "  python3 hashtools.py wordlist --words admin root --mutate -o mywl.txt"
echo -e "  python3 hashtools.py analyze --file hashes.txt"
echo ""
