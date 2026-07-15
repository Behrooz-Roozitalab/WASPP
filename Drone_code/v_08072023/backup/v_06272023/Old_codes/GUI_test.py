#!/usr/bin/python3
import UWASmod_v2
import datetime
from tkinter import *
import time
import numpy
import os

class Application (Frame):

     def __init__(self, master):
          super(Application, self).__init__(master)
          self.grid()
          self.varRH = IntVar()
          self.varTempC = IntVar()
          self.varPsys = IntVar()
          self.varPamb = IntVar()
          self.create_widgets()

     def create_widgets(self):
          self.button1 = Button(self, text='Record Data to File', command=self.logCalData)
          self.button1.grid(row=4,column=2,sticky=W)
          self.label1 = Label(self, text = 'Date and Time:')
          self.label1.grid(row=2,column=0)
          self.datedispl = Entry(self)
          self.datedispl.grid(row=2,column=1)
          self.label2 = Label(self, text = 'Uncalibrated Data Value:')
          self.label2.grid(row=3,column=0)
          self.datadispl = Entry(self)
          self.datadispl.grid(row=3,column=1)
          self.check1 = Checkbutton(self, text = 'RH', variable = self.varRH)
          self.check2 = Checkbutton(self, text = 'TempC', variable = self.varTempC)
          self.check3 = Checkbutton(self, text = 'Psys', variable = self.varPsys)
          self.check4 = Checkbutton(self, text = 'Pamb', variable = self.varPamb)
          self.check1.grid(row=5)
          self.check2.grid(row=6)
          self.check3.grid(row=7)
          self.check4.grid(row=8)



     def logCalData(self):

         Temp = 0
         RH = 0
         Psys = 0
         Pamb = 0

         if(self.varRH.get()):
               DataUncal = RH
         if(self.varTempC.get()):
               DataUncal = Temp
         if(self.varPsys.get()):
               DataUncal = RH
         if(self.varPamb.get()):
               DataUncal = Temp


         now = datetime.datetime.now()
         strDate = str(now)
         self.datedispl.insert(0,strDate)
         strData = str(DataUncal)
         self.datadispl.insert(0,strData)
         print('Main Program Here')
         


root = Tk()
root.title('This is a test Lab CAL GUI')
root.geometry('600x300')
app = Application(root)
root.mainloop()
