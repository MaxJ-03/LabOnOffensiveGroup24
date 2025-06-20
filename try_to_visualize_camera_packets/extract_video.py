import sys
import struct

def extract_video_data(input_file_path, output_file_path):
    """
    Reads a raw proprietary camera TCP stream dump and extracts the video payload.
    It looks for a 'FOSC'-like header structure to identify video frames.
    """
    try:
        with open(input_file_path, 'rb') as infile, open(output_file_path, 'wb') as outfile:
            print(f"Reading from {input_file_path}...")
            
            data = infile.read()
            
            # This is a common magic word for Foscam. If your camera is different,
            # this might need to be changed by inspecting the hex dump.
            magic_word = b'FOSC'
            
            current_position = 0
            frames_found = 0
            
            # Attempt to skip any initial non-video handshake data
            initial_handshake_end = data.find(b'\r\n\r\n')
            if initial_handshake_end != -1:
                current_position = initial_handshake_end + 4
                print(f"Skipped potential handshake of {current_position} bytes.")

            while True:
                # Find the next occurrence of the magic word
                magic_pos = data.find(magic_word, current_position)
                
                if magic_pos == -1:
                    print("No more magic word markers found. End of stream.")
                    break
                
                # The header structure is an assumption. The payload length is often
                # located a few bytes after the magic word. Here we assume 8 bytes after.
                header_start = magic_pos
                payload_len_pos = header_start + 8
                
                if payload_len_pos + 4 > len(data):
                    print("Incomplete header found at the end of the file.")
                    break
                    
                # Unpack the length, assuming a 4-byte little-endian integer (<I)
                payload_len = struct.unpack('<I', data[payload_len_pos:payload_len_pos+4])[0]
                
                # The video payload should start after the full header.
                # A full header length of 20 bytes is a common guess.
                payload_start = header_start + 20

                if payload_start + payload_len > len(data) or payload_len <= 0:
                    print(f"Invalid payload length ({payload_len}) or incomplete data. Skipping.")
                    current_position = magic_pos + 4 
                    continue

                # Extract and write the payload
                payload = data[payload_start : payload_start + payload_len]
                outfile.write(payload)
                
                frames_found += 1
                if frames_found % 100 == 0:
                    print(f"Found and extracted {frames_found} frames...")
                
                current_position = payload_start + payload_len

            print(f"\nExtraction complete. Found {frames_found} frames.")
            print(f"Raw H.264 stream saved to: {output_file_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 extract_video.py <input_file.bin> <output_file.h264>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    extract_video_data(input_file, output_file)