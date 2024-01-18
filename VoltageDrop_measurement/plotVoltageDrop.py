from matplotlib import pyplot as plt
import os
import datetime
import argparse
import numpy as np

def get_parser():
    p = argparse.ArgumentParser(
        description='Generates imageplot.')
    p.add_argument('input',
                   help='The input filename path.')
    return p

def plot(data, labels, xlabel, ylabel, path):
        fig = plt.figure()
        for data, label in zip(data, labels):
            plt.plot(data, label=label)
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        #plt.ylim(ymin=0)
        fig.legend()
        fig.savefig(path, dpi=fig.dpi)

def initDevice():
    points_device = {}
    points_device["time_us"] =[]
    points_device["current"]= []
    points_device["voltage_mV"]= []
    points_device["trig"]= []
    return points_device

def main():
    args = get_parser().parse_args()

    inputOK = False
    if (args.input):
        filepath = args.input
        with open(filepath) as file:
            content_esp = file.read().splitlines()
        inputOK = True
        

    with open("i40mATask.csv") as file:
        content_device = file.read().splitlines()
       
    

    points_device = initDevice()
    points_deltaVoltage = []
    points_dropVoltage = []

    for line in content_device[1:]:
        values = line.split(",")
        time = float(values[0])   
        current = float(values[1])   
        voltage = float(values[2])
        trig = float(values[4])
        points_device['time_us'].append(time)
        points_device['voltage_mV'].append(voltage)
        points_device["trig"].append(trig)
    
    if inputOK:
        for line in content_esp:
            values = line.strip().split(": ")
            if values[0].strip() == "Delta Voltage":
                voltage = int(values[1].strip().split()[0])
                points_deltaVoltage.append(voltage)
            if values[0].strip() == "Voltage Drop":
                voltage = int(values[1].strip().split()[0])
                points_dropVoltage.append(voltage)
    

    #TODO: Make windowing pretty  
    
    mean_deltaVoltage = sum(points_deltaVoltage)/len(points_deltaVoltage)
    mean_dropVoltage = sum(points_dropVoltage)/len(points_dropVoltage)

    print(f"Mean Delta Voltage: {mean_deltaVoltage}")
    print(f"Mean Drop Voltage: {mean_dropVoltage}")

    # create folder structure
    title = filepath.split(".")
    title = title[0]
    current_time = datetime.datetime.now()
    dt = f"{current_time.year}_{current_time.month}_{current_time.day}-{current_time.hour}_{current_time.minute}_{current_time.second}/"
    base_path = "./results/"+title + dt
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    '''with open(base_path + "adc.data", "a") as file:
        file.write("time (in 10s), voltage_device (mV), voltage_esp (mV)\n")
        for i, (p_device, p_esp) in enumerate(zip(points_device, points_esp)):
            file.write("{}, {}, {}\n".format(i, p_device, p_esp))'''

    regInterest = np.array([508000,511500])
    
    voltage = points_device["voltage_mV"][regInterest[0]:regInterest[1]]
    minVoltage = min(voltage)
    maxVoltage = max(voltage)
    minVoltage = np.ones(regInterest[1]-regInterest[0])*minVoltage
    maxVoltage = np.ones(regInterest[1]-regInterest[0])*maxVoltage
    fig = plt.figure()
    plt.subplot(2,1,1)
    #plt.ylim(2.5,2.8)
    samplingfreq = 100000
    period = 1/samplingfreq
    time = np.array(points_device["time_us"][regInterest[0]:regInterest[1]])
    startTime = time[0]
    time = (time-startTime)*period*1e6
    plt.plot(time,voltage)
    plt.plot(time,minVoltage, label="Min Voltage")
    plt.plot(time,maxVoltage, label="Max Voltage")
    plt.legend(loc="lower left")
    plt.ylabel("Voltage [V]") 
    plt.subplot(2,1,2)
    plt.plot(time,points_device["trig"][regInterest[0]:regInterest[1]], color = "red")
    plt.xlabel("Time [us]")
    plt.ylabel("Trigger")
    #x1 = min(np.nonzero(points_device["trig"])[0])
    #x2 = max(np.nonzero(points_device["trig"])[0])
    #plt.fill_between([x1,x2],[3,3],facecolor="green", alpha =0.3)
    plt.show() 
    plot([points_deltaVoltage, points_dropVoltage], ["Delta Voltage", "Drop voltage"], "measurement", "voltage in mV", base_path + "voltageDrop.png")
    txt = open(base_path + "voltageDrop.txt","w")
    txt.write(f"Mean Delta Voltage: {mean_deltaVoltage} mV\n")
    txt.write(f"Mean Drop Voltage: {mean_dropVoltage} mV\n")
    txt.close()

if __name__ == "__main__":
    main()
