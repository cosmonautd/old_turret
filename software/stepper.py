import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

class StepperMotor(object):

    def __init__(self, IN1, IN2, IN3, IN4, delay):
        self.IN1 = IN1
        self.IN2 = IN2
        self.IN3 = IN3
        self.IN4 = IN4
        self.delay = delay
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
    
    def step_clockwise(self, steps=None):
        if not steps: steps = 1
        for i in range(steps):
            GPIO.output(self.IN1,True)
            GPIO.output(self.IN2,True)
            GPIO.output(self.IN3,False)
            GPIO.output(self.IN4,False)
            time.sleep(self.delay)
            GPIO.output(self.IN1,False)
            GPIO.output(self.IN2,True)
            GPIO.output(self.IN3,True)
            GPIO.output(self.IN4,False)
            time.sleep(self.delay)
            GPIO.output(self.IN1,False)
            GPIO.output(self.IN2,False)
            GPIO.output(self.IN3,True)
            GPIO.output(self.IN4,True)
            time.sleep(self.delay)
            GPIO.output(self.IN1,True)
            GPIO.output(self.IN2,False)
            GPIO.output(self.IN3,False)
            GPIO.output(self.IN4,True)
            time.sleep(self.delay)
    
    def step_counterclockwise(self, steps=None):
        if not steps: steps = 1
        for i in range(steps):
            GPIO.output(self.IN1,True)
            GPIO.output(self.IN2,True)
            GPIO.output(self.IN3,False)
            GPIO.output(self.IN4,False)
            time.sleep(self.delay)
            GPIO.output(self.IN1,True)
            GPIO.output(self.IN2,False)
            GPIO.output(self.IN3,False)
            GPIO.output(self.IN4,True)
            time.sleep(self.delay)
            GPIO.output(self.IN1,False)
            GPIO.output(self.IN2,False)
            GPIO.output(self.IN3,True)
            GPIO.output(self.IN4,True)
            time.sleep(self.delay)
            GPIO.output(self.IN1,False)
            GPIO.output(self.IN2,True)
            GPIO.output(self.IN3,True)
            GPIO.output(self.IN4,False)
            time.sleep(self.delay)


#if __name__ == '__main__':

#    phi = StepperMotor(18,22,24,26,0.0025)
#    theta   = StepperMotor(32,36,38,40,0.003)

#    phi.step_clockwise(512/24);
    
#    GPIO.cleanup()
