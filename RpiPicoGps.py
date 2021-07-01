from machine import Pin, UART
import time, _thread

class SimGPRS:
    ModuleState = False
    CMDResponse = False
    LockSerial = False
    GpsPower = False
    InfOut = False
    Debug = False
    def __init__(self,enable_pin):
        self.EnablePin = Pin(enable_pin,Pin.OUT)
        self.uart= UART(0,baudrate=9600,stop=1, bits=8,)
        self.Buff = bytearray(255)
        if not self.AT_TEST():
            print("Module is not Enabled -> enabling...")
            self.EnableModule()
    
    def EnableModule(self):
        if not self.ModuleState:
            print("Enabling the module")
            self.EnablePin.high()
            time.sleep(1.5)
            self.EnablePin.low()
            self.ModuleState = True
            time.sleep(1.5)
            self.AT_TEST()
        else:
            print("Module has already started") 
    
    def AT_TEST(self):
        response = self.WriteSerial("AT")
        print("AT TEST:",response)
        if response[-1] == "OK":
            self.CMDResponse = True
            print("At Test OKAY!")
        else:
            self.CMDResponse = False
            print("At Test FAILED!")
        return self.CMDResponse
    
    def ReadSerial(self):
        self.Buff = []
        time.sleep(0.1)
        while(self.uart.any() > 0):
            self.LockSerial = True
            line = self.uart.readline()
            if self.Debug:
                print("Line",line)
            if line.decode().strip() == "":
                continue
            else:
                self.Buff.append(line.decode().strip())
        self.LockSerial = False    
        if self.Buff:
            return self.Buff
        else:
            return False
    
    def WriteSerial(self,CMD):
        CMD += "\r\n"
        CMD = CMD.encode()
        self.uart.write(CMD)
        time.sleep(0.1)
        return self.ReadSerial()
        
        

class GpsTracker(SimGPRS):
    HasFixed = False
    
    def __init__(self,enable_pin = 2, autostart = True):
        super().__init__(enable_pin=enable_pin)
        if autostart:
            self.StartGPS()        
        else:
            pass
    
    def StartGPS(self):
        response = self.WriteSerial("AT + CGPSPWR = 1")
        print(response)
        if response[-1] == "OK":
            self.GpsPower = True
            print("GPS power is on")
        else:
            print("GPS power on error (StartGPS)")
    
    def StopGPS(self):
        response = self.WriteSerial("AT + CGPSPWR = 0")
        if response[-1] == "OK":
            self.GpsPower = False
            print("GPS power is off")
        else:
            print("GPS power off error (StopGPS)")
    def GetGpsStatus(self):
        response = self.WriteSerial("AT + CGPSSTATUS?")
        if response[-1] == "OK":
            print(response[-2])
        else:
            print("GetGpsStatus error")
    def StartNMEA(self):
        response = self.WriteSerial("AT+ CGPSOUT =32")
        ct = 0
        self.InfOut = True
        while(self.InfOut):
            response=self.ReadSerial()
            if response:
                time.sleep(0.5)
                print("".join(response))
            else:
                pass

        
            
   


gpsmodule=GpsTracker(enable_pin=2)

time.sleep(5)
gpsmodule.GetGpsStatus()
gpsmodule.StartNMEA()


        
    
