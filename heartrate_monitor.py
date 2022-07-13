
from max30102 import MAX30102
import hrcalc
import threading
import time
import numpy as np
import urllib3
import requests
import sys
import RPi.GPIO as GPIO
from time import sleep         # to control how often the sensor data is collected
from w1thermsensor import W1ThermSensor # to enable our project to talk to the sensor
import Adafruit_ADS1x15
import datetime
import os
import array
import pylab as pl
import csv


baseURL = 'http://api.thingspeak.com/update?api_key=EGGDD5XE4A35W6MB'
ECG_volts=[]

class HeartRateMonitor(object):
    """
    A class that encapsulates the max30102 device into a thread
    """
    
    LOOP_TIME = 0.5
    #ADC read for ECG
    def ReadChannel(channel):
        adc = Adafruit_ADS1x15.ADS1115()
        GAIN = 1
        data = adc.read_adc(0, gain=GAIN)
        return data
    # Function to convert data to voltage level,
    # rounded to specified number of decimal places. 
    def ConvertVolts(data,places):
        volts = (data * 4.096) / float(32768)
        volts = round(volts,places)  
        return volts

    #initializing MAX30102
    def __init__(self, print_raw=False, print_result=False):
        self.bpm = 0
        if print_raw is True:
            print('IR, Red')
        self.print_raw = print_raw
        self.print_result = print_result

    #run all sensors
    def run_sensor(self):
        temp_sensor = W1ThermSensor()                 # create an object to store a connection the sensor. 
        temperature = temp_sensor.get_temperature()   # get the current temperature from the DS18B20 sensor,
        sensor = MAX30102()
        ir_data = []
        red_data = []
        bpms = []

        # run until told to stop
        while not self._thread.stopped:
            
            # check if any data is available
            num_bytes = sensor.get_data_present()
            if num_bytes > 0:
                # grab all the data and stash it into arrays
                while num_bytes > 0:
                    red, ir = sensor.read_fifo()
                    num_bytes -= 1
                    ir_data.append(ir)
                    red_data.append(red)
                    if self.print_raw:
                        print("{0}, {1}".format(ir, red))

                while len(ir_data) > 100:
                    ir_data.pop(0)
                    red_data.pop(0)

                if len(ir_data) == 100:
                    bpm, valid_bpm, spo2, valid_spo2 = hrcalc.calc_hr_and_spo2(ir_data, red_data)
                    if valid_bpm:
                        bpms.append(bpm)
                        while len(bpms) > 4:
                            bpms.pop(0)
                        self.bpm = np.mean(bpms)
                        if (np.mean(ir_data) < 50000 and np.mean(red_data) < 50000):
                            self.bpm = 0
                            if self.print_result:
                                print("Finger not detected")
                                ###################################### ECG #######################################
                        delay = .003
                        i = 0
                        while i<200:
                        # Read the light sensor data
                         ECG_level = ReadChannel(0)
                         ECG_volts.append(ConvertVolts(ECG_level,2))
                         now = datetime.datetime.now()
                         timeString = now.strftime("%Y-%m-%d %H:%M:%S.%f")

                         with open('ECG_Readings.csv', 'a') as log:
                            log.write("{},{},{},{},{}\n".format(timeString,ECG_volts[i],self.bpm,spo2,temperature))
                         print("ECG_volts : {} ({}V)".format(i,ECG_volts[i]))
                         i=i+1
                         # Wait before repeating loop
                         time.sleep(delay)
                        pl.plot(ECG_volts,label="ECG")
                        pl.legend()
                        pl.show()
                            ##############################################################################################
                        if self.print_result:
                            print("BPM: {0}, SpO2: {1}".format(self.bpm, spo2))
                            print("The temperature is %s celsius" % temperature) # print the data in the form of a sentence that will tell the us what the temperature is in celsius.
                            print( "--------------------------------------------" ) 
                            finalurl = baseURL +"&field1=%s&field2=%s&field3=%s&field4=%s" %(ECG_volts[i],self.bpm,spo2,temperature)
                            http = urllib3.PoolManager()
                            f = http.request('GET',finalurl)
                            f.read()
                            f.close()
                            if temperature > 38 or temperature < 35 or spo2 < 92 or self.bpm < 60 or self.bpm > 100:                    # temperature threshold
    # *** take an action regarding the cloud ***
                                report = {}
                                report["value1"] = temperature
                                report["value2"] = self.bpm
                                report["value3"] = spo2
                                requests.post('https://maker.ifttt.com/trigger/123/with/key/nRm3Yf4BU-Irdwh4MnqoXmsH4SoHxY7wf7EpsgvFV26',data=report)

                                    # break out of the loop
                         

            #time.sleep(self.LOOP_TIME)
            #time.sleep(0.06)

        #sensor.shutdown()

    def start_sensor(self):
        self._thread = threading.Thread(target=self.run_sensor)
        self._thread.stopped = False
        self._thread.start()

    def stop_sensor(self, timeout=2.0):
        self._thread.stopped = True
        self.bpm = 0
        self._thread.join(timeout)