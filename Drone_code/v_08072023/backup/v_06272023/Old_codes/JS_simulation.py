#!/usr/bin/python2

# Import necessary libraries
import UWASmod_v1
import time
import numpy
import os

# Waypoints for the flight plan
# Waypoint: (lat, lon, alt)
waypoints = [(0,0,120), (0,0,60), (0,0,10)]

# Logging location
log_folder = '/home/pi/logs/'
log_testing = 'UWAS_SamplingLog_test.txt'
log_sampling = 'UWAS_SamplingLog.txt'
data_sample = 'UWAS_Data_Sampling.csv'

# Minimum number of satellites for Configuration
no_sat = 6

# Number of tries to get the GPS
try_gps_num = 10

# Battery Threshold
BAT_threshold = 3.65

# DP Threshold
DP_threshold = 2

# Flow Threshold
Flow_threshold = 0.3

# Searching num
search_no = 1200  # Approx. 600 + alpha sec for each way point searching

# Distance for searching
lat_diff = 0.5
lon_diff = 0.5
alt_diff = 50

# Flushing time
flushing_time = 5

###########################
##### TESTING SENSORS #####
###########################

print('------------------TESTING SENSORS------------------')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_testing,'a')
temp_data_file.write('----Start Testing Sensors----\n')
temp_data_file.close()

### Testing gps data ###
gpsData = UWASmod_v1.GPSsetup()
Date, Lat, Lon, Alt, sat = gpsData[0], gpsData[1], gpsData[2], gpsData[3], gpsData[4] # Date format is hhmmss.ss

print('>>>> Testing gps:')
print('Date: ' + str(Date) + ', Lat: ' + str(Lat) + ', Lon: ' + str(Lon) + ', Alt: ' + str(Alt) + ', sat: ' + str(sat))
if len(Lat)==0 or len(Lon)==0 or len(Alt)==0 or len(sat)==0:
  print('Warning: Cannot receive gps data from satellite')
print('')
print('')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_testing,'a')
temp_data_file.write('>>>> Testing gps:\n')
temp_data_file.write('Date: ' + str(Date) + ', Lat: ' + str(Lat) + ', Lon: ' + str(Lon) + ', Alt: ' + str(Alt) + ', sat: ' + str(sat) + '\n')
temp_data_file.write('\n')
temp_data_file.close()


### Testing wind sensor (TriSonica Mini Wind & Weather Sensor) ###
Data_chk = UWASmod_v1.comTriMini(Date)

print('>>>> Testing wind sensor:')
print('Wind: ' + str(Data_chk))
if Data_chk==0:
  print('Warning: Current wind is 0')
print('')
print('')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_testing,'a')
temp_data_file.write('>>>> Testing wind sensor:\n')
temp_data_file.write('Wind: ' + str(Data_chk) + '\n')
temp_data_file.write('\n')
temp_data_file.close()


### Testing programRunning function ****Ask Question**** ###
runningNow = UWASmod_v1.programRunning(1)

print('>>>> Testing programRunning function:')
print('runningNow: ' + str(runningNow))
print('')
print('')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_testing,'a')
temp_data_file.write('>>>> Testing programRunning function:\n')
temp_data_file.write('runningNow: ' + str(runningNow) + '\n')
temp_data_file.write('\n')
temp_data_file.close()


### Testing communication with Valco Valve ###
sendTo = 0
Pos1 = UWASmod_v1.comValco(sendTo)

print('>>>> Testing communication with Valco Valve:')
print('Current position: ' + chr(Pos1[0]) + chr(Pos1[1]))
print('')
print('')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_testing,'a')
temp_data_file.write('>>>> Testing communication with Valco Valve:\n')
temp_data_file.write('Current position: ' + chr(Pos1[0]) + chr(Pos1[1]) + '\n')
temp_data_file.write('\n')
temp_data_file.close()


