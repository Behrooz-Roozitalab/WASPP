#!/usr/bin/python2

'''
Basic communication functions with Wind sensor 
(TriSonica Mini Wind & Weather Sensor)
'''

CODE_FOLDER = '/home/ljs/v_08072023/py2prog/'
LOG_FOLDER = '/home/ljs/v_08072023/logs/'
LOG_WIND = 'TrisonicaWinds.txt'

def getWind(Date):
  import os
  import smbus
  import time
  
  wind = 0
  bus = smbus.SMBus(1) # for Rpi 2B+ (pi zero bus = 0)
  devAddress = 0x4d #7 bit address (drop read/write bit)

  IER = 0x08 #Interrupt Enable Register subaddressing ~0x01
  EFR = 0x10 # enhanced register...change bit 4 to enable enhanced functions...only accesible when
  #LCR is 0xBF
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
  LCR_Data = bus.read_byte_data(devAddress, LCR)
  EFR_w = 0x10 #0b00010000 Enable enhanced functions
  bus.write_byte_data(devAddress, EFR, EFR_w) #write data to EFR
  EFR_Data = bus.read_byte_data(devAddress, EFR)

  LCR_w = 0x83 #0b10000011 #LCR bit [7] to enable divisor change
  #8 data bits 1 stop bit no parity
  bus.write_byte_data(devAddress, LCR, LCR_w)
  LCR_Data = bus.read_byte_data(devAddress, LCR)

  DLL_w = 0x2 #0b00011000 crystal 3.6864 mHz; divsor = 2
  #divisor = (3686400/(115200*16))
  DLH_w = 0x00 #no high byte needed

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
  MCR_Data = bus.read_byte_data(devAddress, MCR)

  #read IER register
  IER_w = 0x0 #0b00000000 all default
  bus.write_byte_data(devAddress, IER, IER_w)
  IER_Data = bus.read_byte_data(devAddress, IER) & 0xFFFF

  #Set LCR[7] to 0 and disable divisor
  LCR_w = 0x03 #0b00000011 #LCR bit [7] to enable divisor change
  #8 data bits 1 stop bit no parity
  bus.write_byte_data(devAddress, LCR, LCR_w)
  LCR_Data = bus.read_byte_data(devAddress, LCR) & 0xFFFF
   
  RXLVL_Data = bus.read_byte_data(devAddress, RXLVL) & 0xFFFF

  RTHR =0x00 #Receive/Tranmit Holding Register (depends on WR bit)
  EOT = 3 #in decimal
  space = 32
  a = 97
  h = 104
  i = 105
  c = 99
  d = 100
  e = 101
  g = 103
  l = 108
  n = 110
  o = 111
  r = 114
  s = 115
  t = 116
  v = 118
  w = 119
  x = 120   
  D = 68
  H = 72
  S = 83
  T = 84
  CR = 13

  #write control C or EOT 
  data = [3,13]
  bus.write_i2c_block_data(devAddress, RTHR, data)
  time.sleep(0.2)
    
  #hide all
  data = [104,105,100,101, 32,97,108,108,13]
  bus.write_i2c_block_data(devAddress, RTHR, data)
  time.sleep(0.2)
  #show S2D 
  data = [115,104,111,119,32, 83, 50,68,13]
  bus.write_i2c_block_data(devAddress, RTHR, data)
  time.sleep(0.2)
  #show D
  data = [115,104,111,119,32, 68,13]
  bus.write_i2c_block_data(devAddress, RTHR, data)
  time.sleep(0.2)
  #show T
  data = [115,104,111,119,32, 84,13]
  bus.write_i2c_block_data(devAddress, RTHR, data)
  time.sleep(0.2)
  #show heading
  data = [115,104,111,119,32,72,101,97,100,105,110,103,13]
  bus.write_i2c_block_data(devAddress, RTHR, data)
  time.sleep(0.2)
    
  #exit and go back to recieving data
  data = [101,120,105,116,13]
  bus.write_i2c_block_data(devAddress, RTHR, data)

  # Read data from holding register
  time.sleep(1)
  try:
    for _ in range(30):
      Winds = bus.read_i2c_block_data(devAddress, RTHR, 32) #&0xFFFF
      # print('RT Data Register String: ', Winds) #0x0

      RXLVL_Data = bus.read_byte_data(devAddress, RXLVL) & 0xFFFF
      # print('RXLVL Register String: ', hex(RXLVL_Data)) #0x0

      # write position to Trisonica log file
      os.chdir(LOG_FOLDER)
      temp_data_file = open(LOG_WIND, 'a')
      line = []
      for w in Winds:
        if w==0:
          line.append(str(w))
        else:
          line.append(chr(w))
      line = ','.join(line)
      temp_data_file.write(str(Date) + ',' + line + '\n')
      temp_data_file.close()
      wind = Winds[1]
      temp_data_file.close()
      time.sleep(0.105)
  except(KeyboardInterrupt, SystemExit): #press control C
    print('block read aborted')

  bus.close
 
  return wind

      
