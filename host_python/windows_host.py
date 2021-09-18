# Windows:

# Install the following Python modules:
# pip install pyserial
# pip install psutil
# pip install pythonnet
# 
# Make sure 'OpenHardwareMonitorLib.dll' is in the same folder as this Python script!
#
# Change your COM port to match that of your COM port!

import serial
import os
import time
import clr
import psutil

obj_Disk = psutil.disk_usage('/')
updateTime = 4 #number of seconds between each update

# We are only using a few of these, but I left them here so you can experiment

hardwaretypes = ['Mainboard','SuperIO','CPU','RAM','GpuNvidia','GpuAti','TBalancer','Heatmaster','HDD']
sensortypes = ['Voltage','Clock','Temperature','Load','Fan','Flow','Control','Level','Factor','Power','Data','SmallData']

cpu_temp = ''
rpm = ''
gpu_temp = ''

def sendData(temp, rpm, gpu, free_disk, mem_use, procs):
    try:
        connection = serial.Serial('COM16') # Change this to match your COM port!
        data = temp + ',' + rpm + ',' + str(mem_use) + ',' + str(free_disk) + ',' + gpu + ',' + str(procs)
        connection.write(data.encode())
        print("Data written", temp, rpm, mem_use, free_disk, gpu, procs)
        connection.close  
    except Exception as e:
        print(e)

def initialize_openhardwaremonitor():
    file = 'OpenHardwareMonitorLib'
    clr.AddReference(file)

    from OpenHardwareMonitor import Hardware

    handle = Hardware.Computer()
    handle.MainboardEnabled = True
    handle.CPUEnabled = True
    handle.RAMEnabled = True
    handle.GPUEnabled = True
    handle.Open()
    return handle

def fetch_stats(handle):
    for i in handle.Hardware:
        i.Update()
        for sensor in i.Sensors:
            parse_sensor(sensor)
        for j in i.SubHardware:
            j.Update()
            for subsensor in j.Sensors:
                parse_sensor(subsensor)

def parse_sensor(sensor):
        global cpu_temp
        global rpm
        global gpu_temp
        if sensor.Value is not None:
            if sensor.SensorType == sensortypes.index('Temperature') and sensor.Name == 'CPU Package':
                cpu_temp = str(sensor.Value)

            if sensor.SensorType == sensortypes.index('Fan') and sensor.Name == 'Fan #1':
                rpm = str(sensor.Value)

            if sensor.SensorType == sensortypes.index('Temperature') and sensor.Name == 'GPU Core':
               gpu_temp = str(sensor.Value)

HardwareHandle = initialize_openhardwaremonitor()

while(1):
    fetch_stats(HardwareHandle)
    free_disk = int(obj_Disk.used / (1024.0 ** 3))
    mem_use = int(psutil.virtual_memory().used / (1024 * 1024)) 
    proc_counter = 0
    for proc in psutil.process_iter():
        proc_counter += 1
    sendData(cpu_temp, rpm, gpu_temp, free_disk, mem_use, proc_counter)
    time.sleep(updateTime)
    
