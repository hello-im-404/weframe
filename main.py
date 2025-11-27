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
            script_path = "src/osint/start-case.sh"
            subprocess.run(["chmod", "+x", script_path])
            subprocess.run([script_path], shell=True)
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def other():
    print("\n=== Other Tools ===")
    print("1 - my-kali-dot")
    print("2 - nvim-dot") 
    print("3 - pentest-arch")
    print("4 - Description about options")
    
    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run(["chmod", "+x", "src/other/my-kali-dot/install.sh"])
            subprocess.run(["src/other/my-kali-dot/install.sh"], shell=True)
        elif choice == 2:
            subprocess.run(["chmod", "+x", "src/other/nvim-dot/install.sh"])
            subprocess.run(["src/other/nvim-dot/install.sh"], shell=True)
        elif choice == 3:
            subprocess.run(["chmod", "+x", "src/other/pentest-arch-dotfile/setup.sh"])
            subprocess.run(["src/other/pentest-arch-dotfile/setup.sh"], shell=True)
        elif choice == 4:
            print("\n--- Descriptions ---")
            print("my-kali-dot - installing packages for pentest on Debian/Kali distro.")
            print("nvim-dot - neovim personal dotfile.")
            print("pentest-arch - install packages for pentest on Arch-based distro.")
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def cracking():
    print("\n=== Cracking Tools ===")
    print("1 - hash-crack.py")
    print("2 - pass-crack.py")
    
    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run([sys.executable, "src/cracking/hash-crack.py"])
        elif choice == 2:
            subprocess.run([sys.executable, "src/cracking/pass-crack.py"])
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def net():
    print("\n=== Network Tools ===")
    print("1 - net-analyz.py")
    
    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run([sys.executable, "src/network/net-analyz.py"])
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def web():
    print("\n=== Web Tools ===")
    print("1 - csrf-generator.py")
    print("2 - recon.sh")
    print("3 - smuggler.py")
    print("4 - vulnscanner")
    
    try:
        choice = int(input("\n> "))
        if choice == 1:
            subprocess.run([sys.executable, "src/web/csrf-generator.py"])
        elif choice == 2:
            subprocess.run(["chmod", "+x", "src/web/recon.sh"])
            subprocess.run(["src/web/recon.sh"], shell=True)
        elif choice == 3:
            subprocess.run([sys.executable, "src/web/smuggler.py"])
        elif choice == 4:
            subprocess.run([sys.executable, "src/web/vulnscanner/r31scanner.py"])
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")

def main():
    clear()
    menu()

if __name__ == '__main__':
    main()
