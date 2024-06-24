import pysquared_rfm9x
import board
import busio
import digitalio
import traceback

import time
import os
import asyncio

import radio_diagnostics
from icpacket import Packet
from new_comms_protocol.ptp import AsyncPacketTransferProtocol as APTP
from new_comms_protocol.ftp import FileTransferProtocol as FTP

# Chip's buffer size: 256 bytes
# pycubed_rfm9x header size: 4 bytes
# pycubed_rfm9x CRC16 checksum size: 2 bytes (not sure if this takes away from available bytes)
# ptp header size: 6 bytes
MAX_PACKET_SIZE = 256 - 4 - 2 - 6 # 244
# msgpack apparently adds 2 bytes overhead for bytes payloads
MAX_PAYLOAD_SIZE = MAX_PACKET_SIZE - 2 # 242
TEST_IMAGE_PATH = "THBBlueEarthTest.jpeg"

async def main():
	print("Irvington CubeSat's Test Satellite Board")
	
	spi0   = busio.SPI(board.SPI0_SCK,board.SPI0_MOSI,board.SPI0_MISO)
	_rf_cs1 = digitalio.DigitalInOut(board.SPI0_CS0)
	_rf_cs1.switch_to_output(value=True)
	_rf_rst1 = digitalio.DigitalInOut(board.RF1_RST)
	_rf_rst1.switch_to_output(value=True)
	radio1 = pysquared_rfm9x.RFM9x(spi0,_rf_cs1, _rf_rst1, 437.4, code_rate=8, baudrate=1320000)
	radio1.tx_power=23
	radio1.spreading_factor = 8
	radio1.node = 0xfa
	radio1.destination = 0xfb
	radio1.enable_crc=True
	radio1.ack_delay=0.2
	
	ptp = APTP(radio1, packet_size=MAX_PACKET_SIZE, timeout=10, log=False)
	ftp = FTP(ptp, chunk_size=MAX_PAYLOAD_SIZE, packet_delay=0, log=False)
	
	radio_diagnostics.report_diagnostics(radio1)
	
	while True:
		try:
			print("Sending telemetry ping (handshake 1) and waiting for handshake 2")
			packet = Packet.make_handshake1()
			await ptp.send_packet(packet)
			packet = await ptp.receive_packet()
			if packet.categorize() != "handshake2":
				print(f"Packet of type {packet.categorize()} (not handshake2) received")
				continue
				
			print("Handshake 2 received, sending handshake 3")
			
			# header = bytearray("#IRVCBH3", "utf-8")
			image_count = 420
			# image_count_ba = bytearray(image_count.to_bytes(4, "little"))
			# packet = header + image_count_ba
			
			packet = Packet.make_handshake3(image_count)
			# radio1.send(packet)
			await ptp.send_packet(packet)
			
			print("Sending a picture")
			await ftp.send_file(TEST_IMAGE_PATH, file_id=69)
			
			print("20-sec cooldown period")
			time.sleep(20)
		
		except Exception as e:
			print("Error in Main Loop: "+ ''.join(traceback.format_exception(e)))
		

if __name__ == "__main__":
	asyncio.run(main())
