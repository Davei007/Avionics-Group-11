# from machine import I2C, Pin
# import time
# import math
# import struct
# 
# # ── I2C setup ──────────────────────────────────────────────
# i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
# 
# BMP280_ADDR = 0x76
# BMI270_ADDR = 0x68  # or 0x69 if SDO → VCC
# 
# # ══════════════════════════════════════════════════════════
# # BMP280
# # ══════════════════════════════════════════════════════════
# REG_CALIB  = 0x88
# REG_ID     = 0xD0
# REG_CTRL   = 0xF4
# REG_CONFIG = 0xF5
# REG_DATA   = 0xF7
# 
# def bmp_read_calibration():
#     calib = i2c.readfrom_mem(BMP280_ADDR, REG_CALIB, 24)
#     vals = list(struct.unpack('<HhhHhhhhhhhh', calib))
#     return vals
# 
# def bmp_compensate(raw_temp, raw_press, calib):
#     dig_T1, dig_T2, dig_T3 = calib[0], calib[1], calib[2]
#     dig_P1, dig_P2, dig_P3 = calib[3], calib[4], calib[5]
#     dig_P4, dig_P5, dig_P6 = calib[6], calib[7], calib[8]
#     dig_P7, dig_P8, dig_P9 = calib[9], calib[10], calib[11]
# 
#     var1 = ((raw_temp / 16384.0) - (dig_T1 / 1024.0)) * dig_T2
#     var2 = ((raw_temp / 131072.0) - (dig_T1 / 8192.0)) ** 2 * dig_T3
#     t_fine = var1 + var2
#     temperature = t_fine / 5120.0
# 
#     var1 = t_fine / 2.0 - 64000.0
#     var2 = var1 * var1 * dig_P6 / 32768.0
#     var2 = var2 + var1 * dig_P5 * 2.0
#     var2 = var2 / 4.0 + dig_P4 * 65536.0
#     var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
#     var1 = (1.0 + var1 / 32768.0) * dig_P1
#     if var1 == 0:
#         return temperature, 0
#     pressure = 1048576.0 - raw_press
#     pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
#     var1 = dig_P9 * pressure * pressure / 2147483648.0
#     var2 = pressure * dig_P8 / 32768.0
#     pressure = pressure + (var1 + var2 + dig_P7) / 16.0
#     return temperature, pressure
# 
# def bmp_init():
#     chip_id = i2c.readfrom_mem(BMP280_ADDR, REG_ID, 1)[0]
#     if chip_id not in [0x58, 0x60]:
#         raise Exception(f"BMP280 not found, got: {hex(chip_id)}")
#     print(f"BMP280 OK (id={hex(chip_id)})")
#     i2c.writeto_mem(BMP280_ADDR, REG_CTRL, bytes([0x57]))
#     i2c.writeto_mem(BMP280_ADDR, REG_CONFIG, bytes([0x14]))
# 
# def bmp_read_raw():
#     data = i2c.readfrom_mem(BMP280_ADDR, REG_DATA, 6)
#     raw_press = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
#     raw_temp  = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
#     return raw_temp, raw_press
# 
# def pressure_to_altitude(pressure_pa, sea_level_pa=101325.0):
#     return 44330.0 * (1.0 - (pressure_pa / sea_level_pa) ** (1.0 / 5.255))
# 
# # ══════════════════════════════════════════════════════════
# # BMI270 config blob (required by Bosch — must be loaded)
# # ══════════════════════════════════════════════════════════
# BMI270_CONFIG = bytes([
#     0xc8, 0x2e, 0x00, 0x2e, 0x80, 0x2e, 0x1a, 0x00, 0xc8, 0x2e, 0x00, 0x2e, 0xc8, 0x2e, 0x00, 0x2e, 0xc8, 0x2e, 0x00,
#     0x2e, 0xc8, 0x2e, 0x00, 0x2e, 0xc8, 0x2e, 0x00, 0x2e, 0xc8, 0x2e, 0x00, 0x2e, 0x90, 0x32, 0x21, 0x2e, 0x59, 0xf5,
#     0x10, 0x30, 0x21, 0x2e, 0x6a, 0xf5, 0x1a, 0x24, 0x22, 0x00, 0x80, 0x2e, 0x3b, 0x00, 0xc8, 0x2e, 0x44, 0x47, 0x22,
#     0x00, 0x37, 0x00, 0xa4, 0x00, 0xff, 0x0f, 0xd1, 0x00, 0x07, 0xad, 0x80, 0x2e, 0x00, 0xc1, 0x80, 0x2e, 0x00, 0xc1,
#     0x80, 0x2e, 0x00, 0xc1, 0x80, 0x2e, 0x00, 0xc1, 0x80, 0x2e, 0x00, 0xc1, 0x80, 0x2e, 0x00, 0xc1, 0x80, 0x2e, 0x00,
#     0xc1, 0x80, 0x2e, 0x00, 0xc1, 0x80, 0x2e, 0x00, 0xc1, 0x80, 0x2e, 0x00, 0xc1, 0x80, 0x2e, 0x00, 0xc1, 0x00, 0x00,
#     0x00, 0x00, 0x00, 0x00, 0x11, 0x24, 0xfc, 0xf5, 0x80, 0x30, 0x40, 0x42, 0x50, 0x50, 0x00, 0x30, 0x12, 0x24, 0xeb,
#     0x00, 0x03, 0x30, 0x00, 0x2e, 0xc1, 0x86, 0x5a, 0x0e, 0xfb, 0x2f, 0x21, 0x2e, 0xfc, 0xf5, 0x13, 0x24, 0x63, 0xf5,
#     0xe0, 0x3c, 0x48, 0x00, 0x22, 0x30, 0xf7, 0x80, 0xc2, 0x42, 0xe1, 0x7f, 0x3a, 0x25, 0xfc, 0x86, 0xf0, 0x7f, 0x41,
#     0x33, 0x98, 0x2e, 0xc2, 0xc4, 0xd6, 0x6f, 0xf1, 0x30, 0xf1, 0x08, 0xc4, 0x6f, 0x11, 0x24, 0xff, 0x03, 0x12, 0x24,
#     0x00, 0xfc, 0x61, 0x09, 0xa2, 0x08, 0x36, 0xbe, 0x2a, 0xb9, 0x13, 0x24, 0x38, 0x00, 0x64, 0xbb, 0xd1, 0xbe, 0x94,
#     0x0a, 0x71, 0x08, 0xd5, 0x42, 0x21, 0xbd, 0x91, 0xbc, 0xd2, 0x42, 0xc1, 0x42, 0x00, 0xb2, 0xfe, 0x82, 0x05, 0x2f,
#     0x50, 0x30, 0x21, 0x2e, 0x21, 0xf2, 0x00, 0x2e, 0x00, 0x2e, 0xd0, 0x2e, 0xf0, 0x6f, 0x02, 0x30, 0x02, 0x42, 0x20,
#     0x26, 0xe0, 0x6f, 0x02, 0x31, 0x03, 0x40, 0x9a, 0x0a, 0x02, 0x42, 0xf0, 0x37, 0x05, 0x2e, 0x5e, 0xf7, 0x10, 0x08,
#     0x12, 0x24, 0x1e, 0xf2, 0x80, 0x42, 0x83, 0x84, 0xf1, 0x7f, 0x0a, 0x25, 0x13, 0x30, 0x83, 0x42, 0x3b, 0x82, 0xf0,
#     0x6f, 0x00, 0x2e, 0x00, 0x2e, 0xd0, 0x2e, 0x12, 0x40, 0x52, 0x42, 0x00, 0x2e, 0x12, 0x40, 0x52, 0x42, 0x3e, 0x84,
#     0x00, 0x40, 0x40, 0x42, 0x7e, 0x82, 0xe1, 0x7f, 0xf2, 0x7f, 0x98, 0x2e, 0x6a, 0xd6, 0x21, 0x30, 0x23, 0x2e, 0x61,
#     0xf5, 0xeb, 0x2c, 0xe1, 0x6f
# ])
# 
# # ── BMI270 registers ────────────────────────────────────────
# BMI_CHIP_ID     = 0x00
# BMI_ACC_DATA    = 0x0C
# BMI_GYR_DATA    = 0x12
# BMI_PWR_CONF    = 0x7C
# BMI_PWR_CTRL    = 0x7D
# BMI_INIT_CTRL   = 0x59
# BMI_INIT_DATA   = 0x5E
# BMI_INIT_ADDR_0 = 0x5B
# BMI_INIT_ADDR_1 = 0x5C
# BMI_ACC_CONF    = 0x40
# BMI_ACC_RANGE   = 0x41
# BMI_GYR_CONF    = 0x42
# BMI_GYR_RANGE   = 0x43
# BMI_INTERNAL_STATUS = 0x21
# 
# def bmi_write(reg, val):
#     i2c.writeto_mem(BMI270_ADDR, reg, bytes([val]))
# 
# def bmi_read(reg, length):
#     return i2c.readfrom_mem(BMI270_ADDR, reg, length)
# 
# def bmi_load_config():
#     """Load the required Bosch config blob into BMI270."""
#     bmi_write(BMI_PWR_CONF, 0x00)   # disable advanced power save
#     time.sleep_ms(10)
#     bmi_write(BMI_INIT_CTRL, 0x00)  # start config load
#     time.sleep_ms(10)
# 
#     # Write config in 64-byte chunks
#     chunk_size = 64
#     for i in range(0, len(BMI270_CONFIG), chunk_size):
#         chunk = BMI270_CONFIG[i:i + chunk_size]
#         word_addr = i // 2
#         bmi_write(BMI_INIT_ADDR_0, word_addr & 0x0F)
#         bmi_write(BMI_INIT_ADDR_1, (word_addr >> 4) & 0xFF)
#         i2c.writeto_mem(BMI270_ADDR, BMI_INIT_DATA, chunk)
# 
#     bmi_write(BMI_INIT_CTRL, 0x01)  # end config load
#     time.sleep_ms(20)
# 
#     status = bmi_read(BMI_INTERNAL_STATUS, 1)[0] & 0x0F
#     if status != 0x01:
#         raise Exception(f"BMI270 config load failed, status={hex(status)}")
# 
# def bmi_init():
#     chip_id = bmi_read(BMI_CHIP_ID, 1)[0]
#     if chip_id != 0x24:
#         raise Exception(f"BMI270 not found, got: {hex(chip_id)}")
#     print(f"BMI270 OK (id={hex(chip_id)})")
# 
#     bmi_load_config()
# 
#     # Enable accel + gyro
#     bmi_write(BMI_PWR_CTRL, 0x0E)
#     time.sleep_ms(10)
# 
#     # Accel: 100Hz, normal mode, ±8g range
#     bmi_write(BMI_ACC_CONF,  0xA8)
#     bmi_write(BMI_ACC_RANGE, 0x02)
# 
#     # Gyro: 100Hz, normal mode, ±2000 dps range
#     bmi_write(BMI_GYR_CONF,  0xA9)
#     bmi_write(BMI_GYR_RANGE, 0x00)
# 
#     bmi_write(BMI_PWR_CONF, 0x02)  # enable FIFO, disable adv power save
#     time.sleep_ms(10)
# 
# def bmi_read_accel():
#     """Returns acceleration in m/s² (±8g range)."""
#     data = bmi_read(BMI_ACC_DATA, 6)
#     ax = struct.unpack('<h', data[0:2])[0]
#     ay = struct.unpack('<h', data[2:4])[0]
#     az = struct.unpack('<h', data[4:6])[0]
#     # ±8g range → sensitivity = 4096 LSB/g
#     scale = 9.81 / 4096.0
#     return ax * scale, ay * scale, az * scale
# 
# def bmi_read_gyro():
#     """Returns rotation rate in degrees/sec (±2000 dps range)."""
#     data = bmi_read(BMI_GYR_DATA, 6)
#     gx = struct.unpack('<h', data[0:2])[0]
#     gy = struct.unpack('<h', data[2:4])[0]
#     gz = struct.unpack('<h', data[4:6])[0]
#     # ±2000 dps → 16.384 LSB/dps
#     scale = 1.0 / 16.384
#     return gx * scale, gy * scale, gz * scale
# 
# # ══════════════════════════════════════════════════════════
# # Main
# # ══════════════════════════════════════════════════════════
# bmp_calib = bmp_read_calibration()
# bmp_init()
# bmi_init()
# 
# while True:
#     # BMP280
#     raw_temp, raw_press = bmp_read_raw()
#     temp, press = bmp_compensate(raw_temp, raw_press, bmp_calib)
#     altitude = pressure_to_altitude(press)
# 
#     # BMI270
#     ax, ay, az = bmi_read_accel()
#     gx, gy, gz = bmi_read_gyro()
# 
#     print(f"Temp:      {temp:.2f} °C")
#     print(f"Pressure:  {press/100:.2f} hPa")
#     print(f"Altitude:  {altitude:.2f} m")
#     print(f"Accel:     X={ax:.2f}  Y={ay:.2f}  Z={az:.2f}  m/s²")
#     print(f"Gyro:      X={gx:.1f}  Y={gy:.1f}  Z={gz:.1f}  °/s")
#     print("─" * 40)
#     time.sleep(0.1)






