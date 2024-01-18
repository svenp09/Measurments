from matplotlib import pyplot as plt
import os
import datetime
import argparse

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

def main():
    args = get_parser().parse_args()
    #with open("adc.csv") as file:
    #    content_device = file.read().splitlines()
    filepath = args.input
    with open(filepath) as file:
        content_esp = file.read().splitlines()
    

    #points_device = []
    points_deltaVoltage = []
    points_dropVoltage = []

    '''for line in content_device[1:]:
        values = line.split(", ")
        duration = float(values[1])
        if duration > 21:
            continue
        voltage = float(values[2])
        points_device.append(voltage)'''
    
    for line in content_esp:
        values = line.strip().split(": ")
        if values[0].strip() == "Delta Voltage":
            voltage = int(values[1].strip().split()[0])
            points_deltaVoltage.append(voltage)
        if values[0].strip() == "Voltage Drop":
            voltage = int(values[1].strip().split()[0])
            points_dropVoltage.append(voltage)
    
    #print(points_device)
    #print(points_esp)

    #points_esp = points_esp[:len(points_device)]   
            
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


    plot([points_deltaVoltage, points_dropVoltage], ["Delta Voltage", "Drop voltage"], "measurement", "voltage in mV", base_path + "voltageDrop.png")
    txt = open(base_path + "voltageDrop.txt","w")
    txt.write(f"Mean Delta Voltage: {mean_deltaVoltage} mV\n")
    txt.write(f"Mean Drop Voltage: {mean_dropVoltage} mV\n")
    txt.close()

if __name__ == "__main__":
    main()
