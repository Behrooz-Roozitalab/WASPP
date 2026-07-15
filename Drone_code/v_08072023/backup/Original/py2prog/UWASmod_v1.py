#!/usr/bin/python2

#define functions here
def programRunning(Run):
    import RPi.GPIO as GPIO
    import time
    #prior to pump test, system pressure and ambient pressure
    #should be equal
    #if its over some value (no pump on) pressure is NOT Ok (0)
    if Run > 0:
        runningNow = 1
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(22,GPIO.OUT)
        GPIO.output(22, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(22, GPIO.LOW)
        #GPIO.cleanup()
    else:
        runningNow = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(22,GPIO.OUT)
        GPIO.output(22, GPIO.LOW)
        GPIO.cleanup()
    return runningNow

def softShutdown():
    import os
    #soft shudown on landing or if tests fail
    os.system("sudo poweroff")
    return

def pumpTest(pumpWorks):
    import RPi.GPIO as GPIO
    import time
    if pumpWorks == 1:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(24,GPIO.OUT)
        GPIO.output(24, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(24, GPIO.LOW)
        GPIO.cleanup()
        
def batteryOK(BAT):
    import RPi.GPIO as GPIO
    import time
    if BAT > 3.6: 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(27,GPIO.OUT)
        GPIO.output(27, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(27, GPIO.LOW)
        GPIO.cleanup()
        
        

def testSensors(RH, Temp, pSys, pAmb):
    import RPi.GPIO as GPIO
    import time
    sensors = 1
    #assume all sensors are working until proven wrong
    if pSys < 8:
        sensors = 0

    if pAmb < 8:
        sensors = 0

    if Temp < -5:
        sensors = 0

    if RH < 2:
        sensors = 0

    if sensors == 1:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23,GPIO.OUT)
        GPIO.output(23, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(23, GPIO.LOW)
        GPIO.cleanup()
    
    return sensors

    
def pumpOn(onOff):
    import RPi.GPIO as GPIO
    import time

    if onOff == 1:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18,GPIO.OUT)
    
        #GPIO.output(18, GPIO.LOW)
        #time.sleep(2)
        GPIO.output(18, GPIO.HIGH)
        PumpStatus = 1
        #GPIO.cleanup()
    else:
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18,GPIO.OUT)
        
        GPIO.output(18, GPIO.LOW)
        time.sleep(2)
        GPIO.cleanup()
        PumpStatus = 0
        
    return PumpStatus

    
def GPSsetup():
    import serial
    import time
    import os

    gps = serial.Serial('/dev/ttyAMA0', baudrate=9600)

    #test- trying to set new output rate to 5Hz from (~1 Hz)
    outstr = ''
    instr = ''

    gps.flushInput()
    gps.flushOutput()

    outstr = '$PMTK220,200*2C\r\n'

    gps.write(outstr)

    time.sleep(0.2)

    #read data...maybe this and read ADC should be running in background
    number = 0
    Date = 'No Date Available'
    while (number  <8):
        line = gps.readline()
        #print(line)
        data = line.split(',')
        number = number + 1
        
        if (data[0] == '$GPGGA'):
            #print line
            #read line & parse lat, lon, alt, time, fix, satellites, ect...
            gpsData = line.split(',')
            Date = gpsData[1]
            Lat = gpsData[2]
            Lon = gpsData[4]
            Alt = gpsData[9]
            DGeo = gpsData[11]
            Sat = gpsData[7]
            #open file and write header
            os.chdir('/home/pi/temp/')
            temp_data_file = open('GPS_log.txt', 'a')
            temp_data_file.write(Date+','+Lat+','+Lon+','+Alt+','+DGeo+','+Sat+'\n')
            temp_data_file.close()
            os.chdir('/home/pi/py2prog/')
    
    return (Date,Lat,Lon,Alt,Sat)
    gps.close()

def readGPSdata():
    import os

    #parse GPS String here
    os.chdir('/home/pi/temp/')
    gpsfile = open('GPSlog_v2.txt', 'r')
    #move pointer to one line before the end of file
    gpsfile.seek(-48,2)
    GPSdata = gpsfile.readline()
    print (GPSdata)
    GPSdata = GPSdata.rstrip('\n')
    line = GPSdata.split(',')
    Date = line[0]
    Lat = line[1]
    Lon = line[3]
    Alt = line[5]
    Sat = line[7]
    print(GPSsplit)
    temp_data_file.close()
    os.chdir('/home/pi/py2prog/')

    return(Date, Lat, Lon, Alt,sat)

def readi2cU10(Date):
    import os
    import numpy
    import time
    import Adafruit_ADS1x15
    adc = Adafruit_ADS1x15.ADS1115(address=0x49,busnum=1)
    GAIN = 2/3

    #open file and write header
    #os.chdir('/home/pi/temp/')
    #temp_data_file = open('FlowLog_Posall_v1.txt', 'a')
    #temp_data_file.write('Ch1 V, Flow, Ch3 V,'+'\n')
    #temp_data_file.write('Battery Voltage, Ch2 V, Flow SLMP, 10V Power'+'\n')
    #temp_data_file.close()
    #os.chdir('/home/pi/py2prog/')
        
    values=[0]*4
    #read ADC channel 0 as Humidity (0 - 100%)
    values[0] = adc.read_adc(0,gain=GAIN)
    #Ratio of 15 bit balue to max volts determines the volts
    Ch1volts = values[0]/32767.0*6.144 #battery
    #print 'Ch1 Bits', values[0]
    #print 'Battery Voltage ', Ch1volts
    BattVolt = Ch1volts
        
    #print 'Battery Voltage', BattVolt 
    
    values[1] = adc.read_adc(1,gain=GAIN)
    Ch2volts = values[1]/32767.0*6.144
    #print 'CH2 Bits  ', values[1]
    #print 'CH2 Volts  ', Ch2volts
    Flow = (Ch2volts-1)*0.8
    #print 'Flow (SLMP)', Flow

    values[2] = adc.read_adc(2,gain=GAIN)
    Ch3volts = values[2]/32767.0*6.144
    Pwr10V = Ch3volts
    #print 'CH2 Bits  ', values[1]
    #print '10V Pwr Volts  ', Ch3volts

    
    os.chdir('/home/pi/temp/')
    temp_data_file = open('Batt&Flowlog.txt', 'a')
    temp_data_file.write(Date +','+ str(Ch1volts)+','+ str(Flow) +','+ str(Ch3volts) +','+'\n')
    temp_data_file.close()
    os.chdir('/home/pi/py2prog/')
    BT = 0
    if (BattVolt > 0.5):
        BT = 1
    return (BattVolt, Flow, Pwr10V)

def readi2cU9(Date):
    import os
    import numpy
    import time
    import datetime
    import Adafruit_ADS1x15
    adc = Adafruit_ADS1x15.ADS1115(address=0x48,busnum=1)
    GAIN = 1

    values=[0]*4
    values[0] = adc.read_adc(0,gain=GAIN)
    #print ('Value', values[0])
    #Ratio of 15 bit balue to max volts determines the volts
    Ch1volts = values[0]/32767.0*4.096 
    RH = Ch1volts/2.5*100
    #print('RH',RH)

    #print values[0]
    values[1] = adc.read_adc(1,gain=GAIN)
    Ch2volts = values[1]/32767.0*4.096
    TempC = (Ch2volts/2.5)*120-40
    #print('TempC',TempC)

    values[2] = adc.read_adc(2,gain=GAIN)
    PsysV = values[2]/32767.0*4.096
    Psys = (PsysV-0.5)/4*50
    #print('PsysV', PsysV)

    values[3] = adc.read_adc(3,gain=GAIN)
    PambV = values[3]/32767.0*4.096
    Pamb = (PambV-0.5)/4*15
    #print('PambV', PambV)

    os.chdir('/home/pi/temp/')
    temp_data_file = open('TRHP.txt', 'a')
    temp_data_file.write(Date+','+ str(RH)+','+str(TempC)+','+str(Psys)+','+str(Pamb) +'\n')
    temp_data_file.close()
    os.chdir('/home/pi/py2prog/')
    

    return(RH , TempC, Psys, Pamb)

def comValco(sendTo):
    import smbus
    import time
    import os

    time.sleep(1)
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
    #DLH_Data = bus.read_byte_data(devAddress, DLH) & 0xFFFF
    #print('DLH status Register String: ', hex(DLH_Data))
    #print('DDL Status Register String: ', hex(DLL_Data))

    #read MCR register
    MCR_w = 0x0 #0b00000000 clock prescaler = 1 bit 7 (0)

    #read IER register
    IER_w = 0x0 #0b00000000 all default
    bus.write_byte_data(devAddress, IER, IER_w)
    IER_Data = bus.read_byte_data(devAddress, IER) & 0xFFFF
    #print('IER Register String: ', hex(IER_Data)) #0x0 

    #Set LCR[7] to 0 and disable divisor
    LCR_w = 0x03 #0b00000011 #LCR bit [7] to enable divisor change
    #8 data bits 1 stop bit no parity
    bus.write_byte_data(devAddress, LCR, LCR_w)
    LCR_Data = bus.read_byte_data(devAddress, LCR) & 0xFFFF
    #print('LCR Register String: ', hex(LCR_Data)) #0x0
    

    EFCR = 0x0f #enhanced freatures control register
    #EFCR_w = 0x20 #try inverting the string??
    #bus.write_byte_data(devAddress, EFCR, EFCR_w)
    EFCR_Data = bus.read_byte_data(devAddress, EFCR) & 0xFFFF
    #print('EFCR Register String: ', hex(EFCR_Data)) #0x0 

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
        #print('HM CR')

    elif sendTo == 2:
        bus.write_byte_data(devAddress, RTHR, C)
        time.sleep(0.1)

        #write data to transmit
        bus.write_byte_data(devAddress, RTHR, W)
        time.sleep(0.1)

        #write data to transmit
        bus.write_byte_data(devAddress, RTHR, CR)
        time.sleep(0.1)
        #print('CW CR')

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
    #print('LSR Register String: ', hex(Status)) #0x0 

    time.sleep(1)
        
    #read Position from relply 
    Pos1 = bus.read_i2c_block_data(devAddress, RTHR,32) 
    #print('RT Register String: ', Pos1) #0x0
    time.sleep(0.1)

    #write position to MAIN log file
    time.sleep(0.1)
    RXLVL_Data = bus.read_byte_data(devAddress, RXLVL) & 0xFFFF
    #print('RXLVL Register String: ', hex(RXLVL_Data)) #0x0 

    time.sleep(0.5)

    #except(KeyboardInterrupt, SystemExit): #press control C
    bus.close

    #has valve moved? maybe check that and return a 1...or something
    return (Pos1[2], Pos1[3])

def comValco2(sendTo):
    import smbus
    import time

    time.sleep(1)
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
    DLH_w = 0x46 #no high byte needed

    #currently bus.write_byte_data acting like bus.write_word
    #i.e. you cannot write to the low and high byte sepereately. Whichever byte
    #is last written overwrites the other
    #similarly bus.read_byte_data is reading the whole word, not high and low bytes
    bus.write_byte_data(devAddress, DLL, DLL_w)
    #bus.write_byte_data(devAddress, DLH, DLH_w)
    DLL_Data = bus.read_byte_data(devAddress, DLL) & 0xFFFF
    DLH_Data = bus.read_byte_data(devAddress, DLH) & 0xFFFF
    #DLH_Data = bus.read_byte_data(devAddress, DLH) & 0xFFFF
    #print('DLH status Register String: ', hex(DLH_Data))
    print('DDL Status Register String: ', hex(DLL_Data))

    #read MCR register
    MCR_w = 0x0 #0b00000000 clock prescaler = 1 bit 7 (0)

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
    CR = 0xd
    A = 0x41
    C = 0x43
    D = 0x44
    H = 0x48
    I = 0x49
    M = 0x4d
    P = 0x50
    W = 0x57
    STAR = 0x2A

    #bus.write_byte_data(devAddress, RTHR, STAR)
    #time.sleep(0.2)

    #write data to transmit
    #bus.write_byte_data(devAddress, RTHR, I)
    #time.sleep(0.2)

    #write data to transmit
    #bus.write_byte_data(devAddress, RTHR, D)
    #time.sleep(0.1)

    #write data to transmit
    #bus.write_byte_data(devAddress, RTHR, STAR)
    #time.sleep(0.1)

    #write data to transmit
    #bus.write_byte_data(devAddress, RTHR, CR)
    #time.sleep(1)
        
    Position = bus.read_byte_data(devAddress, RTHR) &0xFFFF
    print('RT Register String: ', hex(Position)) #0x0

        
    #write data to transmit
    #for 2 pos valve CC A->B pos CW B->A pos
    if sendTo == 0:
        bus.write_byte_data(devAddress, RTHR, C)
        time.sleep(0.1)

        #write data to transmit
        bus.write_byte_data(devAddress, RTHR, W)
        time.sleep(0.1)

        #write data to transmit
        bus.write_byte_data(devAddress, RTHR, CR)
        time.sleep(0.2)
        #print('CW CR')

    RXLVL_Data = bus.read_byte_data(devAddress, RXLVL) & 0xFFFF
    print('RXLVL Register String: ', hex(RXLVL_Data)) #0x0 
    time.sleep(1)

    bus.write_byte_data(devAddress, RTHR, C)
    time.sleep(0.1)

    #write data to transmit
    bus.write_byte_data(devAddress, RTHR, P)
    time.sleep(0.1)

    #write data to transmit
    bus.write_byte_data(devAddress, RTHR, CR)
    time.sleep(1)
    
    #while 1:
        
    Pos2 = bus.read_i2c_block_data(devAddress, RTHR,32) 
    print('RT Register String: ', Position) #0x0
    time.sleep(0.1)

    RXLVL_Data = bus.read_byte_data(devAddress, RXLVL) & 0xFFFF
    print('RXLVL Register String: ', hex(RXLVL_Data)) #0x0 

    #write position to MAIN log file
    os.chdir('/home/pi/temp/')
    temp_data_file = open('RS232_reply_Test.txt', 'a') #CHANGE where this is writing to
    temp_data_file.write('Valve2 Position (A or B)'+'\n')
    for x in range(len(Pos)):
        temp_data_file.write(chr(Pos2[x]))
    
    temp_data_file.write('\n')
    temp_data_file.close()
    #except(KeyboardInterrupt, SystemExit): #press control C
    bus.close

    #Has valve moved? Check this and return a 1 or a 0...
    Moved = 1
    return Moved 

def comTriMini(Date):
    import os
    import smbus
    import time

    Data_chk =0

    time.sleep(1)
    bus = smbus.SMBus(1) #for Rpi 2B+ (pi zero bus = 0)

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
    #print('LCR Status Register String: ', hex(LCR_Data))


    EFR_w = 0x10 #0b00010000 Enable enhanced functions
    bus.write_byte_data(devAddress, EFR, EFR_w) #write data to EFR
    EFR_Data = bus.read_byte_data(devAddress, EFR)
    #print('EFR Status Register String: ', hex(EFR_Data))

    LCR_w = 0x83 #0b10000011 #LCR bit [7] to enable divisor change
    #8 data bits 1 stop bit no parity
    bus.write_byte_data(devAddress, LCR, LCR_w)
    LCR_Data = bus.read_byte_data(devAddress, LCR)
    #print('LCR Status Register String: ', hex(LCR_Data))

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
    #print('DDH status Register String: ', hex(DLH_Data))
    #print('DDL Status Register String: ', hex(DLL_Data))

    #read MCR register
    MCR_w = 0x0 #0b00000000 clock prescaler = 1 bit 7 (0)
    MCR_Data = bus.read_byte_data(devAddress, MCR)
    #print('MCR Status Register String: ', hex(MCR_Data))

    #read IER register
    IER_w = 0x0 #0b00000000 all default
    bus.write_byte_data(devAddress, IER, IER_w)
    IER_Data = bus.read_byte_data(devAddress, IER) & 0xFFFF
    #print('IER Register String: ', hex(IER_Data)) #0x0 

    #Set LCR[7] to 0 and disable divisor
    LCR_w = 0x03 #0b00000011 #LCR bit [7] to enable divisor change
    #8 data bits 1 stop bit no parity
    bus.write_byte_data(devAddress, LCR, LCR_w)
    LCR_Data = bus.read_byte_data(devAddress, LCR) & 0xFFFF
    #print('LCR Register String: ', hex(LCR_Data)) #0x0 

   
    RXLVL_Data = bus.read_byte_data(devAddress, RXLVL) & 0xFFFF
    #print('RXLVL Register String: ', hex(RXLVL_Data)) #0x0 


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
    
    #exit and go back to recieing data
    data = [101,120,105,116,13]
    bus.write_i2c_block_data(devAddress, RTHR, data)
    
    #read data from holding register
    time.sleep(1)
    try:
        for y in range(30):        
            Winds = bus.read_i2c_block_data(devAddress, RTHR,32) #&0xFFFF
            #print('RT Data Register String: ', Winds) #0x0

            RXLVL_Data = bus.read_byte_data(devAddress, RXLVL) & 0xFFFF
            #print('RXLVL Register String: ', hex(RXLVL_Data)) #0x0
           

            #write position to Trisonica log file
            os.chdir('/home/pi/temp/')
            temp_data_file = open('TrisonicaWinds.txt', 'a') 
            for x in range(len(Winds)):
                #print(chr(Winds[x]))
                temp_data_file.write(chr(Winds[x]))
    
            temp_data_file.write('\n')
            #write Sample Date to Trisonica log file
            temp_data_file.write(Date + '\n')

            temp_data_file.close()
            Data_chk = Winds[1]
            time.sleep(0.105)

        #print('RT Data Register String: ', Winds) #0x0

        
            #5 Hz data... so aquire it 300 times
    except(KeyboardInterrupt, SystemExit): #press control C
        print('block read aborted')

    
    bus.close
    #maybe just return some part of Winds string
    return Data_chk
