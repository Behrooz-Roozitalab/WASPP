#!/usr/bin/python2

'''
Basic communication functions with Valco Valve

if sendTo == 0: Getting current position
if sendTo == 1: Getting current position
if sendTo == 2: Moving to next position
'''

def comValco(sendTo):
  import smbus
  import time
  import os

  #time.sleep(1)
  bus = smbus.SMBus(1) #for Rpi 2B+ (pi zero bus = 0)

  devAddress = 0x4c #7 bit address (drop read/write bit)

  IER = 0x08 #Interrupt Enable Register subaddressing ~0x01
  EFR = 0x10 # enhanced register...change bit 4 to enable enhanced functions
  LCR = 0x18 #Line Control Register Set parity, stop bits, data bits subadrr 0x03
  MCR = 0x20 # Modem Control Register - Set clock divisor bit 7 subadrr. 0x04
  LSR = 0x28 #Line Status Register - READ DATA
  SPR = 0x38 #scratchpad register (try writing to this one...)

  FCR = 0x10 #FIFO REGISTER...accessible when LCR is NOT 0xBF
  RXLVL = 0x48 #RX FIFO #read only register...tells number of charecters stored in RX FIFO
  #ranges from 0 (0x00) to  64 (0x40) bit 7 = 0 bits 6:0 is num. of char

  DLL = 0x00 #sepcial register set for divisor ect
  DLH = 0x01

  #set FIFO register (read only)
  FCR_w = 0x83
  bus.write_byte_data(devAddress, FCR, FCR_w)

  #set EFR using LCR 0xBF
  LCR_w = 0xbf #0b10111111 to set EFR
  bus.write_byte_data(devAddress, LCR, LCR_w)

  EFR_w = 0x10 #0b00010000 Enable enhanced functions
  bus.write_byte_data(devAddress, EFR, EFR_w) #write data to EFR

  LCR_w = 0x83 #0b10000011 #LCR bit [7] to enable divisor change
  #8 data bits 1 stop bit no parity
  bus.write_byte_data(devAddress, LCR, LCR_w)

  DLL_w = 0x18 #0b00011000 crystal 3.6864 mHz; divsor = 24
  #DLL_w = 0x46
  #divisor = (3686400/(9600*16))
  #DLH_w = 0x46 #no high byte needed

  #currently bus.write_byte_data acting like bus.write_word
  #i.e. you cannot write to the low and high byte sepereately. Whichever byte
  #is last written overwrites the other
  #similarly bus.read_byte_data is reading the whole word, not high and low bytes
  bus.write_byte_data(devAddress, DLL, DLL_w)
  #bus.write_byte_data(devAddress, DLH, DLH_w)
  DLL_Data = bus.read_byte_data(devAddress, DLL) & 0xFFFF
  DLH_Data = bus.read_byte_data(devAddress, DLH) & 0xFFFF

  #read MCR register
  MCR_w = 0x0 #0b00000000 clock prescaler = 1 bit 7 (0)

  #read IER register
  IER_w = 0x0 #0b00000000 all default
  bus.write_byte_data(devAddress, IER, IER_w)
  IER_Data = bus.read_byte_data(devAddress, IER) & 0xFFFF

  #Set LCR[7] to 0 and disable divisor
  LCR_w = 0x03 #0b00000011 #LCR bit [7] to enable divisor change
  #8 data bits 1 stop bit no parity
  bus.write_byte_data(devAddress, LCR, LCR_w)
  LCR_Data = bus.read_byte_data(devAddress, LCR) & 0xFFFF
    

  EFCR = 0x0f #enhanced freatures control register
  #EFCR_w = 0x20 #try inverting the string??
  #bus.write_byte_data(devAddress, EFCR, EFCR_w)
  EFCR_Data = bus.read_byte_data(devAddress, EFCR) & 0xFFFF

  RTHR =0x00 #Receive/Tranmit Holding Register (depends on WR bit)
  CR = 0xd
  A = 0x41
  C = 0x43
  H = 0x48
  M = 0x4d
  P = 0x50
  W = 0x57

  #write data to transmit
  if sendTo == 1:
    bus.write_byte_data(devAddress, RTHR, C)
    time.sleep(0.1)
        
    #write data to transmit
    bus.write_byte_data(devAddress, RTHR, C)
    time.sleep(0.1)

    #write data to transmit
    bus.write_byte_data(devAddress, RTHR, CR)
    time.sleep(0.1)

  elif sendTo == 2:
    bus.write_byte_data(devAddress, RTHR, C)
    time.sleep(0.1)

    #write data to transmit
    bus.write_byte_data(devAddress, RTHR, W)
    time.sleep(0.1)

    #write data to transmit
    bus.write_byte_data(devAddress, RTHR, CR)
    time.sleep(0.1)

  time.sleep(0.1)
  #write data to transmit
  bus.write_byte_data(devAddress, RTHR, C)
  time.sleep(0.1)

  bus.write_byte_data(devAddress, RTHR, P)
  time.sleep(0.1)

  bus.write_byte_data(devAddress, RTHR, CR)
  time.sleep(0.1)
        
  #Read status and print status
  Status = bus.read_byte_data(devAddress, LSR) &0xFFFF

  time.sleep(0.1)
        
  #read Position from relply 
  Pos1 = bus.read_i2c_block_data(devAddress, RTHR,32) 
  time.sleep(0.1)

  #write position to MAIN log file
  time.sleep(0.1)
  RXLVL_Data = bus.read_byte_data(devAddress, RXLVL) & 0xFFFF

  time.sleep(0.1)
  bus.close

  #has valve moved? maybe check that and return a 1...or something
  return (Pos1[2], Pos1[3])
