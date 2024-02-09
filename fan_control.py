import os
import sys
import time
import signal
from threading import Event

class fan_control:
    def __init__(self, fan_pin=19):
        import RPi.GPIO
        self.fan_pin=fan_pin
        self.GPIO = RPi.GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)

    def module_init(self):    
        self.GPIO.setup(self.fan_pin, self.GPIO.OUT)
        self._pwm_fan = self.GPIO.PWM(self.fan_pin, 1000)
        self._pwm_fan.start(100)

    def module_exit(self):
        self._pwm_fan.stop()

    def check_loop(self, threshold = 70, temp_offset = 3):
        current_temp = int(os.popen("redis-cli get system_temp_celsius").read())

        if current_temp > threshold - temp_offset:
            self._pwm_fan.ChangeDutyCycle(100)
            #print("pwm 100")
        elif current_temp < threshold - temp_offset and current_temp > threshold - 2*temp_offset:
            self._pwm_fan.ChangeDutyCycle(50)
            #print("pwm 50")
        else:
            self._pwm_fan.stop()
            #print("pwm 0")

        #print("Temp: %d " % int(current_temp))

exit_event = Event()

def signal_handler(signal_num, frame):
    exit_event.set()

if __name__ == '__main__':
    for signal_number in ("INT", "TERM", "HUP"):
        signal.signal(getattr(signal, "SIG" + signal_number), signal_handler)

    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 70
    sleep_time = int(sys.argv[2]) if len(sys.argv) > 2 else 5 

    fan_control = fan_control()
    fan_control.module_init()

    while not exit_event.is_set():
        fan_control.check_loop(threshold)
        exit_event.wait(sleep_time)

    fan_control.module_exit()
    print("\nexiting..")
    sys.exit(0)
