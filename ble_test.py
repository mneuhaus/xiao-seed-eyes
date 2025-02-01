import asyncio
from bleak import BleakClient

# Replace with the actual BLE MAC address of your ESP32S3
address = "XX:XX:XX:XX:XX:XX"
CHAR_UUID = "abcdefab-cdef-1234-5678-1234567890ab"

async def send_command(command):
    async with BleakClient(address) as client:
        await client.write_gatt_char(CHAR_UUID, command.encode())
        print(f"Sent command: {command}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 ble_test.py <open|close|blink|colorful>")
    else:
        command = sys.argv[1]
        asyncio.run(send_command(command))