### Testing Battery (Thermistor T) ****Ask Question**** ###
BT = UWASmod_v1.readi2cU10(Date)

print('>>>> Testing battery:')
print('Battery voltage: ' + str(BT[0]) + ', Flow: ' + str(BT[1]) + ', Pwr10V: ' + str(BT[2]))
print('')
print('')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_testing,'a')
temp_data_file.write('>>>> Testing battery:\n')
temp_data_file.write('Battery voltage: ' + str(BT[0]) + ', Flow: ' + str(BT[1]) + ', Pwr10V: ' + str(BT[2]) + '\n')
temp_data_file.write('\n')
temp_data_file.close()


### Testing Temp/Humidity sensors ####
TRH = UWASmod_v1.readi2cU9(Date)
RH, Temp, pSys, pAmb = TRH[0], TRH[1], TRH[2], TRH[3]

print('>>>> Testing Temp/Humidity sensors:')
print('RH: ' + str(RH) + ', Temp: ' + str(Temp) + ', pSys: ' + str(pSys) + ', pAmb: ' + str(pAmb))

# Logging
os.chdir(log_folder)
temp_data_file = open(log_testing,'a')
temp_data_file.write('>>>> Testing Temp/Humidity sensor:\n')
temp_data_file.write('RH: ' + str(RH) + ', Temp: ' + str(Temp) + ', pSys: ' + str(pSys) + ', pAmb: ' + str(pAmb) + '\n')
temp_data_file.write('\n')
temp_data_file.close()

# Testing sensors using testSensors function
sensors = UWASmod_v1.testSensors(RH, Temp, pSys, pAmb)
print('Sensors are OK (1) or not OK (0): ' + str(sensors))
print('')
print('')

### Testing pump on/off ###
# **** checking current position and configure if necessary ****
# have to start from odd number position

print('>>>> Testing Pump on/off:')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_testing,'a')
temp_data_file.write('>>>> Testing Pump on/off:\n')

# Pump on
onOff = 1 # turn the pump on
PumpStatus = UWASmod_v1.pumpOn(onOff)
print('Pump is On ------> Wait for 5 sec')
# Logging
temp_data_file.write('Pump On: ' + str(PumpStatus) + '\n')

time.sleep(5)

# Pump off
onOff = 0 # turn the pump off
PumpStatus = UWASmod_v1.pumpOn(onOff)
print('Pump is off')
# Logging
temp_data_file.write('Pump off: ' + str(PumpStatus) + '\n')
temp_data_file.write('----End Testing Sensors----\n\n')
temp_data_file.close()

print('------------------END TESTING SENSORS------------------')
print('')
print('')
print('')

###########################
#####  Configuration  #####
###########################

### Configure GPS ###

print('------------------START CONFIGURATION------------------')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_sampling, 'a')
temp_data_file.write('----Start Configuration----\n')
temp_data_file.write('\n')
temp_data_file.close()


# Getting GPS data until number of GPS staellites is greater than no_sat
# Try try_gps_num times and abort the program (default: 100 times)

print('>>>> Start Configuring GPS')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_sampling, 'a')
temp_data_file.write('>>>> Start Configuring GPS\n')
temp_data_file.close()

# Try try_gps_num times
for try_gps in range(try_gps_num):
  # Getting GPS data
  gpsData = UWASmod_v1.GPSsetup()
  Sat = float(gpsData[4])

  # if number of sat is greater than the threshold
  if Sat>no_sat:
    
    print('Configuration GPS success!!!!')
    print('Num of GPS satellites: ' + str(Sat))
    print('')
    print('')
    
    # Logging
    os.chdir(log_folder)
    temp_data_file = open(log_sampling, 'a')
    temp_data_file.write('Configuring GPS success!!!!\n')
    temp_data_file.write('Num of GPS satellites: ' + str(Sat) + '\n')
    temp_data_file.write('\n')
    temp_data_file.close()
    
    break


