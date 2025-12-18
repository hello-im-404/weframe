#!/usr/bin/bash

git add .
git commit -m "update"  
git branch -M master
if ! git remote | grep -q origin; then
    git remote add origin git@github.com:hello-im-404/nvim-dot.git
else
    git remote set-url origin git@github.com:hello-im-404/nvim-dot.git
fi
git push -u origin master
