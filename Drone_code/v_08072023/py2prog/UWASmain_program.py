''' UWASmain_program.py
Description: 
    This program runs a set of intstructions during drone flight for sampling canisters.
    Waypoints where samples are collected are pre-determined.
    Overall flow of the program is:
      1. Test a set of sensors and abort the program if the test fails
      2. Configure the system (e.g., setting GPS) and abor the program if there the configuration fails
      3. Operate the sampling system (Loop over way points)
        3-1. Search for target way points
        3-2. If the drone approaches to the target close enough, start sampling.
        3-3. Sampling procedure
          a. Pump on
          b. Record sensor data (Sampling start)
          c. Move Valco position to odd number and fill a canister
             Flush for a certain time
          d. Move Valco position to even number
          e. Record sensor data (Sampling end)
          f. Pump off
      4. Save relevant data in csv file

Output files:
    testing_log.txt
    sampling_log.txt
    sampling_data.csv
'''
#!/usr/bin/python2

# Import necessary libraries
import time
import numpy
import os
import sys
import argparse
import csv
import math
from Hdwcom import GPScom, Windcom, RunSignal, Valcocom, ADCcom, Pumpcom

# Parameter configuration file
CONF = '/home/pi/configs/conf.csv'

# Default value for waypoints
DEFAULT_WAYPOINTS = [(0,0,120), (0,0,60), (0,0,10)]

# Simulation Flag
'''
In simulation mode, system will not shut down even if test & configuration fails
In addition, the system will search for each way point 20 times and assume that it reaches the target
  0: Field experiment
  1: Simulation in lab
'''
SIM_FLAG = 0

# A dictionary for parameters
PARAMS = {}

def config_params():
  '''
  This function configures parameters for this program.
  The list of parameters configured by this function is follows:
  1. LOG_FOLDER: Logging folder
  2. LOG_TESTING: Logging file for testing sensors
  3. LOG_SAMPLING: Logging file for configuration & operation steps
  4. DATA_FOLDER: Data storage folder
  5. DATA_SAMPLING: Data file for analysis
  6. NO_SAT: Minimum number of satellite
  7. TRY_GPS_NUM: Number of tries to get the GPS
  8. BAT_THRES: Battery Threshold for configuration
  9. DP_THRES: DP Threshold for configuration
  10. FLOW_THRES: Flow Threshold for configuration
  11. SEARCH_NO: Number of searching for each waypoint
                 Approx. 600 + alpha sec for each way point searching
  12. LAT_DIFF: Tolerance range for latitude during searching
  13. LON_DIFF: Tolerance range for longitude during searching
  14. ALT_DIFF: Tolerance range for altitude during searching
  15. FLUSHING_NO: Flushing time for each sampling

  Input:
  Output:
  Only modify PARAM global variable
  '''
  with open(CONF, mode='r') as file:
    csvFile = csv.reader(file)
    for line in csvFile:
      # If value is numeric
      if line[1].replace('.','',1).replace('-','',1).isdigit():     
        if math.floor(float(line[1])) == float(line[1]):
          # if it is integer
          PARAMS[line[0]] = int(line[1])
        else:
          # if it is float
          PARAMS[line[0]] = float(line[1])
      else:
        # if it is string
        PARAMS[line[0]] = line[1]

def write_files(folder, file, messages):
  '''
  This function writes txt or csv files for recording.
  It writes a list of messages line by line

  Input:
  folder>> a folder to write
  file>> a file to write on
  meassges>> a list of messages (doesn't have \n character in each message)
  
  Output:
  Only modify a file specified by folder & file variables
  '''
  os.chdir(folder)
  temp_data_file = open(file, 'a')
  for message in messages:
    temp_data_file.write(message + '\n')
  temp_data_file.close()

def print_msg(messages):
  '''
  This function prints out a list of messages line by line

  Input:
  messages>> a list of messages

  Output:
  None
  '''
  for message in messages:
    print(message)

