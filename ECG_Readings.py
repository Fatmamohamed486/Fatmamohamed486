import time
import datetime
import os
import array
import pylab as pl
import Adafruit_ADS1x15
import csv

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
class ECG_Readings(object):

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
