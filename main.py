# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
from dpeaDPi.DPiComputer import DPiComputer
from dpeaDPi.DPiStepper import *



# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
ON = False
OFF = True
HOME = True
TOP = False
OPEN = False
CLOSE = True
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
DEBOUNCE = 0.1
INIT_RAMP_SPEED = 10
RAMP_LENGTH = 725

dpiStepper = DPiStepper()
dpiStepper.setBoardNumber(0)
dpiComputer = DPiComputer()
dpiComputer.initialize()

microstepping = 8
dpiStepper.setMicrostepping(microstepping)

speed_steps_per_second = 200 * microstepping
accel_steps_per_second_per_second = speed_steps_per_second
dpiStepper.setSpeedInStepsPerSecond(0, speed_steps_per_second)
dpiStepper.setSpeedInStepsPerSecond(1, speed_steps_per_second)
dpiStepper.setAccelerationInStepsPerSecondPerSecond(0, accel_steps_per_second_per_second)
dpiStepper.setAccelerationInStepsPerSecondPerSecond(1, accel_steps_per_second_per_second)


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):
    def build(self):
        self.title = "Perpetual Motion"
        return sm

Builder.load_file('main.kv')
Window.clearcolor = (1,0.4,.5, .8)
update_staircaseSpeed = 1
# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()
#ramp = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
           #  steps_per_unit=200, speed=INIT_RAMP_SPEED)

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////
	
# ////////////////////////////////////////////////////////////////
# //        DEFINE MAINSCREEN CLASS THAT KIVY RECOGNIZES        //
# //                                                            //
# //   KIVY UI CAN INTERACT DIRECTLY W/ THE FUNCTIONS DEFINED   //
# //     CORRESPONDS TO BUTTON/SLIDER/WIDGET "on_release"       //
# //                                                            //
# //   SHOULD REFERENCE MAIN FUNCTIONS WITHIN THESE FUNCTIONS   //
# //      SHOULD NOT INTERACT DIRECTLY WITH THE HARDWARE        //
# ////////////////////////////////////////////////////////////////
class MainScreen(Screen):
    staircaseSpeedText = '0'
    rampSpeed = INIT_RAMP_SPEED
    staircaseSpeed = 1
    gatestate = "Open Gate"
    stairstate = "Staircase On"

    def __init__(self, **kwargs):
        Clock.schedule_interval(self.isBallonRamp, .5)
        print("clock schedule created")
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def toggleGate(self, gatestate):
        servo_number = 0
        if gatestate == "Open Gate":
            gatestate = "Close Gate"
            dpiComputer.writeServo(servo_number, 180)
        else:
            gatestate = "Open Gate"
            dpiComputer.writeServo(servo_number, 30)
        return str(gatestate)


    def reset_ramp(self):
        dpiStepper.moveToAbsolutePositionInSteps(0, 0, True)
        return
        
    def toggleRamp(self):
        dpiStepper.enableMotors(True)
        newspeed_steps_per_second = 200 * microstepping
        dpiStepper.setSpeedInStepsPerSecond(0, newspeed_steps_per_second)
        dpiStepper.moveToRelativePositionInSteps(0, 1600, True)
        dpiStepper.enableMotors(False)
        return
        
    def auto(self):
        dpiComputer.writeServo(0, 180)
        sleep(2)
        dpiComputer.writeServo(0, 30)
        if (dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1)):
            if dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1):
                return
        if dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1) == 0:
            dpiStepper.enableMotors(True)
            newspeed_steps_per_second = 200 * microstepping
            dpiStepper.setSpeedInStepsPerSecond(0, newspeed_steps_per_second)
            dpiStepper.moveToRelativePositionInSteps(0, -50000, False)
            while dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_0) == 1:
                sleep(.01)
        dpiStepper.decelerateToAStop(0)
        sleep(3)
        dpiComputer.writeServo(1, 140)
        sleep(6)
        dpiComputer.writeServo(1, 90)
        return

        
    def setRampSpeed(self, rampSpeed):
        self.rampSpeed = rampSpeed
        speed_int = int(rampSpeed)
        newspeed_steps_per_second = speed_int * microstepping
        dpiStepper.setSpeedInStepsPerSecond(0, newspeed_steps_per_second)
        return

    def isBallonRamp(self, dt=None):
        if (dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1)):
            if dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1):
                return
        if dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_1) == 0:
            dpiStepper.enableMotors(True)
            newspeed_steps_per_second = 200 * microstepping
            dpiStepper.setSpeedInStepsPerSecond(0, newspeed_steps_per_second)
            dpiStepper.moveToRelativePositionInSteps(0, -50000, False)
            while dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_0) == 1:
                sleep(.01)
            dpiStepper.decelerateToAStop(0)
        return

    def setStaircaseSpeed(self, staircaseSpeed):
        self.staircaseSpeed = staircaseSpeed
        update_staircaseSpeed = int(staircaseSpeed * 90)
        print(update_staircaseSpeed)
        return str(staircaseSpeed)

    def toggleStaircase(self, stairstate):
        if stairstate == "Staircase On":
            stairstate = "Staircase Off"
            dpiComputer.writeServo(1, update_staircaseSpeed)
        else:
            stairstate = "Staircase On"
            dpiComputer.writeServo(1, 90)
        return(stairstate)

    def initialize(self):
        dpiStepper.enableMotors(True)
        dpiComputer.writeServo(0, 30)
        dpiStepper.moveToAbsolutePositionInSteps(0, 0, True)
        dpiStepper.enableMotors(False)
        return

    def resetColors(self):
        self.ids.gate.color = YELLOW
        self.ids.staircase.color = YELLOW
        self.ids.ramp.color = YELLOW

    
    def quit(self):
        print("Exit")
        MyApp().stop()

sm.add_widget(MainScreen(name = 'main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