def testing_sensors():
  '''
  This function conducts a series of testings on sensors.
  - GPS
  - Wind
  - Valco Valve
  - Battery & Flow (Thermistor)
  - Temp/Humidity/Pressure sensors
  - Testing each sensor's data
  - Testing pump / Signal
  - Program running singal
  ''' 
  messages = ['------------------TESTING SENSORS------------------',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
  
  ### Getting GPS data ###
  gpsData = GPScom.getGPS()
  Date, Lat, Lon, Alt, sat = gpsData[0], gpsData[1], gpsData[2], gpsData[3], gpsData[4] # Date format is hhmmss.ss
  
  messages = ['>>>>>> Testing GPS:',
              'Date: ' + str(Date) + ', Lat: ' + str(Lat) + ', Lon: ' + str(Lon) + ', Alt: ' + str(Alt) + ', sat: ' + str(sat),
              '',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

  ### Getting wind sensor (TriSonica Mini Wind & Weather Sensor) ###
  wind = Windcom.getWind(Date)
  
  messages = ['>>>>>> Testing wind sensor:',
              'Date: ' + str(Date) + ', wind: ' + str(wind),
              '',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)            

  
  ### Communicating with Valco Valve ###
  sendTo = 0 # Getting current position
  Pos1 = Valcocom.comValco(sendTo)

  messages = ['>>>>>> Testing Valco Valve:',
              'Current Position: ' + chr(Pos1[0]) + chr(Pos1[1]),
              '',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

  ### Testing Battery & Flow (Thermistor) ###
  BT = ADCcom.readADC_bat_flow(Date)
  
  messages = ['>>>>>> Testing Battery & Flow:',
              'Battery voltage: ' + str(BT[0]),
              'Flow: ' + str(BT[1]),
              'Pwr10V: ' + str(BT[2]),
              '',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

  ### Testing Temp/Humidity/Pressure sensors ###
  TRH = ADCcom.readADC_temp_rh_ps_pa(Date)
  RH, Temp, pSys, pAmb = TRH[0], TRH[1], TRH[2], TRH[3]

  messages = ['>>>>>> Testing Temp/Humidity/Pressure:',
              'RH: ' + str(RH),
              'Temp: ' + str(Temp),
              'pSys: ' + str(pSys),
              'pAmb: ' + str(pAmb),
              '',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
  
  ### Testing each sensor's data ###
  # Output: [pSysTest, pAmbTest, TempTest, RHTest, BTTest, ComTest, Overall]
  # sensors[0]: 0 - pass, 1 - pSys < 8
  # sensors[1]: 0 - pass, 2 - pAmb < 8
  # sensors[2]: 0 - pass, 3 - Temp < -5
  # sensors[3]: 0 - pass, 4 - RH < 2
  # sensors[4]: 0 - pass, 5 - BT < 3.65
  # sensors[5]: 0 - pass, 6 - abs(pSys-pAmb) > 1 # prior to pump test, system pressure and ambient pressure should be equal
  # sensors[6]: 0 - All pass, 1 - At least one test fails
  # Light on D4 & D6 (D4: Battery OK, D6: All sensor OK)
  sensors = RunSignal.testSensors(RH, Temp, pSys, pAmb, BT[0])
  
  messages = ['>>>>>> Testing sensors:',
              'Test Results: ' + str(sensors),
              '',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

  ### Testing pump ###
  onOff = 1
  PumpStatus = Pumpcom.pumpOn(onOff)
  
  messages = ['>>>>>> Testing pump:',
              'Pump is On, Pump Status: ' + str(PumpStatus),
              '------ Wait for 5 sec ------']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

  time.sleep(5)
  
  onOff = 0
  PumpStatus = Pumpcom.pumpOn(onOff)

  messages = ['Pump is Off, Pump Status: ' + str(PumpStatus)]
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
  
  # Signal the success of pump test (Light on D7)
  PumpWorks = 1
  RunSignal.pumpTestSig(PumpWorks) # D7 lights on

  messages = ['Pump test Success!!!']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

  ### Program running singal ###
  # Should be modified when all thresholds are set and sensors are working
  runningNow = RunSignal.programRunning(1)  # D5 lights on

  messages = ['------------------END TESTING SENSORS------------------',
             '',
             '',
             '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

def config_system(wayPoints):
  '''
  This function conducts a series of final tests on sensors.
  If any of tests fails, it shutdowns the system & Raspberry pi.
  - Waypoints # If there are more then 16 waypoints, shut down the program
  - GPS
  - Battery
  - Flow & Pressure
  - Valco valve position   # Set the initial position to 16 to ensure that first sampling position is always 01   
  '''

  messages = ['------------------START CONFIGURATION------------------',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

  ### Check the number of waypoints ###
  # If there are more then 8 waypoints, shut down the program
  messages = ['>>>>>> Checking the number of waypoints:']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
  
  if len(wayPoints)>8:
    messages = ['Number of waypoints should be less than 9...',
                'Number of waypoints: ' + str(len(wayPoints)),
                '......SHUTTING DOWN......',
                '',
                '']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
 
    # Shut down the program & Raspberry pi
    if SIM_FLAG==0:
      messages = ['Quit for Number of waypoints']
      print_msg(messages)
      write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
      # quit()
      # softshutdown()
  else:
    messages = ['Number of waypoints: ' + str(len(wayPoints)),
                '',
                '']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
    

  ### Configure GPS ### 
  # Getting GPS data until number of GPS satellites is greater than NO_SAT
  # Try TRY_GPS_NUM times and abort the program (default: 100 times)
  messages = ['>>>>>> Configuring GPS:']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

  flag = 0
  # Try TRY_GPS_NUM times
  for _ in range(PARAMS['TRY_GPS_NUM']):
    # Getting GPS data
    gpsData = GPScom.getGPS()
    sat = float(gpsData[4])

    # if number of satellites is greater than the threshold
    if sat > PARAMS['NO_SAT']:
      messages = ['Configuring GPS SUCCESS!!!',
                  'Num of satellites: ' + str(sat),
                  '',
                  '']
      print_msg(messages)
      write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
      flag = 1
      break

  # If GPS configuration fails
  if flag == 0:
    messages = ['Configuring GPS FAILS...',
                'Num of satellites: ' + str(sat),
                '......SHUTTING DOWN......',
                '',
                '']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
    # Shut down the program & Raspberry pi
    if SIM_FLAG==0:
      messages = ['Quit for Number of satellites']
      print_msg(messages)
      write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
      # quit()
      # softshutdown()

  ### Configure Battery ###
  messages = ['>>>>>> Configuring Battery:']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
  
  BT = ADCcom.readADC_bat_flow(gpsData[0])
  BAT = BT[0]
  if BAT < PARAMS['BAT_THRES']:
    messages = ['Configuring Battery FAILS...',
                'Battery Volt: value(' + str(BAT) + ') > threshold(' + str(PARAMS['BAT_THRES']) + ')',
                '......SHUTTING DOWN......',
                '',
                '']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
    # Shut down the program & Raspberry pi
    if SIM_FLAG==0:
      messages = ['Quit for Battery']
      print_msg(messages)
      write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
      # quit()
      # softshutdown()
  else:
    messages = ['Configuring Battery SUCCESS!!!',
                'Battery Volt: value(' + str(BAT) + ') > threshold(' + str(PARAMS['BAT_THRES']) + ')',
                '',
                '']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

  ### Configure Flow & Pressure ###
  messages = ['>>>>>> Configuring Flow & Pressure:']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
  
  # Reading sensors' data
  BT = ADCcom.readADC_bat_flow(gpsData[0])
  TRH = ADCcom.readADC_temp_rh_ps_pa(gpsData[0])

  Flow = BT[1]
  pSys = TRH[2]
  pAmb = TRH[3]
  DP = abs(pSys-pAmb) 
  
  if not ((DP>PARAMS['DP_THRES']) & (Flow>PARAMS['FLOW_THRES'])):
    messages = ['Configuring Flow & Pressure FAILS...',
                'Diff between pSys & pAmb: value(' + str(DP) + ') > threshold(' + str(PARAMS['DP_THRES']) + ')',
                'Flow: value(' + str(Flow) + ') > threshold(' + str(PARAMS['FLOW_THRES']) + ')',
                '......SHUTTING DOWN......',
                '',
                '']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
    # Shut down the program & Raspberry pi
    if SIM_FLAG==0:
      messages = ['Quit for DP']
      print_msg(messages)
      write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
      # quit()
      # softshutdown()
  else:
    messages = ['Configuring Flow & Pressure SUCCESS!!!',
                'Diff between pSys & pAmb: value(' + str(DP) + ') > threshold(' + str(PARAMS['DP_THRES']) + ')',
                'Flow: value(' + str(Flow) + ') > threshold(' + str(PARAMS['FLOW_THRES']) + ')',
                '',
                '']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
    

#  ### Configure Valco valve initial position ###
#  # Set the initial position to 16 to ensure that first sampling position is always 01   
#  messages = ['>>>>>> Configuring initial position of Valco valve:']
#  print_msg(messages)
#  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)

#  sendTo = 0
#  for _ in range(16):
#    pos = Valcocom.comValco(sendTo)
#    pos = chr(pos[0]) + chr(pos[1])
#    
#    if pos == '16':
#      messages = ['Configuring initial Valco valve initial position SUCCESS!!!',
#                  'Initial Valco valve position: ' + str(pos),
#                  '',
#                  '']
#      print_msg(messages)
#      write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
#      break
#    sendTo = 2
#    pos = Valcocom.comValco(sendTo)   

  messages = ['------------------END CONFIGURATION------------------',
             '',
             '',
             '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_TESTING'], messages)
            
def operate_system(wayPoints):
  '''
  This function conducts a series of steps for sampling.
  For each way point, it checks current position SEARCH_NO times 
  to see if the drone approaches to the point within LAT_DIFF, LON_DIFF, and ALT_DIFF range.
  If the drone approaches the point, it starts the sampling process:
    1. Turn on pump
    2. Record sensor data (Start)
    3. Move Valco valve position (even to odd) &
       Fill a canister
    4. Move Valco valve position (odd to even)
    5. Record sensor data (End)
    6. Turn off pump
    7. Save data for analysis
  '''
  messages = ['------------------START OPERATION------------------',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)
  
  ### Retreive initial GPS ###
  gpsData = GPScom.getGPS()
  if len(gpsData[1])!=0 and len(gpsData[2])!=0 and len(gpsData[3])!=0:
    Lat_init, Lon_init, Alt_init = float(gpsData[1]), float(gpsData[2]), float(gpsData[3])
  else:
    Lat_init, Lon_init, Alt_init = 0.0, 0.0, 0.0

  messages = ['>>>>>> Getting initial GPS:',
              'Lat(init): ' + str(Lat_init) + ', Lon(init): ' + str(Lon_init) + ', Alt(init): ' + str(Alt_init),
              '',
              '']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)

  ### Search for target way points and start sampling ###
  messages = ['>>>>>> Searching for target way points']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)
  
  for wp in range(len(wayPoints)):
    # Target waypoint
    tg_lat, tg_lon, tg_alt = wayPoints[wp][0], wayPoints[wp][1], wayPoints[wp][2]
    messages = ['-------- WP_' + str(wp+1) + ' --------',
                'TARGET WP: (' + str(tg_lat) + ', ' + str(tg_lon) + ', ' + str(tg_alt) + ')']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)
    
    # Start searching for SEARCH_NO times
    for s in range(PARAMS['SEARCH_NO']):
      messages = ['======== Searching attempt ' + str(s+1) + ' ========']
      print_msg(messages)
      
      if s%10==0:
        RunSignal.blink(wp+1)

      
      # Getting current GPS
      gpsData = GPScom.getGPS()      
      # When recieving valid GPS data 
      if len(gpsData[1])!=0 and len(gpsData[2])!=0 and len(gpsData[3])!=0:
        Lat_curr, Lon_curr, Alt_curr = float(gpsData[1]), float(gpsData[2]), float(gpsData[3])
      else:
        Lat_curr, Lon_curr, Alt_curr = 0.0, 0.0, 0.0 

      ######## For Simulation purpose #########
      # After 20 searches, location will match
      if s == 20 and SIM_FLAG==1:
        Lat_curr = Lat_init + tg_lat
        Lon_curr = Lon_init + tg_lon
        Alt_curr = Alt_init + tg_alt
      ######## For Simulation purpose #########

      # Calculating distance between current and target position
      Dlat = abs(Lat_init + tg_lat - Lat_curr)
      Dlon = abs(Lon_init + tg_lon - Lon_curr)
      Dalt = abs(Alt_init + tg_alt - Alt_curr)

      # Check whether we reach the way point within certain distance
      Match = ((Dlat<PARAMS['LAT_DIFF']) & (Dlon<PARAMS['LON_DIFF'])) & (Dalt<PARAMS['ALT_DIFF'])
      if Match==1:
        break      
      time.sleep(0.5)
     
    messages = ['>>>>>>>> Searching successful at attempt ' + str(s+1) + ' >>>>>>>>']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)

    ### 1. Turn on pump ###
    onOff = 1
    PumpStatus = Pumpcom.pumpOn(onOff)

    messages = ['........ Pump On: Sampling at WP ' + str(wp+1) + ' ........',
              '........ Sampling at (' + str(tg_lat) + ', ' + str(tg_lon) + ', ' + str(tg_alt) + ')']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)

    ### Record sensor data (Start) ###
    gpsData_start = GPScom.getGPS()
    BT_start = ADCcom.readADC_bat_flow(gpsData_start[0])
    TRH_start = ADCcom.readADC_temp_rh_ps_pa(gpsData_start[0])  

    messages = ['GPS_Start (Date, lat, lon, alt): ' + str(gpsData_start[0]) + ', ' + str(gpsData_start[1]) + ', ' + str(gpsData_start[2]) + ', ' + str(gpsData_start[3]),
                'BT_Start (BattVoltage, Flow, 10V): ' + str(BT_start[0]) + ', ' + str(BT_start[1]) + ', ' + str(BT_start[2]),
                'TRH_Start (RH, T, Psys, Pamb): ' + str(TRH_start[0]) + ', ' + str(TRH_start[1]) + ', ' + str(TRH_start[2]) + ', ' + str(TRH_start[3])]
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)

    ###  3. Move Valco valve position (even to odd) & Fill a canister ###
    sendTo = 2 # Valco valve position from even to odd
    Pos1_start = Valcocom.comValco(sendTo)

    messages = ['---->>>> Start filling Canister Pos ' + str(chr(Pos1_start[0])) + str(chr(Pos1_start[1])) + ' >>>>----']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)

    # Flushing for a specified time
    for _ in range(PARAMS['FLUSHING_NO']):
      Winds = Windcom.getWind(gpsData_start[0])
  
    time.sleep(1)

    ### 4. Move Valco valve position (odd to even) ###
    sendTo = 2 # Valco valve position from odd to even
    Pos1_end = Valcocom.comValco(sendTo)

    messages = ['---->>>> End filling Canister >>>>----',
                'End Pos: ' + str(chr(Pos1_end[0])) + str(chr(Pos1_end[1]))]
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)

    ### 5. Record sensor data (End) ###
    gpsData_end = GPScom.getGPS()
    BT_end = ADCcom.readADC_bat_flow(gpsData_end[0])
    TRH_end = ADCcom.readADC_temp_rh_ps_pa(gpsData_end[0])

    messages = ['GPS_End (Date, lat, lon, alt): ' + str(gpsData_end[0]) + ', ' + str(gpsData_end[1]) + ', ' + str(gpsData_end[2]) + ', ' + str(gpsData_end[3]),
                'BT_End (BattVoltage, Flow, 10V): ' + str(BT_end[0]) + ', ' + str(BT_end[1]) + ', ' + str(BT_end[2]),
                'TRH_End (RH, T, Psys, Pamb): ' + str(TRH_end[0]) + ', ' + str(TRH_end[1]) + ', ' + str(TRH_end[2]) + ', ' + str(TRH_end[3])]
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)

    ### 6. Turn off pump ###
    onOff = 0
    PumpStatus = Pumpcom.pumpOn(onOff)

    messages = ['........ Pump Off ........']
    print_msg(messages)
    write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)

    ### 7. Save data for analysis ###
    # Date_start,Date_end,lat_start,lat_end,lon_start,lon_end,alt_start,alt_end,BattVol_start,BattVol_end,Flow_start,Flow_end,10V_start,10V_end,RH_start,RH_end,T_start,T_end,Psys_start,Psys_end,Pamb_start,Pamb_end
    messages = ['>>>>>>>> Recording data for analysis:']
    print_msg(messages)
 
    messages = [str(chr(Pos1_start[0])) + str(chr(Pos1_start[1])) + ',' +
                str(gpsData_start[0]) + ',' + str(gpsData_end[0]) + ',' +
                str(gpsData_start[1]) + ',' + str(gpsData_end[1]) + ',' +
                str(gpsData_start[2]) + ',' + str(gpsData_end[2]) + ',' +
                str(gpsData_start[3]) + ',' + str(gpsData_end[3]) + ',' +
                str(BT_start[0]) + ',' + str(BT_end[0]) + ',' +
                str(BT_start[1]) + ',' + str(BT_end[1]) + ',' +
                str(BT_start[2]) + ',' + str(BT_end[2]) + ',' +
                str(TRH_start[0]) + ',' + str(TRH_end[0]) + ',' +
                str(TRH_start[1]) + ',' + str(TRH_end[1]) + ',' +
                str(TRH_start[2]) + ',' + str(TRH_end[2]) + ',' +
                str(TRH_start[3]) + ',' + str(TRH_end[3]),
                '']    
    print_msg(messages)
    write_files(PARAMS['DATA_FOLDER'], PARAMS['DATA_SAMPLING'], messages)

  messages = ['------------------END OPERATION------------------']
  print_msg(messages)
  write_files(PARAMS['LOG_FOLDER'], PARAMS['LOG_SAMPLING'], messages)
  

