"""
Date of Creation: 2024-06-21
Version of Python used for Testing: 3.8.17
Written and edited by: G. R. Pennisi, Nora Charles, and Thorlabs
==================
Description: This example controls the BSC203 series (Using the MAX683/M stage)
"""

import time
import clr
import pygame # module necessary for xbox controller
from System import Decimal  # necessary for real world units

# initialize pygame for joystick control
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# load kinesis libraries so that they can be reference in the code
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.Benchtop.StepperMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.Joystick.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorUI.dll")

#import those specific libraries 
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.GenericMotorUI import *
from Thorlabs.MotionControl.Benchtop.StepperMotorCLI import *
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.Joystick import *

def main():
    try:
        #gives you ability to create devices so that you can access the bsc203 controller
        DeviceManagerCLI.BuildDeviceList()

        # create new devices for both controllers
        serial_no1 = "70214254"  # xyz axis
        serial_no2 = "70205184" # roll (hens) pitch yaw axis

        # connect, begin polling, and enable for device 1 and 2
        device1 = BenchtopStepperMotor.CreateBenchtopStepperMotor(serial_no1)
        device1.Connect(serial_no1)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

        device2 = BenchtopStepperMotor.CreateBenchtopStepperMotor(serial_no2)
        device2.Connect(serial_no2)
        time.sleep(0.25)

        # initialize the channels of each controller for each axis being used
        channel1 = device1.GetChannel(1) # x axis
        channel2 = device1.GetChannel(2) # y axis
        channel3 = device1.GetChannel(3) # z axis

        channel4 = device2.GetChannel(1) # roll (hens) axis
        channel5 = device2.GetChannel(2) # pitch axis
        channel6 = device2.GetChannel(3) # yaw axis

        # ensure that the device settings of each device and its respective channels have been initialized
        channels = [channel1, channel2, channel3, channel4, channel5, channel6]
        for channel in channels:
            if not channel.IsSettingsInitialized():
                channel.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert channel.IsSettingsInitialized() is True
        
        # start polling and enable for each channel
        for channel in channels:
            channel.StartPolling(250)  # 250ms polling rate
            time.sleep(0.5)
            channel.EnableDevice() # EnableDevice() properly intiailizes the device so that it can now be referenced and used later
            time.sleep(0.25)

        #get device info and display description
        ''' --> this is helpful to keep because
        upon start up, this will print for each axis being used.
        therefore, you know if every channel is actually properly connected. ''' 
        for channel in channels:
            device_info = channel.GetDeviceInfo()
            print(device_info.Description)

        # load any configuration settings needed by the controller/stage
        for channel in channels:
            channel_config = channel.LoadMotorConfiguration(channel.DeviceID)
            chan_settings = channel.MotorDeviceSettings
            channel.GetSettings(chan_settings)
            channel_config.DeviceSettingsName = f'MAX683/M/{channel.DeviceID}'  # update the string as per your device naming convention
            channel_config.UpdateCurrentConfiguration()
            channel.SetSettings(chan_settings, True, False)

        # home or zero the motors of the deivce 
        print("Homing Motor")
        for channel in channels:
            channel.Home(60000) # do NOT change the timeout. leave it at 60s
        print("Homing Complete")

        # main control loop setup
        running = True
        step_size = Decimal(0.01)
        timeout = 60000

        while running:
            pygame.event.pump() # necessary to process internal events (such as button pressing and joystick moving)
            # apply movement based on joystick input
            #x axis
            if joystick.get_button(2): # MoveRelative is necessary as opposed to MoveTo for continuous movement
                channel1.MoveRelative(MotorDirection.Forward, step_size, timeout)
            if joystick.get_button(3):
                channel1.MoveRelative(MotorDirection.Backward, step_size, timeout)

            # y axis
            if joystick.get_button(0):
                channel2.MoveRelative(MotorDirection.Forward, step_size, timeout)
            if joystick.get_button(1):
                channel2.MoveRelative(MotorDirection.Backward, step_size, timeout)

            # for analog stick movement, must get the state of the axis and which way it is moving first before you reference it
            z_axis = joystick.get_axis(0)  # left stick horizontal
            roll_axis= joystick.get_axis(1)  # left stick vertical
            pitch_axis = joystick.get_axis(2)  # right stick horizontal
            yaw_axis = joystick.get_axis(3)  # right stick vertical

            #z axis
            if z_axis > 0.1:  # threshold to avoid small, unintentional movements
                channel3.MoveRelative(MotorDirection.Forward, step_size * Decimal(abs(z_axis)), timeout)
            elif z_axis < -0.1:  # threshold to avoid small, unintentional movements but in the backwards direction
                channel3.MoveRelative(MotorDirection.Backward, step_size * Decimal(abs(z_axis)), timeout)

            #roll (hens) axis
            if roll_axis > 0.1: 
                channel4.MoveRelative(MotorDirection.Forward, step_size * Decimal(abs(roll_axis)), timeout)
            elif roll_axis < -0.1:  
                channel4.MoveRelative(MotorDirection.Backward, step_size * Decimal(abs(roll_axis)), timeout)

            #pitch axis
            if pitch_axis > 0.1:  
                channel5.MoveRelative(MotorDirection.Forward, step_size * Decimal(abs(pitch_axis)), timeout)
            elif pitch_axis < -0.1: 
                channel5.MoveRelative(MotorDirection.Backward, step_size * Decimal(abs(pitch_axis)), timeout)

            #yaw axis
            if yaw_axis > 0.1:
                channel6.MoveRelative(MotorDirection.Forward, step_size * Decimal(abs(yaw_axis)), timeout)
            elif yaw_axis < -0.1: 
                channel6.MoveRelative(MotorDirection.Backward, step_size * Decimal(abs(yaw_axis)), timeout)
                
            # stop the loop when the 'Start' button is pressed (button 7 on Xbox controllers)
            if joystick.get_button(7):
                running = False

            time.sleep(0.1)
        
        # stop polling and disconnect all devices
        for channel in channels:
            channel.StopPolling()

        device1.Disconnect()
        device2.Disconnect()

    except Exception as e:
        # if any sort of error occurs, that exception will print
        print(e)

if __name__ == "__main__": # run the code
    main()
