import serial
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from drawnow import *

def main():
    def ReadChannel(channel):
        adc = Adafruit_ADS1x15.ADS1115()
        GAIN = 1
        data = adc.read_adc(0, gain=GAIN)
        return data
    
    def ConvertVolts(data,places):
        volts = (data * 3.3) / float(1023)
        volts = round(volts,places)  
        return volts
    min = float(input('Time to record >> ')) 
    amount = min*60*250    

    print('Start')

    plt.ion() # modo interactivo para plotear en tiempo real.

    # Función para plotear en tiempo real.
    def grafRT(): 
        plt.ylim(100,650) #Limites del eje y
        plt.plot(ECG_volts) #graph ecg, array data ECG_volts.
        plt.xlabel('time (miliseconds)')
        plt.ylabel('voltage (mV)')
        plt.title('Electrocardiograma')
        plt.ticklabel_format(useOffset=False) #no autoescalar el eje Y.

    # Arreglo para guardar los datos obtenidos del sensor.
    ECG_volts=[]


    while len(ECG_volts) < amount:
        
        ECG_level = ReadChannel(ECG_channel)
        ECG_volts.append(ConvertVolts(ECG_level,2))
        drawnow(grafRT)                       
        plt.pause(.00000001)
        ecg_data = pd.DataFrame(ECG_volts=ECG_volts) #Guardar datos en un dataframe de pandas.
        name= input("Archive name: ")
        archived = name+ ".csv"
        ecg_data.to_csv(archived) # Generar un archived csv con los datos del ECG.
            
            
    print('Data captured', end='\n')

    # Analyze data acquired with the sensor.
    ecg_data = pd.DataFrame(ECG_volts=ECG_volts)
    name= input("Archive name: ")
    archived = name+ ".csv"
    ecg_data.to_csv(archived)


    ECG_volts = pd.read_csv(archived,delimiter=",")

    ecg_data = data.iloc[:, 1].values #extract samples from dataframe, only column with values.

    # Detection of R peaks in the ECG signal.
    peaks, _ = find_peaks(ecg_data, distance=150)
    distancias = np.diff(peaks)
    media = np.mean(distancias)

    # Calculate and display beats per minute (BPM).

    bpm = (ecg_data.size/media)/(ecg_data.size/15000)
    print('registered {} beats per minute.'.format(round(bpm)))

    # Mostrar la gráfica de los picos R detectados.
    fig1 = plt.figure(1)
    plt.plot(ecg_data, 'b')
    plt.plot(peaks, ecg_data[peaks], 'rx')

# Show the graph of the distribution of the distance between peaks R, equivalent to one heartbeat.
    fig2 = plt.figure(2)
    plt.hist(distancias)
    plt.xlabel('distance (samples)')
    plt.ylabel('frequency')
    plt.title('Distance distribution between local maxima (peaks)')
    plt.show()

    # Save the generated graphs as images.
    
    fig1.savefig(name+ "ecg.png")
    fig2.savefig(name+ "dist.png")
 
#Llamar la función principal main()
if __name__ == '__main__':
  main()