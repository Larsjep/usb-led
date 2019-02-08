from datetime import datetime
from datetime import timedelta
from datetime import timezone
import win32com.client
from time import sleep
from time import time
import calendar
from tzlocal import get_localzone
import usb_led
import threading
from systrayicon import SysTrayIcon
import pythoncom


LOCAL_TIMEZONE = get_localzone()

DIM_FACTOR = 0.1
WARNING_COLOR = (int(178*DIM_FACTOR),int(60*DIM_FACTOR),0)
ALARM_COLOR = (128,0,0)

TEMPORARY_OFF_TIME = 10*60

class CalenderChecker(object):
    def __init__(self, led_controller):
        self.led_controller = led_controller
        self.work_thread = threading.Thread(target=self._main_loop)
        self.work_thread.setDaemon(True)
        self.work_thread.start()
        self.turn_off_time = 0

    def temporary_turn_off(self, sysTrayIcon):
        self.turn_off_time = time()

    def _getCalendarEntries(self, days=1):
        """
        Returns calender entries for days default is 1
        """
        Outlook = win32com.client.Dispatch("Outlook.Application")
        ns = Outlook.GetNamespace("MAPI")
        appointments = ns.GetDefaultFolder(9).Items
        #print("{appointments} : {ns} : {ns.GetDefaultFolder(9)}")
        appointments.Sort("[Start]")
        appointments.IncludeRecurrences = "True"
        today = datetime.today()
        begin = today.date().strftime("%d/%m/%Y")
        tomorrow= timedelta(days=days)+today
        end = tomorrow.date().strftime("%d/%m/%Y")
        appointments = appointments.Restrict("[Start] >= '" +begin+ "' AND [END] <= '" +end+ "'")
        def convert_time(wintime):
            # Apparently the timezone information is incorrect. It is always +00:00 even thou the time
            # is in local time
            return LOCAL_TIMEZONE.localize(datetime.fromisoformat(str(wintime)[:-6])).timestamp()
        return [(convert_time(a.Start), a.Subject, a.Sensitivity) for a in appointments]

    def _main_loop(self):
        pythoncom.CoInitialize()
        while True:
            entries = self._getCalendarEntries()
            now = time()
            active = False
            print(f"Time is now: {datetime.fromtimestamp(now)}")
            if now - self.turn_off_time > TEMPORARY_OFF_TIME:
                for start, subject, sensitivity in entries:
                    if sensitivity >= 2: continue
                    until = start - now
                    print(f"Time until {subject} = {until}")
                    if until > 0:
                        if until <= 60:
                            print(f"Alarm less than 60 seconds to {subject}")
                            self.led_controller.set_blink(ALARM_COLOR,0.5,1)
                            active = True
                        elif until <= 5*60:
                            print(f"Under 5 minutes {subject}")
                            self.led_controller.set_constant(WARNING_COLOR)
                            active = True
                    # Keep state for 5 min
                    print(f"Until = {until}")
                    if until > -5*60 and until < 0:
                        active = True
            if not active:
                print("LED off")
                self.led_controller.set_constant((0,0,0))
            sleep(10)

led_controller = usb_led.USBLedController()
calendar_checker = CalenderChecker(led_controller)

SysTrayIcon('lamp.ico', "USB Led Notifier", (
    ("Temporary off", 'lamp.ico', calendar_checker.temporary_turn_off),
    ))