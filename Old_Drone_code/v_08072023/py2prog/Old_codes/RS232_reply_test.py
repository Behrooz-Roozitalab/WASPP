import os

Pos = [66, 67, 32, 68, 75, 32]
os.chdir('/home/pi/temp/')
temp_data_file = open('RS232_reply_Test.txt', 'a')

for x in range(len(Pos)):
    temp_data_file.write(chr(Pos[x]))
    
temp_data_file.write('\n')
temp_data_file.close()

Pos = [66, 67, 32, 68, 75, 32]

os.chdir('/home/pi/temp/')
temp_data_file = open('RS232_reply_Test.txt', 'a')

for x in range(len(Pos)):
    temp_data_file.write(chr(Pos[x]))
    
temp_data_file.write('\n')
temp_data_file.close()
