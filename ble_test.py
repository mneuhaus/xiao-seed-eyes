import asyncio
from bleak import BleakClient, BleakScanner
import logging
logging.basicConfig(level=logging.INFO)

# Debug function to scan for BLE devices.
async def scan_devices():
    devices = await BleakScanner.discover()
    logging.info("Discovered devices:")
    for device in devices:
        logging.info(device)

# Replace with the actual BLE MAC address of your ESP32S3
address = "02443EA4-8886-2901-1BAB-F33A3C2EDAA6"
CHAR_UUID = "abcdefab-cdef-1234-5678-1234567890ab"

async def send_command(command):
    try:
        async with BleakClient(address) as client:
            await client.write_gatt_char(CHAR_UUID, command.encode())
            logging.info(f"Sent command: {command}")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        asyncio.run(send_command(command))
    else:
        asyncio.run(scan_devices())
