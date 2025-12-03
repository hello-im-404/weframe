# Reference - https://github.com/coffinxp/loxs
# There should be a license here, but I'd rather talk about the script.
# I'll explain quickly (I promise). It's written in Python 3, using a minimal number of libraries.
# More vulnerabilities will be added in the future (as I learn about them)
# You can try to read the source code, I wish you good luck 
#
# Oh yeah, I forgot to remind you. r31v14n and hello-im-404 are the same person.

version = "1.0.1"

import requests
import os
import pyfiglet
from urllib.parse import urlparse, quote
import threading
import time 
import random
from queue import Queue

User_Agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15.7; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Mozilla/5.0 (X11; Linux i686; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.2; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/142.0.3595.53",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/142.0.3595.53",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 OPR/123.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 OPR/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/123.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/123.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Vivaldi/7.6.3797.63",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Vivaldi/7.6.3797.63",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_7_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Vivaldi/7.6.3797.63",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Vivaldi/7.6.3797.63",
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Vivaldi/7.6.3797.63",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 YaBrowser/25.8.5.890 Yowser/2.5 Safari/537.36"
]

def clear():
    cmd = 'cls' if os.name == 'nt' else 'clear'
    os.system(cmd)

def banner():
    ascii_banner = pyfiglet.figlet_format("r31 vuln scanner")
    print(ascii_banner)
    print(""" 
========================================================

        creator: https://github.com/hello-im-404
            version: {}
    
========================================================
    """.format(version))

def word_list(attack_type):
    default_wordlists = {
        '1': 'wordlists/xss_default.txt',  # XSS
        '2': 'wordlists/sqli_default.txt', # SQLi
        '3': 'wordlists/lfi_default.txt'   # LFI
    }
    
    attack_names = {
        '1': 'XSS',
        '2': 'SQLi', 
        '3': 'LFI'
    }

    attack_name = attack_names.get(attack_type, 'UNKNOWN')
    default_path = default_wordlists.get(attack_type)

    print(f"\n=== Wordlist selection for {attack_name} ===")
    choice = input("Use default wordlist? [Y/n]: ").strip().lower()

    if choice == '' or choice == 'y':
        print(f"Using default {attack_name} wordlist: {default_path}")
        return default_path

    wordlist_path = input("Enter path to custom wordlist\n> ").strip()
    if os.path.isfile(wordlist_path):
        print(f"Using custom {attack_name} wordlist: {wordlist_path}")
        return wordlist_path
    else:
        print(f"Custom wordlist not found: {wordlist_path}")
        if default_path and os.path.isfile(default_path):
            print(f"Falling back to default {attack_name} wordlist: {default_path}")
            return default_path
        else:
            print(f"Default wordlist also not found: {default_path}. Returning provided path (may be invalid).")
            return wordlist_path

def get_url(attack_choice):
    print("Enter url to attack. example: ")
    if attack_choice == '1': # XSS
        url = input("example: [https://example.com/search?q=test] or [https://example.com/search?q={PAYLOAD}]\n> ").strip()
    elif attack_choice == '2': # SQLi
        url = input("example: [https://example.com/search?id=1] or [https://example.com/search?id={PAYLOAD}]\n> ").strip()
    elif attack_choice == '3': # LFI
        url = input("example: [https://example.com/?file=index.html] or [https://example.com/?file={PAYLOAD}]\n> ").strip()
    else:
        return None
    
    # If user didn't specify {PAYLOAD}, add it appropriately
    if '{PAYLOAD}' not in url:
        if '?' in url:
            # If there are parameters
            if '=' in url:
                if url.endswith('='):
                    url += '{PAYLOAD}'
                else:
                    url += '{PAYLOAD}'
            else:
                # If there's ? but no =, add parameter
                url += '={PAYLOAD}'
        else:
            # If no parameters, add as path
            url += '/{PAYLOAD}' if not url.endswith('/') else '{PAYLOAD}'
    
    return url

def get_threads_count():
    try:
        threads = int(input("Enter number of threads (1-50, default 10): ").strip() or 10)
        return max(1, min(50, threads))  # Limit between 1 and 50
    except ValueError:
        print("Invalid input, using 10 threads")
        return 10

def filter_vulnerable_only():
    """Ask user if they want to see only vulnerable results"""
    choice = input("\nShow only vulnerable results? [Y/n]: ").strip().lower()
    return choice == '' or choice == 'y'