# If GPS configuration fails
if try_gps == try_gps_num-1:

  print('Configuration GPS fails')
  print('Num of GPS satellites: ' + str(Sat))
  print('Shutting Down....')
  print('')
  print('')
  
  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('Configuring GPS fails....\n')
  temp_data_file.write('Num of GPS satellites: ' + str(Sat) + '\n')
  temp_data_file.write('Shutting Down....' + '\n')
  temp_data_file.write('\n')
  temp_data_file.close()

  # Shut down the system
  ##### ****UWASmod_v1.softShutdown()****  

### Configure Battery ###

print('>>>> Start Configuring Battery')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_sampling, 'a')
temp_data_file.write('>>>> Start Configuring Battery\n')
temp_data_file.close()

BAT = BT[0]

if BAT < BAT_threshold:
  print('Battery lower than threshold...')
  print('Current Battery: ' + str(BAT))
  print('Threshold: ' + str(BAT_treshold))
  print('Shutting down...')
  print('')
  print('')

  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('Battery lower than threshold...\n')
  temp_data_file.write('Current Battery: ' + str(BAT) + '\n')
  temp_data_file.write('Threshold: ' + str(BAT_threshold) + '\n')
  temp_data_file.write('Shutting down...\n')
  temp_data_file.write('\n')
  temp_data_file.close()
  
  # Shut down the system
  ##### ****UWASmod_v1.softShutdown()****    
else:
  # Battery OK sign
  print('Battery higher than threshold!!!')
  print('Current Battery: ' + str(BAT))
  print('Threshold: ' + str(BAT_threshold))
  print('')
  print('')

  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('Battery higher than threshold!!!\n')
  temp_data_file.write('Current Battery: ' + str(BAT) + '\n')
  temp_data_file.write('Threshold: ' + str(BAT_threshold) + '\n')
  temp_data_file.write('\n')
  temp_data_file.close()

  UWASmod_v1.batteryOK(BAT)

### Configure Flow & Pressure ###

print('>>>> Start Configuring Flow & Pressure')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_sampling, 'a')
temp_data_file.write('>>>> Start Configuring Flow & Pressure\n')
temp_data_file.close()

# Get data
Flow = BT[1]
pSys = TRH[2]
pAmb = TRH[3]
DP = abs(pSys-pAmb)

if not ((DP>DP_threshold) & (Flow>Flow_threshold)):
  print('Either Flow or DP does not satisfy threshold...')
  print('DP: ' + str(DP))
  print('DP threshold: ' + str(DP_threshold))
  print('Flow: ' + str(Flow))
  print('Flow threshold: ' + str(Flow_threshold))
  print('Shutting down...')

  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('Either Flow or DP does not satisfy threshold...\n')
  temp_data_file.write('DP: ' + str(DP) + '\n')
  temp_data_file.write('DP threshold: ' + str(DP_threshold) + '\n')
  temp_data_file.write('Flow: ' + str(Flow) + '\n')
  temp_data_file.write('Flow threshold: ' + str(Flow_threshold) + '\n')
  temp_data_file.write('Shutting down...\n')
  temp_data_file.write('\n')
  temp_data_file.close()
  
  # Shut down the system
  ##### ****UWASmod_v1.softShutdown()****

# Signaling that pump is working
pumpWorks = 1
UWASmod_v1.pumpTest(pumpWorks)

print('------------------END CONFIGURATION------------------')
print('')
print('')
print('')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_sampling, 'a')
temp_data_file.write('Successfully comeplete configuration\n')
temp_data_file.write('----End Configuration----\n')
temp_data_file.write('\n')
temp_data_file.write('\n')
temp_data_file.close()

   
###########################
#####    Operating    #####
###########################

print('------------------START OPERATION------------------')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_sampling, 'a')
temp_data_file.write('----Start Operation----\n')
temp_data_file.write('\n')
temp_data_file.close()

# Retreiving initial GPS
gpsData = UWASmod_v1.GPSsetup()

