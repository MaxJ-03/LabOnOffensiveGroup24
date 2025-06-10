from scapy.all import IP, TCP, send, sr1

# Target IP and Port
target_ip = "192.168.0.5"
target_port = 88

# Create IP layer
ip = IP(dst=target_ip)

# Create TCP SYN packet
tcp = TCP(dport=target_port, flags='S', sport=12345, seq=1000)


for i in range(100):
    # Send the packet
    packet = ip / tcp
    send(packet)
# Send the SYN and wait for a SYN-ACK
response = sr1(packet, timeout=2, verbose=False)

# Analyze response
if response:
    if response.haslayer(TCP) and response.getlayer(TCP).flags == 0x12:
        print("[+] SYN-ACK received!")
        print(f"    Source Port: {response[TCP].sport}")
        print(f"    Sequence Number: {response[TCP].seq}")
    else:
        print("[-] Received packet, but not SYN-ACK.")
else:
    print("[-] No response received.")

