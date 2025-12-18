import subprocess
import os
import sys

def clear():
    cmd = 'cls' if os.name == 'nt' else 'clear'
    os.system(cmd)

def menu():
    while True:
        print("\n=== Security Tools Menu ===")
        print("1 - Web Tools")
        print("2 - Cracking Tools") 
        print("3 - Network Tools")
        print("4 - OSINT Tools")
        print("5 - Other Tools")
        print("6 - Dot files")
        print("99 - Exit")
        
        try:
            choice = int(input("\n> "))
            
            if choice == 1:
                web()
            elif choice == 2:
                cracking()
            elif choice == 3:
                net()
            elif choice == 4:
                osint()
            elif choice == 5:
                other()
            elif choice == 6:
                dots()
            elif choice == 99:
                print("Goodbye!")
                break
            else:
                print("Invalid input. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def osint():
    print("\n=== OSINT Tools ===")
    print("1 - start-case.sh")
    
    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run(["src/osint/start-case.sh"])
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")


def dots():
    print("\n=== Dot files===")
    print("1 - my-kali-dot")
    print("2 - nvim-dot") 
    print("3 - pentest-arch")

    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run(["src/dots/my-kali-dot/install.sh"])
        elif choice == 2:
            subprocess.run(["src/dots/nvim-dot/install.sh"])
        elif choice == 3:
            subprocess.run(["src/dots/pentest-arch-dotfile/setup.sh"])
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def other():
    print("\n=== Other Tools ===")
    print("1 - password-policy-analyz.py")
    print("2 - phishing-email.py")
    
    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run(["src/other/password-policy-analyz.py"])
        elif choice == 2:
            subprocess.run(["src/other/phishing-email.py"])
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def cracking():
    print("\n=== Cracking Tools ===")
    print("1 - hash-crack.py")
    print("2 - pass-crack.py")
    print("3 - ssh-bruteforce.py")
    
    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run(["src/cracking/hash-crack.py"])
        elif choice == 2:
            subprocess.run(["src/cracking/pass-crack.py"])
        elif choice == 3:
            subprocess.run(["src/cracking/ssh-bruteforce.py"])
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def net():
    print("\n=== Network Tools ===")
    print("1 - net-analyz.py")
    print("2 - packet-sniffer.py")
    
    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run(["src/network/net-analyz.py"])
        elif choice == 2:
            subprocess.run(["src/network/packet-sniffer.py"])
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def web():
    print("\n=== Web Tools ===")
    print("1 - port-scanner.py")
    print("2 - recon.sh")
    print("3 - smuggler.py")
    print("4 - vulnscanner")
    
    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run(["src/web/port-scanner.py"])
        elif choice == 2:
            subprocess.run(["src/web/recon.sh"])
        elif choice == 3:
            subprocess.run(["src/web/smuggler.py"])
        elif choice == 4:
            subprocess.run(["src/web/vulnscanner/r31scanner.py"])
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def main():
    clear()
    menu()

if __name__ == '__main__':
    main()
