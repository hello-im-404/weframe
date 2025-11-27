#!/usr/bin/env python3

import hashlib
import base64

def main():
    hash_type = input("Hello, enter hash: MD5 | SHA224 | SHA512 | SHA384 | SHA256 | BASE64\n> ").lower()
    hash_value = input("Enter hash\n> ")
    wordlist_choice = input("Choice the path\n0) Default(/usr/share/wordlists/rockyou.txt)\n1) Custom\n> ")

    if wordlist_choice == "0":
        wordlist_path = "/usr/share/wordlists/rockyou.txt"
    elif wordlist_choice == "1":
        wordlist_path = input("Enter path to wordlist\n> ")
    else:
        print("Invalid choice!")
        return -1

    try:
        with open(wordlist_path, 'r', encoding='latin-1') as file:
            wordlist = file.read()
        lists = wordlist.splitlines()
    except FileNotFoundError:
        print(f"Error: File '{wordlist_path}' not found!")
        return -1
    except Exception as e:
        print(f"Error reading file: {e}")
        return -1

    print(f"Starting hash cracking with {len(lists)} words...")
    
    found = False
    for word in lists:
        if hash_type == "md5":
            hash_object = hashlib.md5(word.encode('utf-8'))
            hashed = hash_object.hexdigest()
            if hash_value == hashed:
                print(f"Hash found: {word}")
                found = True
                break
        elif hash_type == "sha224":
            hash_object = hashlib.sha224(word.encode('utf-8'))
            hashed = hash_object.hexdigest()
            if hash_value == hashed:
                print(f"Hash found: {word}")
                found = True
                break
        elif hash_type == "sha512":
            hash_object = hashlib.sha512(word.encode('utf-8'))
            hashed = hash_object.hexdigest()
            if hash_value == hashed:
                print(f"Hash found: {word}")
                found = True
                break
        elif hash_type == "sha384":
            hash_object = hashlib.sha384(word.encode('utf-8'))
            hashed = hash_object.hexdigest()
            if hash_value == hashed:
                print(f"Hash found: {word}")
                found = True
                break
        elif hash_type == "sha256":
            hash_object = hashlib.sha256(word.encode('utf-8'))
            hashed = hash_object.hexdigest()
            if hash_value == hashed:
                print(f"Hash found: {word}")
                found = True
                break
        elif hash_type == "base64":
            try:
                encoded = base64.b64encode(word.encode('utf-8')).decode('utf-8')
                if hash_value == encoded:
                    print(f"Base64 found: {word}")
                    found = True
                    break
            except Exception as e:
                continue 
        else:
            print("Invalid hash type!")
            return -1

    if not found:
        print("Password not found in wordlist!")

if __name__ == "__main__":
    main()