def isalive(url, timeout=8):
    if not url:
        return False
    
    # Remove {PAYLOAD} for connectivity check
    test_url = url.replace('{PAYLOAD}', 'test')
    
    parsed = urlparse(test_url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        print("Invalid URL, add to URL https:// or http://")
        return False

    try:
        headers = {'User-Agent': random.choice(User_Agents)}
        rget = requests.get(test_url, headers=headers, timeout=timeout, allow_redirects=True)
        print(f"Server responded with status code: {rget.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Server didn't respond: {e}")
        return False

def load_payloads(wordlist_path):
    """Load payloads from wordlist file"""
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            payloads = [line.strip() for line in f if line.strip()]
        return payloads
    except Exception as e:
        print(f"Error loading wordlist: {e}")
        return []

def get_random_user_agent():
    return random.choice(User_Agents)

#################################### ATTACK WORKERS

def xss_worker(queue, url, results, timeout=8, show_only_vulnerable=False):
    while True:
        payload = queue.get()
        if payload is None:
            queue.task_done()
            break
            
        try:
            target_url = url.replace('{PAYLOAD}', quote(payload))
            headers = {'User-Agent': get_random_user_agent()}
            
            response = requests.get(target_url, headers=headers, timeout=timeout, allow_redirects=True)
            
            # Simple detection - check if payload is reflected in response
            if payload in response.text:
                result = f"[VULNERABLE] XSS found - Payload: {payload} - URL: {target_url} - Status: {response.status_code}"
                results.append(result)
                print(f"\033[92m{result}\033[0m")  # Green color for vulnerabilities
            else:
                if not show_only_vulnerable:
                    print(f"[TESTED] Payload: {payload} - Status: {response.status_code}")
                
        except Exception as e:
            if not show_only_vulnerable:
                print(f"[ERROR] Payload: {payload} - Error: {e}")
        
        queue.task_done()

def sqli_worker(queue, url, results, timeout=8, show_only_vulnerable=False):
    while True:
        payload = queue.get()
        if payload is None:
            queue.task_done()
            break
            
        try:
            target_url = url.replace('{PAYLOAD}', quote(payload))
            headers = {'User-Agent': get_random_user_agent()}
            
            response = requests.get(target_url, headers=headers, timeout=timeout, allow_redirects=True)
            
            # Simple SQLi detection - common error messages
            sql_errors = [
                "sql syntax", "mysql_fetch", "warning: mysql", 
                "unclosed quotation mark", "you have an error in your sql syntax",
                "microsoft odbc", "ora-", "postgresql", "sqlite_exception"
            ]
            
            response_lower = response.text.lower()
            if any(error in response_lower for error in sql_errors):
                result = f"[VULNERABLE] SQLi found - Payload: {payload} - URL: {target_url} - Status: {response.status_code}"
                results.append(result)
                print(f"\033[92m{result}\033[0m")
            else:
                if not show_only_vulnerable:
                    print(f"[TESTED] Payload: {payload} - Status: {response.status_code}")
                
        except Exception as e:
            if not show_only_vulnerable:
                print(f"[ERROR] Payload: {payload} - Error: {e}")
        
        queue.task_done()

def lfi_worker(queue, url, results, timeout=8, show_only_vulnerable=False):
    while True:
        payload = queue.get()
        if payload is None:
            queue.task_done()
            break
            
        try:
            target_url = url.replace('{PAYLOAD}', quote(payload))
            headers = {'User-Agent': get_random_user_agent()}
            
            response = requests.get(target_url, headers=headers, timeout=timeout, allow_redirects=True)
            
            # Simple LFI detection - common file contents
            lfi_indicators = [
                "root:", "bin/bash", "etc/passwd", "boot.ini", "windows/system32",
                "<?php", "index.php", "DOCTYPE html", "html public"
            ]
            
            response_text = response.text
            # Check if we got a successful response and common file indicators
            if (response.status_code == 200 and 
                len(response_text) > 100 and  # Basic filter for error pages
                any(indicator in response_text for indicator in lfi_indicators)):
                
                result = f"[VULNERABLE] LFI found - Payload: {payload} - URL: {target_url} - Status: {response.status_code}"
                results.append(result)
                print(f"\033[92m{result}\033[0m")
            else:
                if not show_only_vulnerable:
                    print(f"[TESTED] Payload: {payload} - Status: {response.status_code}")
                
        except Exception as e:
            if not show_only_vulnerable:
                print(f"[ERROR] Payload: {payload} - Error: {e}")
        
        queue.task_done()

#################################### ATTACK MANAGERS

def xss_attack(url, wordlist_path, thread_count=10, show_only_vulnerable=False):
    print(f"\nStarting XSS attack on: {url}")
    print(f"Using wordlist: {wordlist_path}")
    print(f"Threads: {thread_count}")
    if show_only_vulnerable:
        print("Showing only VULNERABLE results")
    
    # Check if wordlist exists
    if not os.path.isfile(wordlist_path):
        print(f"Error: Wordlist not found: {wordlist_path}")
        return
    
    payloads = load_payloads(wordlist_path)
    if not payloads:
        print("No payloads loaded. Exiting.")
        return
    
    print(f"Loaded {len(payloads)} payloads")
    
    queue = Queue()
    results = []
    threads = []
    
    # Start worker threads
    for _ in range(thread_count):
        t = threading.Thread(target=xss_worker, args=(queue, url, results, 8, show_only_vulnerable))
        t.daemon = True
        t.start()
        threads.append(t)
    
    # Add payloads to queue
    for payload in payloads:
        queue.put(payload)
    
    # Add poison pills to stop workers
    for _ in range(thread_count):
        queue.put(None)
    
    print("Attack in progress... Press Ctrl+C to stop\n")
    
    try:
        queue.join()
    except KeyboardInterrupt:
        print("\nAttack interrupted by user")
    
    print(f"\nXSS scan completed. Found {len(results)} potential vulnerabilities.")
    for result in results:
        print(result)

def sqli_attack(url, wordlist_path, thread_count=10, show_only_vulnerable=False):
    print(f"\nStarting SQL injection attack on: {url}")
    print(f"Using wordlist: {wordlist_path}")
    print(f"Threads: {thread_count}")
    if show_only_vulnerable:
        print("Showing only VULNERABLE results")
    
    # Check if wordlist exists
    if not os.path.isfile(wordlist_path):
        print(f"Error: Wordlist not found: {wordlist_path}")
        return
    
    payloads = load_payloads(wordlist_path)
    if not payloads:
        print("No payloads loaded. Exiting.")
        return
    
    print(f"Loaded {len(payloads)} payloads")
    
    queue = Queue()
    results = []
    threads = []
    
    for _ in range(thread_count):
        t = threading.Thread(target=sqli_worker, args=(queue, url, results, 8, show_only_vulnerable))
        t.daemon = True
        t.start()
        threads.append(t)
    
    for payload in payloads:
        queue.put(payload)
    
    for _ in range(thread_count):
        queue.put(None)
    
    print("Attack in progress... Press Ctrl+C to stop\n")
    
    try:
        queue.join()
    except KeyboardInterrupt:
        print("\nAttack interrupted by user")
    
    print(f"\nSQL injection scan completed. Found {len(results)} potential vulnerabilities.")
    for result in results:
        print(result)

def lfi_attack(url, wordlist_path, thread_count=10, show_only_vulnerable=False):
    print(f"\nStarting LFI attack on: {url}")
    print(f"Using wordlist: {wordlist_path}")
    print(f"Threads: {thread_count}")
    if show_only_vulnerable:
        print("Showing only VULNERABLE results")
    
    # Check if wordlist exists
    if not os.path.isfile(wordlist_path):
        print(f"Error: Wordlist not found: {wordlist_path}")
        return
    
    payloads = load_payloads(wordlist_path)
    if not payloads:
        print("No payloads loaded. Exiting.")
        return
    
    print(f"Loaded {len(payloads)} payloads")
    
    queue = Queue()
    results = []
    threads = []
    
    for _ in range(thread_count):
        t = threading.Thread(target=lfi_worker, args=(queue, url, results, 8, show_only_vulnerable))
        t.daemon = True
        t.start()
        threads.append(t)
    
    for payload in payloads:
        queue.put(payload)
    
    for _ in range(thread_count):
        queue.put(None)
    
    print("Attack in progress... Press Ctrl+C to stop\n")
    
    try:
        queue.join()
    except KeyboardInterrupt:
        print("\nAttack interrupted by user")
    
    print(f"\nLFI scan completed. Found {len(results)} potential vulnerabilities.")
    for result in results:
        print(result)

#################################### ATTACKS

def menu():
    banner()
    print(""" 
Hello, choice which attack type you will use:
1) XSS
2) SQLi
3) LFI
4) Exit
    """)

    choice = input("> ").strip()
    if choice in ['1', '2', '3']:
        return choice
    elif choice == '4':
        print("Goodbye!")
        exit(0)
    else:
        print("Invalid choice!")
        return None

def main():
    try:
        attack_choice = menu() # 1 - XSS, 2 - SQLi, 3 - LFI;

        if attack_choice is None:
            print("No attack type selected, exiting. . . ")
            return 

        wordlist_path = word_list(attack_choice)

        target_url = get_url(attack_choice)
        if target_url is None:
            print("No target URL provided, exiting. . .")
            return

        if not isalive(target_url):
            print("Target didn't response, exiting. . .")
            return
        
        thread_count = get_threads_count()
        
        # Ask about filtering results
        show_only_vulnerable = filter_vulnerable_only()
        
        print("Starting attack...")

        if attack_choice == '1':
            xss_attack(target_url, wordlist_path, thread_count, show_only_vulnerable)
        elif attack_choice == '2':
            sqli_attack(target_url, wordlist_path, thread_count, show_only_vulnerable)
        elif attack_choice == '3':
            lfi_attack(target_url, wordlist_path, thread_count, show_only_vulnerable)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting. . .")
        return 
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    main()
