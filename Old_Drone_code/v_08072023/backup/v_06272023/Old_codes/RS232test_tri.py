import smbus
import time

time.sleep(1)
bus = smbus.SMBus(1) #for Rpi 2B+ (pi zero bus = 0)

devAddress = 0x4d #7 bit address (drop read/write bit)

IER = 0x08 #Interrupt Enable Register subaddressing ~0x01
EFR = 0x10 # enhanced register...change bit 4 to enable enhanced functions
LCR = 0x18 #Line Control Register Set parity, stop bits, data bits subadrr 0x03
MCR = 0x20 # Modem Control Register - Set clock divisor bit 7 subadrr. 0x04
LSR = 0x28 #Line Status Register - READ DATA
SPR = 0x38 #scratchpad register (try writing to this one...)

DLL = 0x00 #sepcial register set for divisor ect
DLH = 0x01

#set EFR using LCR 0xBF
LCR_w = 0xbf #0b10111111 to set EFR
bus.write_byte_data(devAddress, LCR, LCR_w)
LCR_Data = bus.read_byte_data(devAddress, LCR)
print('LCR Status Register String: ', hex(LCR_Data))


EFR_w = 0x10 #0b00010000 Enable enhanced functions
bus.write_byte_data(devAddress, EFR, EFR_w) #write data to EFR
EFR_Data = bus.read_byte_data(devAddress, EFR)
print('EFR Status Register String: ', hex(EFR_Data))

LCR_w = 0x83 #0b10000011 #LCR bit [7] to enable divisor change
#8 data bits 1 stop bit no parity
bus.write_byte_data(devAddress, LCR, LCR_w)
LCR_Data = bus.read_byte_data(devAddress, LCR)
print('LCR Status Register String: ', hex(LCR_Data))

DLL_w = 0x2 #0b00011000 crystal 3.6864 mHz; divsor = 2
#divisor = (3686400/(115200*16))
DLH_w = 0x00 #no high byte needed

bus.write_byte_data(devAddress, DLL, DLL_w)
#bus.write_byte_data(devAddress, DLH, DLH_w)
DLL_Data = bus.read_byte_data(devAddress, DLL) & 0xFFFF
DLH_Data = bus.read_byte_data(devAddress, DLH) & 0xFFFF
print('DDH status Register String: ', hex(DLH_Data))
print('DDL Status Register String: ', hex(DLL_Data))

#read MCR register
MCR_w = 0x0 #0b00000000 clock prescaler = 1 bit 7 (0)
MCR_Data = bus.read_byte_data(devAddress, MCR)
print('MCR Status Register String: ', hex(MCR_Data))

#read IER register
IER_w = 0x0 #0b00000000 all default
bus.write_byte_data(devAddress, IER, IER_w)
IER_Data = bus.read_byte_data(devAddress, IER) & 0xFFFF
print('IER Register String: ', hex(IER_Data)) #0x0 

#Set LCR[7] to 0 and disable divisor
LCR_w = 0x03 #0b00000011 #LCR bit [7] to enable divisor change
#8 data bits 1 stop bit no parity
bus.write_byte_data(devAddress, LCR, LCR_w)
LCR_Data = bus.read_byte_data(devAddress, LCR) & 0xFFFF
print('LCR Register String: ', hex(LCR_Data)) #0x0 

RTHR =0x00 #Receive/Tranmit Holding Register (depends on WR bit)
time.sleep(2)
#read data from holding register
try:
    Data = bus.read_i2c_block_data(devAddress, RTHR, 12) #&0xFFFF
    print('RT Data Register String: ', (Data)) #0x0 
except(KeyboardInterrupt, SystemExit): #press control C
    print('block read aborted')
    

Data = bus.read_word_data(devAddress, RTHR) &0xFFFF
print('RT Data Register String: ', hex(Data)) #0x0

time.sleep(1)
Data = bus.read_word_data(devAddress, RTHR) &0xFFFF
print('RT Data Register String: ', hex(Data)) #0x0

time.sleep(1)    
Data = bus.read_word_data(devAddress, RTHR) &0xFFFF
print('RT Data Register String: ', hex(Data)) #0x0

time.sleep(1) 
Data = bus.read_word_data(devAddress, RTHR) &0xFFFF
print('RT Data Register String: ', hex(Data)) #0x0

time.sleep(1) 
Data = bus.read_byte_data(devAddress, RTHR) &0xFFFF
print('RT Data Register String: ', hex(Data)) #0x0
time.sleep(1) 
Data = bus.read_byte_data(devAddress, RTHR) &0xFFFF
print('RT Data Register String: ', hex(Data)) #0x0


bus.close
