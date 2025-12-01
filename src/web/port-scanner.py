#!/usr/bin/env python3

import socket
from threading import Thread
import argparse 


def scan(target, port):
    try: 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        result = sock.connect_ex((target, port))

        if result == 0:
            print(f"Port {port} open")
        sock.close()

    except Exception as e:
        pass

def main(target, ports):
    print(f"Scanning {target}. . .")
    for port in ports:
        thread = Thread(target=scan, argc=(target, port))
        thread.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple Port Scanner')
    parser.add_argument('host', help='Target host')
    parser.add_argument('-p', '--ports', help='Ports to scan (e.g., 1-1000 or 80,443,22)', default='1-1000')
    args = parser.parse_args()

    if '-' in args.ports:
        start, end = map(int, args.ports.split('-'))
        ports = range(start, end+1)
    else:
        ports = map(int, args.ports.split(','))
    main(args.target, ports)