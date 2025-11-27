#!/usr/bin/bash

git add .
git commit -m "update"  
git branch -M main
if ! git remote | grep -q origin; then
    git remote add origin git@github.com:hello-im-404/my-kali-dot.git
else
    git remote set-url origin git@github.com:hello-im-404/my-kali-dot.git
fi
git push -u origin main