def get_waypoints(wayPoints_file):
  '''
  This function gets waypoints to be searched.
  It first tries to get waypoints from wayPoint_file, which is a user-specified csv file that holds a list of waypoints.
  If it fails to retreive waypoints from wayPoint_file, it returns a default value

  Input:
  wayPoints_file>> a location of csv file that has a list of waypoints

  Output:
  waypoints>> a list of waypoints
              format of a waypoint --> (lat, lon, alt)  
  '''
  
  waypoints = []

  try:
    with open(wayPoints_file, mode='r') as file:
      csvFile = csv.reader(file)
      for line in csvFile:
        waypoint = (int(line[0]), int(line[1]), int(line[2]))
        waypoints.append(waypoint)
  except:
    messages = ['Warning>>>>>No such file or wrong value... Returning default values'
               ,''
               ,'']
    print_msg(messages)
    waypoints = DEFAULT_WAYPOINTS

  return waypoints


def main():
  
  # Parsing arguments from command line
  parser = argparse.ArgumentParser(description='Arguments for the main function',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  
  parser.add_argument('-w', '--waypoints', help='waypoints file location (csv)') 
  args = parser.parse_args()
  config = vars(args)

  # Getting waypoints file location
  wayPoints_file = config['waypoints']

  # Getting waypoints from csv file
  wayPoints = get_waypoints(wayPoints_file)

  # Configuring other parameters
  config_params()
  time.sleep(10)
  # Start signal
  RunSignal.blink(10)
  time.sleep(10)
  
  ###########################
  ##### TESTING SENSORS #####
  ###########################
  testing_sensors()
  
  # Test end signal
  RunSignal.blink(3)
  
  ###########################
  #####  CONFIGURATION  #####
  ###########################
  config_system(wayPoints)
  
  # Config end signal
  RunSignal.blink(5)

  ###########################
  #####    OPERATION    #####
  ###########################
  operate_system(wayPoints)

  ###########################
  #####       END       #####
  ###########################
  # cleanup() 
  # softshutdown()
  os.system("sudo poweroff")

if __name__=='__main__':
  main()