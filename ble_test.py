import asyncio
from bleak import BleakClient

# Replace with the actual BLE MAC address of your ESP32S3
address = "34:85:18:71:f5:35"
CHAR_UUID = "abcdefab-cdef-1234-5678-1234567890ab"

async def send_command(command):
    try:
        async with BleakClient(address) as client:
            await client.write_gatt_char(CHAR_UUID, command.encode())
            print(f"Sent command: {command}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 ble_test.py <open|close|blink|colorful>")
    else:
        command = sys.argv[1]
        asyncio.run(send_command(command))