#-------------------------------------SD-----------------------------
#import machine
import os
import sdcard

# ── SD setup ─────────────────────
spi = machine.SPI(
    1,
    sck=machine.Pin(10),
    mosi=machine.Pin(11),
    miso=machine.Pin(8)
)

cs = machine.Pin(9, machine.Pin.OUT)

sd = sdcard.SDCard(spi, cs)
vfs = os.VfsFat(sd)
os.mount(vfs, "/sd")

print("Mounted OK")

# ── WRITE FILE ───────────────────
with open("/sd/test2.txt", "w") as f:
    f.write("Hello SD card2\n")

print("Write done")





# 
# #-----------------------------------LoRa-------------------------------
# from machine import SPI, Pin
# import time
# 
# # ── SPI setup ──────────────────────────────────────────────
# spi = SPI(0,
#           baudrate=1000000,
#           polarity=0,
#           phase=0,
#           sck=Pin(18),
#           mosi=Pin(19),
#           miso=Pin(16))
# 
# cs = Pin(17, Pin.OUT)
# cs.value(1)
# 
# # ── SX1278 register write/read ─────────────────────────────
# def spi_write(reg, val):
#     cs.value(0)
#     spi.write(bytes([reg | 0x80, val]))
#     cs.value(1)
# 
# def spi_read(reg):
#     cs.value(0)
#     spi.write(bytes([reg & 0x7F]))
#     result = spi.read(1)
#     cs.value(1)
#     return result[0]
# 
# # ── Registers ──────────────────────────────────────────────
# REG_FIFO            = 0x00
# REG_OP_MODE         = 0x01
# REG_FRF_MSB         = 0x06
# REG_FRF_MID         = 0x07
# REG_FRF_LSB         = 0x08
# REG_PA_CONFIG       = 0x09
# REG_FIFO_ADDR_PTR   = 0x0D
# REG_FIFO_TX_BASE    = 0x0E
# REG_IRQ_FLAGS       = 0x12
# REG_PAYLOAD_LENGTH  = 0x22
# REG_MODEM_CONFIG1   = 0x1D
# REG_MODEM_CONFIG2   = 0x1E
# REG_MODEM_CONFIG3   = 0x26
# REG_SYNC_WORD       = 0x39
# REG_DIO_MAPPING1    = 0x40
# REG_VERSION         = 0x42
# REG_PA_DAC          = 0x4D
# 
# # ── Modes ──────────────────────────────────────────────────
# MODE_SLEEP   = 0x80  # LoRa + sleep
# MODE_STDBY   = 0x81  # LoRa + standby
# MODE_TX      = 0x83  # LoRa + TX
# 
# # ── Init ───────────────────────────────────────────────────
# def lora_init(freq_mhz=433.0):
#     # Check version register
#     ver = spi_read(REG_VERSION)
#     if ver != 0x12:
#         raise Exception(f"SX1278 not found, got: {hex(ver)}")
#     print(f"SX1278 OK (ver={hex(ver)})")
# 
#     # Must be in sleep mode to switch to LoRa
#     spi_write(REG_OP_MODE, MODE_SLEEP)
#     time.sleep_ms(10)
# 
#     # Set frequency (433 MHz default)
#     frf = int((freq_mhz * 1e6) / (32e6 / 524288))
#     spi_write(REG_FRF_MSB, (frf >> 16) & 0xFF)
#     spi_write(REG_FRF_MID, (frf >> 8)  & 0xFF)
#     spi_write(REG_FRF_LSB,  frf        & 0xFF)
# 
#     # Standby before config
#     spi_write(REG_OP_MODE, MODE_STDBY)
#     time.sleep_ms(10)
# 
#     # Modem config:
#     # BW=125kHz, CR=4/5, explicit header
#     spi_write(REG_MODEM_CONFIG1, 0x72)
#     # SF=7, normal mode, CRC on
#     spi_write(REG_MODEM_CONFIG2, 0x74)
#     # Low data rate optimize off, AGC on
#     spi_write(REG_MODEM_CONFIG3, 0x04)
# 
#     # PA boost pin, max power, +17dBm
#     spi_write(REG_PA_CONFIG, 0x80)		#<--------------------- this line should be (0x8F) for max power instead of 0x80 (can be changed only when antenna is attached)
#     spi_write(REG_PA_DAC,    0x84)		#<--------------------- this line should have (0x87) for max power instead of 0x84 (can be changed only when antenna is attached)
# 
#     # FIFO TX base at 0
#     spi_write(REG_FIFO_TX_BASE, 0x00)
#     spi_write(REG_FIFO_ADDR_PTR, 0x00)
# 
#     # Sync word 0x12 = private LoRa network
#     spi_write(REG_SYNC_WORD, 0x12)
# 
#     print("SX1278 configured")
# 
# # ── Transmit ───────────────────────────────────────────────
# def lora_send(data: bytes):
#     # Go to standby
#     spi_write(REG_OP_MODE, MODE_STDBY)
#     time.sleep_ms(10)
# 
#     # Reset FIFO pointer
#     spi_write(REG_FIFO_ADDR_PTR, 0x00)
# 
#     # Write payload into FIFO
#     for byte in data:
#         spi_write(REG_FIFO, byte)
# 
#     # Set payload length
#     spi_write(REG_PAYLOAD_LENGTH, len(data))
# 
#     # Clear IRQ flags
#     spi_write(REG_IRQ_FLAGS, 0xFF)
# 
#     # Start TX
#     spi_write(REG_OP_MODE, MODE_TX)
# 
#     # Poll TxDone flag (bit 3 of IRQ register)
#     timeout = 5000  # 5 seconds max
#     start = time.ticks_ms()
#     while True:
#         irq = spi_read(REG_IRQ_FLAGS)
#         if irq & 0x08:  # TxDone bit
#             break
#         if time.ticks_diff(time.ticks_ms(), start) > timeout:
#             print("TX timeout!")
#             break
#         time.sleep_ms(10)
# 
#     # Clear flags and go back to standby
#     spi_write(REG_IRQ_FLAGS, 0xFF)
#     spi_write(REG_OP_MODE, MODE_STDBY)
#     print(f"Sent: {data}")
# 
# # ── Main ───────────────────────────────────────────────────
# lora_init(freq_mhz=433.0)
# 
# counter = 0
# while True:
#     msg = f"hello {counter}".encode()
#     lora_send(msg)
#     counter += 1
#     time.sleep(5)
#     # Run this to verify SPI comms and chip registers
#     print(hex(spi_read(0x42)))  # Version — should print 0x12
#     print(hex(spi_read(0x01)))  # OpMode — should print 0x81 (standby)
#     print(hex(spi_read(0x06)))  # Frequency MSB — should match what you set
