'''
Hardware Wrapper
- Makes old hardware com code easier to use as a single class
- uses legacy hardware interface code
- requires the WASPP Pi Hat PCB
'''

import sys
sys.path.append("/home/ljs/v_08072023/py2prog")

from Hdwcom import(
    GPScom,
    Windcom,
    RunSignal,
    Valcocom,
    ADCcom,
    Pumpcom,
)

class UWASHardware:
    def __init__(self):
        self.pump_on = False
        self.last_valve_position = None
    
    def get_gps(self):
        gpsData = GPScom.getGPS()
        date, Lat, Lon, Alt, Sat = gpsData[0], gpsData[1], gpsData[2], gpsData[3], gpsData[4]
        return {            
            "date": str(date)[:6],
            "lat": Lat[:6],
            "lon": Lon,
            "alt": Alt,
            "sat": int(str(Sat)),
        }

    def get_wind(self):
        ws = Windcom.getWind('') # wind speed
        return {
            "wind": int(ws)
        }
    def get_valve_position(self):
        position = Valcocom.comValco(0)
        return {
            "pos": int(chr(position[0])+chr(position[1]))
        }
    def move_valve_next(self):
        result = Valcocom.comValco(2)
        #verify
        position = self.get_valve_position()

        return {
            "result": int(chr(result[0])+chr(result[1]))
        }

    def get_pressures(self):

    # NOTE: CALIBRATION
    #       pA found to be ~ .2 less than true pressure
    #       pS found to be ~ 1.5 kess than true pressure
        p = ADCcom.readADC_temp_rh_ps_pa('')
        pS, pA = str(p[2]), str(p[3])

        return {
            "pS": round(float(pS),1) + 1.5,
            "pA": round(float(pA),1) + .2,
        }
    
    def get_battery(self):
        BT = ADCcom.readADC_bat_flow('')
        BV, BF, Pwr = str(BT[0]), str(BT[1]), str(BT[2])
        return {
            "BV": round(float(BV),1),
            "flow":  round(float(BF),1),    # THIS MIGHT BE AIR FLOW SNSR
            "pwr":  round(float(Pwr),1),
        }

    def set_pump(self, on):  # 0: off | 1: on
        self.pump_on = on
        PumpStatus = Pumpcom.pumpOn(on)
        
    def get_status(self):
        status = {}

        try:
            status.update(self.get_gps())
        except Exception as exc:
            status["gps_err"] = str(exc)
        try:
            status.update(self.get_wind())
        except Exception as exc:
            status["wind_err"] = str(exc)
        try:
            status.update(self.get_valve_position())
        except Exception as exc:
            status["valve_err"] = str(exc)
        try:
            status.update(self.get_battery())
        except Exception as exc:
            status["batt_err"] = str(exc)
        try:
            status.update(self.get_pressures())
        except Exception as exc:
            status["pressure_err"] = str(exc)
        status["pump"] = int(self.pump_on)
        return status


