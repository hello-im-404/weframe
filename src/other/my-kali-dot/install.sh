#!/usr/bin/bash

RED='\033[1;31m'
NC='\033[0m'

echo -e "${RED}ATTENTION: This script will change the system!${NC}"
read -p "Did u make a backup? [y/n] " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Cancelled. GoodBye!${NC}"
    exit 1
fi

echo "Starting installation"

# secret/ 

mkdir -p ~/.config/404/
touch ~/.config/404/flag.txt
echo "hello:)" >> ~/.config/404/flag.txt

# linpeas.sh + winpeas.bat

sudo mv /usr/share/peass/linpeas/linpeas.sh ~/
sudo mv /usr/share/peass/winpeas/winPEAS.bat ~/

# packets

sudo apt update && sudo apt install -y neovim subfinder gimp nuclei screenfetch torbrowser-launcher timeshift git build-essential apt-utils cmake libfontconfig1 libglu1-mesa-dev libgtest-dev libspdlog-dev libboost-all-dev libncurses5-dev libgdbm-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev mesa-common-dev qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools libqt5websockets5 libqt5websockets5-dev qtdeclarative5-dev golang-go qtbase5-dev libqt5websockets5-dev python3-dev libboost-all-dev mingw-w64 nasm

# havoc

git clone https://github.com/HavocFramework/Havoc.git ~/

# sliver

curl https://sliver.sh/install|sudo bash

# seclists

git clone --depth 1 https://github.com/danielmiessler/SecLists.git ~/

# web-pentesting

go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
CGO_ENABLED=1 go install github.com/projectdiscovery/katana/cmd/katana@latest
sudo mv ~/go/bin/httpx /usr/bin/
sudo mv ~/go/bin/katana /usr/bin/

# uv(python venv)

curl -LsSf https://astral.sh/uv/install.sh | sh

# just pwndbg(install ida free/pro also) 

curl -qsL 'https://install.pwndbg.re' | sh -s -- -t pwndbg-gdb

# my nvim-dot 

git clone https://github.com/hello-im-404/nvim-dot.git ~/.config/nvim
rm -rf ~/.config/nvim/README.md
rm -rf ~/.config/nvim/screenshots

#  Hello, i'm error
# 4o_O4 4O4 4o4 404
