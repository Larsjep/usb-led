from arduino.usbdevice import ArduinoUsbDevice
from arduino.usbdevice import USBDeviceNotFound
import time
import usb
import threading


class USBFailed(Exception):
    pass

class USBLedController(object):
    def __init__(self):
        self.blink = False
        self.on_time = 0
        self.off_time = 0
        self.color = (0,0,0)
        self.work_thread = threading.Thread(target=self._main_loop)
        self.work_thread.setDaemon(True)
        self.work_thread.start()

    def set_constant(self, color):
        self.blink = False
        self.color = color

    def set_blink(self, color, on_time, off_time):
        self.on_time = on_time
        self.off_time = off_time
        self.color = color
        self.blink = True

    def _main_loop(self):
        while True:
            try:
                self.led_usb = ArduinoUsbDevice(idVendor=0x16c0, idProduct=0x05df)
                led_usb = self.led_usb

                print("Found: 0x%04x 0x%04x %s %s" % (led_usb.idVendor,
                                                    led_usb.idProduct,
                                                    led_usb.productName,
                                                    led_usb.manufacturer));

                while True:
                    if not self.blink:
                        self._set_color(self.color)
                        time.sleep(1)
                    else:
                        self._set_color(self.color)
                        time.sleep(self.on_time)
                        self._set_color((0,0,0))
                        time.sleep(self.off_time)
            except USBFailed:
                print("USB communication problem, retrying later")
                time.sleep(2)
            except USBDeviceNotFound:
                print("No USB device found, retrying later")
                time.sleep(2)


    def _set_color(self, color):
        r,g,b = color
        for retry in range(5):
            try:
                if retry > 0: # If retrying, flush any previous transfer
                    for _ in range(3):
                        self.led_usb.write(0)
                self.led_usb.write(ord("s"))
                self.led_usb.write(r)
                self.led_usb.write(g)
                self.led_usb.write(b)
                return
            except usb.core.USBError:
                print(f"USB error retrying({retry})...")
        raise USBFailed("USB communication failed")



