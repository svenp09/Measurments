from matplotlib import pyplot as plt
import os
import time

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
    with open("adc.csv") as file:
        content_device = file.read().splitlines()
    
    with open("adc.txt") as file:
        content_esp = file.read().splitlines()
    

    points_device = []
    points_esp = []

    for line in content_device[1:]:
        values = line.split(", ")
        duration = float(values[1])
        if duration > 21:
            continue
        voltage = float(values[2])
        points_device.append(voltage)
    
    for line in content_esp:
        values = line.strip().split(": ")
        if not values[0].strip() == "Voltage mV":
            continue
        voltage = int(values[1].strip().split()[0])
        points_esp.append(voltage)
    
    print(points_device)
    print(points_esp)

    points_esp = points_esp[:len(points_device)]   

    base_path = "./results/adc/adc_{}/".format(int(time.time()))
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    with open(base_path + "adc.data", "a") as file:
        file.write("time (in 10s), voltage_device (mV), voltage_esp (mV)\n")
        for i, (p_device, p_esp) in enumerate(zip(points_device, points_esp)):
            file.write("{}, {}, {}\n".format(i, p_device, p_esp))


    plot([points_device, points_esp], ["device", "esp"], "time in 10s", "voltage in mV", base_path + "adc.png")


if __name__ == "__main__":
    main()