# When recieving valid GPS data 
if len(gpsData[1])!=0 and len(gpsData[2])!=0 and len(gpsData[3])!=0:
  Lat_init, Lon_init, Alt_init = float(gpsData[1]), float(gpsData[2]), float(gpsData[3])
else:
  Lat_init, Lon_init, Alt_init = 0.0, 0.0, 0.0

print('>>>> Retreiving initial GPS')
print('Lat(init): ' + str(Lat_init) + ', Lon(init): ' + str(Lon_init) + ', Alt(init): ' + str(Alt_init))
print('')
print('')

# Logging
os.chdir(log_folder)
temp_data_file = open(log_sampling, 'a')
temp_data_file.write('>>>> Retreiving initial GPS\n')
temp_data_file.write('Lat(init): ' + str(Lat_init) + ', Lon(init): ' + str(Lon_init) + ', Alt(init): ' + str(Alt_init) + '\n\n')
temp_data_file.close()


### Search for target way points and Start sampling ###
print('>>>> Search for target way points & Start sampling')
# Logging
os.chdir(log_folder)
temp_data_file = open(log_sampling, 'a')
temp_data_file.write('>>>> Search for target way points & Start sampling\n')
temp_data_file.close()

for wp in range(len(waypoints)):
  # Getting current target waypoint
  curr_target_lat = waypoints[wp][0]
  curr_target_lon = waypoints[wp][1]
  curr_target_alt = waypoints[wp][2]
  
  print('------- WP ' + str(wp+1) + ' -------')
  print('Current target WP: (' + str(curr_target_lat) + ', ' + str(curr_target_lon) + ', ' + str(curr_target_alt) + ')')
  
  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('------- WP' + str(wp+1) + ' -------\n')
  temp_data_file.write('Current target WP: (' + str(Lat_init + curr_target_lat) + ', ' + str(Lon_init + curr_target_lon) + ', ' + str(Alt_init + curr_target_alt) + ')\n')
  temp_data_file.close()

  # Start searching
  for s in range(search_no):
    print('>>>>>>> Searching attempt ' + str(s+1) + ' >>>>>>>')
    
    # Getting GPS
    Date = gpsData[0]

    # When recieving valid GPS data 
    if len(gpsData[1])!=0 and len(gpsData[2])!=0 and len(gpsData[3])!=0:
      Lat_curr, Lon_curr, Alt_curr = float(gpsData[1]), float(gpsData[2]), float(gpsData[3])
    else:
      Lat_curr, Lon_curr, Alt_curr = 0.0, 0.0, 0.0
    
    ###### For Simulation purpose #######
    # After 20 searches, location will match
    if s == 20:
      Lat_curr = Lat_init + curr_target_lat
      Lon_curr = Lon_init + curr_target_lon
      Alt_curr = Alt_init + curr_target_alt
    ###### For Simulation purpose #######  
    
    # Calculating Difference
    Dlat = abs(Lat_init + curr_target_lat - Lat_curr)
    Dlon = abs(Lon_init + curr_target_lon - Lon_curr)
    Dalt = abs(Alt_init + curr_target_alt - Alt_curr)

    time.sleep(0.5)

    # Check whether we reach the way point within certain distance
    Match = ((Dlat<lat_diff) & (Dlon<lon_diff)) & (Dalt<alt_diff)
    if Match==1:
      break

  print('>>>>>>> Searching successful at attempt ' + str(s+1) + ' >>>>>>>')
  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('>>>>>>> Searching successful at attempt ' + str(s+1) + ' >>>>>>>\n') 
  temp_data_file.close()

  # Turn pump on
  onOff = 1
  PumpStatus = UWASmod_v1.pumpOn(onOff)
  
  print('....... Pum On: Sampling at WP ' + str(wp+1) + ' .......')
  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('....... Pum On: Sampling at WP ' + str(wp+1) + ' .......\n')
  temp_data_file.close()

  # Getting start data (GPS, Batt, Flow, 10V, RH, T, Psys, Pamb)
  gpsData_start = UWASmod_v1.GPSsetup()
  Date_start = gpsData_start[0]
  BT_start = UWASmod_v1.readi2cU10(Date_start)
  TRH_start = UWASmod_v1.readi2cU9(Date_start)

  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('Start GPS (Date, lat, lon, alt): ' + str(Date_start) + ',' + str(gpsData_start[1]) + ',' + str(gpsData_start[2]) + ',' + str(gpsData_start[3]) + ',' + str(gpsData_start[4]) + '\n')
  temp_data_file.write('Start Batt, Flow, 10V: ' + str(BT_start[0]) + ',' + str(BT_start[1]) + ',' + str(BT_start[2]) + '\n') 
  temp_data_file.write('Start RH, T, Psys, Pamb: ' + str(TRH_start[0]) + ',' + str(TRH_start[1]) + ',' + str(TRH_start[2]) + ',' + str(TRH_start[3]) + '\n')
  temp_data_file.close()

  # Moving poisition & Filling canister
  sendTo = 2 # increment position to odd number where canister is connected
  Pos1_start = UWASmod_v1.comValco(sendTo)
  print('...... Start filling Pos: ' + str(chr(Pos1_start[0])) + str(chr(Pos1_start[1])))
  
  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('...... Start filling Pos: ' + str(chr(Pos1_start[0])) + str(chr(Pos1_start[1])) + '\n')
  temp_data_file.close()

  # Flushing
  for z in range(flushing_time): # 15--> ~1:30
    Winds = UWASmod_v1.comTriMini(Date_start) # Why use this? Not time.sleep? **********

  time.sleep(1)
  
  # Moving position
  sendTo = 2 # increment position to even number where there is no canister
  Pos1_end = UWASmod_v1.comValco(sendTo)
  
  # Getting end data
  gpsData_end = UWASmod_v1.GPSsetup()
  Date_end = gpsData_end[0]
  BT_end = UWASmod_v1.readi2cU10(Date_end)
  TRH_end = UWASmod_v1.readi2cU9(Date_end)
  
  # Turn pump off
  onOff = 0
  PumpStatus = UWASmod_v1.pumpOn(onOff)
  
  # Logging
  os.chdir(log_folder)
  temp_data_file = open(log_sampling, 'a')
  temp_data_file.write('End GPS (Date, lat, lon, alt): ' + str(Date_end) + ',' + str(gpsData_end[1]) + ',' + str(gpsData_end[2]) + ',' + str(gpsData_end[3]) + ',' + str(gpsData_end[4]) + '\n')
  temp_data_file.write('Start Batt, Flow, 10V: ' + str(BT_end[0]) + ',' + str(BT_end[1]) + ',' + str(BT_end[2]) + '\n') 
  temp_data_file.write('Start RH, T, Psys, Pamb: ' + str(TRH_end[0]) + ',' + str(TRH_end[1]) + ',' + str(TRH_end[2]) + ',' + str(TRH_end[3]) + '\n')
  temp_data_file.write('Valco Position now: ' + str(chr(Pos1_end[0])) + str(chr(Pos1_end[1])) + '\n')
  temp_data_file.write('...... WP ' + str(wp+1) + ' successfully complete ......\n\n')
  temp_data_file.close()

  # Saving data
  # Format: waypoint,Date_start,Date_end,lat_start,lat_end,lon_start,lon_end,alt_start,alt_end,BT_start,BT_end,Flow_start,Flow_end,10V_start,10V_end,RH_start,RH_end,T_start,T_end,Psys_start,Psys_end,Pamb_start,Pamb_end,valco_pos
  #os.chdir(log_foler)
  #temp_data_file = open(data_sampling, 'a')
  #temp_date_file = write(str(Date_start)+','+str(Date_end)+','+str(gpsData_start

  time.sleep(6)
  

  