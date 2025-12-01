#!/usr/bin/env python3

import os

def clear():
    cmd = 'cls' if os.name == 'nt' else 'clear'
    os.system(cmd)

def main():
    clear()
    payload = "{{ 7 * 7 }}"

    url = input("Enter url [example: https://google.com/{PAYLOAD}]\n> ")
    

if __name__ == '__main__':
    main()
