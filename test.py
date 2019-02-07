import usb_led
import time



print("Setting color")
delay = 0.5

led_controller = usb_led.USBLedController()
while True:
    led_controller.set_constant((178,60,0))
    time.sleep(5)
    led_controller.set_blink((0,0,255),0.5,2)
    time.sleep(10)
