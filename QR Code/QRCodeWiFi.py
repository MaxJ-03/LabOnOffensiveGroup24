import qrcode

def generate_wifi_qr(ssid, password, security='WPA', hidden=False, filename="wifi_qr.png"):
    # Format the Wi-Fi string
    hidden_str = f";H:true" if hidden else ""
    wifi_config = f"WIFI:T:{security};S:{ssid};P:{password}{hidden_str};;"

    # Create and save QR code
    qr = qrcode.make(wifi_config)
    qr.save(filename)
    print(f"Wi-Fi QR code saved as '{filename}'")

# Example usage
generate_wifi_qr(ssid="MyHomeWiFi", password="SuperSecret123", security="WPA", filename="my_wifi_qr.png")
