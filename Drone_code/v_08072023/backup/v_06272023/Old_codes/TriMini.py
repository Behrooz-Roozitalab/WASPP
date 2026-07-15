import serial
import os
import time
import UWASmod_v1

tri = serial.Serial('/dev/ttyUSB0',
                    baudrate = 115200,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize = serial.EIGHTBITS,
                    timeout=1)
os.chdir('/home/pi/temp/')
#open file and write header
try:
        number = 0
        while (number < 10): #2 Hz output writing data...
            data = tri.readline()
            data = tri.readline()
            print(data)
            temp_data_file = open('Trisonica_mini_Log.txt', 'a')
            temp_data_file.write(data+'\n')
            number = number + 1
            time.sleep(0.1)
            temp_data_file.close()
            os.chdir('/home/pi/temp/')
        #os.system("sudo poweroff")
except(KeyboardInterrupt, SystemExit): #press CNTRL Cexcept
    print('abort shutdown') 
