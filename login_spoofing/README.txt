Login Spoofing of Foscam camera

Before running the script a Man-in-the-Middle position should be established between the camera and the victim.
Open WireShark using the command: sudo wireshark, in order to monitor the packets sent between the victim and the camera.
Start capturing the packets on the respective interface.
Then run the script.

Running the script:
0. You need to be on a Linux machine
1. Open terminal
2. Navigate to the directory containing this script
3. Type in the command: sudo python3 http_spoof_server.py --camera 192.168.0.5 --port 88 --iface <whatever-interface>

The victim connects to the server without knowing and sees the fake copy of the website
When the victim enters his/hers credentials, in terminal we can see them (both username and password)
