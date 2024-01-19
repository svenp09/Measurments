from matplotlib import pyplot as plt
import os
import datetime
import argparse
import numpy as np

def get_parser():
    p = argparse.ArgumentParser(
        description='Generates imageplot.')
    p.add_argument('--input',
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
    points_device["current_mA"]= []
    points_device["voltage_mV"]= []
    points_device["power_mW"] =[]
    points_device["trig"]= []
    return points_device

def initESP():
    points_ESP = {}
    points_ESP["startVoltage_mV"] =[]
    points_ESP["finalVoltage_mV"] =[]
    points_ESP["dropVoltage_mV"] =[]
    return points_ESP

def main():
    args = get_parser().parse_args()

    inputOK = False
    if (args.input):
        filepath = args.input
        with open(filepath) as file:
            content_esp = file.read().splitlines()
        inputOK = True
        

    with open("i20mATask.csv") as file:
        content_device = file.read().splitlines()
       
    

    points_device = initDevice()
    points_ESP = initESP()

    for line in content_device[1:]:
        values = line.split(",")
        time = float(values[0])   
        current = float(values[1])*1000   
        voltage = float(values[2])
        power = float(values[3])*1000
        trig = float(values[4])
        points_device['time_us'].append(time)
        points_device['voltage_mV'].append(voltage)
        points_device['current_mA'].append(current)
        points_device['power_mW'].append(power)
        points_device["trig"].append(trig)
    
    if inputOK:
        for line in content_esp:
            values = line.strip().split(": ")
            if values[0].strip() == "Start Voltage":
                voltage = int(values[1].strip().split()[0])
                points_ESP["startVoltage_mV"].append(voltage)
            if values[0].strip() == "Final Voltage":
                voltage = int(values[1].strip().split()[0])
                points_ESP["finalVoltage_mV"].append(voltage)
            if values[0].strip() == "Voltage Drop":
                voltage = int(values[1].strip().split()[0])
                points_ESP["dropVoltage_mV"].append(voltage)
    

     
    if inputOK:
        mean_startVoltage = np.mean(points_ESP["startVoltage_mV"])
        mean_finalVoltage = np.mean(points_ESP["finalVoltage_mV"])
        mean_dropVoltage = np.mean(points_ESP["dropVoltage_mV"])

        print(f"Mean Start Voltage: {mean_startVoltage}")
        print(f"Mean Final Voltage: {mean_finalVoltage}")
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
    
    

    trig = points_device["trig"]
    rise = np.where(np.convolve(trig, [1, -1]) == 1)
    rise = rise[0]

    regInterest = np.array([rise[0]-2000,rise[0]+4000])



    samplingfreq = 100000
    period = 1/samplingfreq
    time = np.array(points_device["time_us"][regInterest[0]:regInterest[1]])
    startTime = time[0]
    time = (time-startTime)*period*1e6
    
    voltage = points_device["voltage_mV"][regInterest[0]:regInterest[1]]
    minVoltage = min(voltage)
    
    minVoltage = np.ones(len(time))*minVoltage
    startVoltage = np.ones(len(time))*points_device["voltage_mV"][rise[0]]

    print(f"Joulescope Start voltage {points_device['voltage_mV'][rise[0]]}")
    print(f"Joulescope Final voltage {points_device['voltage_mV'][rise[1]+1000]}")

    plt.figure()
    plt.subplot(2,1,1)
    plt.ylim(2.5,3)
    
    
    plt.plot(time,voltage)
    plt.plot(time,minVoltage, label="Min Voltage")
    plt.plot(time,startVoltage, label="Start Voltage")
    plt.legend(loc="lower left")
    plt.ylabel("Voltage [V]") 
    plt.subplot(2,1,2)
    plt.plot(time,points_device["trig"][regInterest[0]:regInterest[1]], color = "red")
    plt.xlabel("Time [us]")
    plt.ylabel("Trigger")
    if inputOK:
        plt.savefig(base_path + "voltageDropJouleScope.png")
    

    current = points_device["current_mA"][regInterest[0]:regInterest[1]]
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(time,current)
    plt.ylabel("Current [mA]")
    plt.xlabel("Time [us]")
    plt.subplot(2,1,2)
    plt.plot(time,points_device["trig"][regInterest[0]:regInterest[1]], color = "red")
    plt.xlabel("Time [us]")
    plt.ylabel("Trigger")
    if inputOK:
        plt.savefig(base_path + "currentJouleScope.png")

    power = points_device["power_mW"][regInterest[0]:regInterest[1]]

    
    
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(time,power)
    plt.ylabel("Power [mW]")
    plt.xlabel("Time [us]")
    plt.subplot(2,1,2)
    plt.plot(time,points_device["trig"][regInterest[0]:regInterest[1]], color = "red")
    plt.xlabel("Time [us]")
    plt.ylabel("Trigger")
    if inputOK:
        plt.savefig(base_path + "powerJouleScope.png")
    else:
        plt.show()
    
    MeanActivePower = np.mean(points_device["power_mW"][rise[0]:rise[1]])
    MeanActivePowerESP = (1/2*(49.3e-3)*(np.power(mean_startVoltage*1e-3,2) - np.power(mean_finalVoltage*1e-3,2)))/8e-3 * 1000
    
    if inputOK:
        plot([points_ESP["startVoltage_mV"],points_ESP["finalVoltage_mV"], points_ESP["dropVoltage_mV"]], ["Start Voltage", "Final Voltage","Drop voltage"], "measurement", "voltage in mV", base_path + "voltageDropESP.png")
        

        # Save Data   
        csv = open(base_path + "dataJouleScope.csv", 'wt')  
        csv.write(f"Mean power Joulescope: {MeanActivePower} mW")
        csv.write('run, time(ms), current (mA), voltage(mV), trig\n')
        for i in range(0, len(time)):
            csv.write(f'{i}, {time[i]*1000:.6f}, {current[i]:.6f}, {voltage[i]:.6f}, {points_device["trig"][regInterest[0]:regInterest[1]][i]:.0f}\n') 

        csv.close()

        csv = open(base_path + "dataESP.csv", 'wt')
        csv.write(f"Mean Delta Voltage: {mean_startVoltage} mV\n")
        csv.write(f"Mean Delta Voltage: {mean_finalVoltage} mV\n")
        csv.write(f"Mean Drop Voltage: {mean_dropVoltage} mV\n")
        csv.write(f"Mean power ESP: {MeanActivePowerESP} mW")
        csv.write('run, Start Voltage [mV], Final Voltage [mV], Voltage Drop[mV]:\n')
        for i in range(0, len(points_ESP["dropVoltage_mV"])):
            csv.write(f'{i}, {points_ESP["startVoltage_mV"][i]:.6f}, {points_ESP["finalVoltage_mV"][i]:.6f}, {points_ESP["dropVoltage_mV"][i]:.6f}\n')
        csv.close()

if __name__ == "__main__":
    main()
