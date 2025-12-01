#!/usr/bin/env python3

import sys
from scapy.all import *
import argparse

def handle_packet(packet, log_file, verbose=False):
    if packet.haslayer(IP):
        ip_layer = packet[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
        
        if packet.haslayer(TCP):
            tcp_layer = packet[TCP]
            src_port = tcp_layer.sport
            dst_port = tcp_layer.dport
            protocol = "TCP"
            
            log_entry = f"{protocol} Connection: {src_ip}:{src_port} -> {dst_ip}:{dst_port}"
            log_file.write(log_entry + '\n')
            
            if verbose:
                print(log_entry)

def main(interface, verbose=False):
    logfile_name = f"sniffer_{interface}_log.txt"

    try:
        with open(logfile_name, 'w') as logfile:
            print(f"Starting packet sniffing on interface: {interface}")
            print(f"Logging to: {logfile_name}")
            print("Press Ctrl+C to stop...")
            
            # Используем lambda для передачи дополнительных аргументов
            sniff(iface=interface, 
                  prn=lambda pkt: handle_packet(pkt, logfile, verbose),
                  store=0)

    except KeyboardInterrupt:
        print(f"\nSniffing stopped on {interface}")
    except PermissionError:
        print("Permission denied! Try running with sudo.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple packet sniffer')
    parser.add_argument('interface', help='Network interface to sniff on')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    main(args.interface, verbose=args.verbose)
