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
        self.uart= UART(0,baudrate=9600,stop=1,parity=None, rxbuf=100)
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
        time.sleep(0.1)
        self.Buff = []
        line = bytes()
        while(self.uart.any() > 1):
            self.LockSerial = True
            line = self.uart.readline()
            print(line)
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
    GpsPower = 0
    
    def __init__(self,enable_pin = 2, autostart = True):
        super().__init__(enable_pin=enable_pin)
        if autostart:
            self.StartGPS()        
        else:
            pass
    
    def StartGPS(self):
        if self.GetGPSPower() != 1:
            print("GPS power is off -> opening...")
            response = self.WriteSerial("AT + CGPSPWR = 1")
            print(response)
        elif self.GetGPSPower() == 1:
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
            
    def GetGPSPower(self):
        response = self.WriteSerial("AT+CGPSPWR?")
        print("GPS Power:", response)
        if response[-1]=="OK":
            for res in response:
                if res.startswith("+CGPSPWR:"):
                    self.GpsPower = int(res[10::])
                    print("GpsPower:",self.GpsPower)
                    return self.GpsPower
                else:
                    pass
        else:
            print("GetGPSpower Error")
            return -1
        
    def GetGpsStatus(self):
        response = self.WriteSerial("AT + CGPSSTATUS?")
        if response[-1] == "OK":
            for res in response:
                if res.startswith("+CGPSSTATUS:"):
                    print(res[13::])
                    break
                else:
                    pass             
        else:
            print("GetGpsStatus error")
            
    def StartNMEA(self):
        response = self.WriteSerial("AT+ CGPSOUT =32")
        ct = 0
        self.InfOut = True
        while(self.InfOut):
            response=self.ReadSerial()
            if response:
                time.sleep(0.1)
                print("".join(response))
                nmea = response[0].split(",")
                print(nmea)
            else:
                pass
    
    def GetNMEALine(self):
        response = self.WriteSerial("AT+CGPSINF=0")
        print(response)


gpsmodule=GpsTracker(enable_pin=2)
time.sleep(1)
gpsmodule.GetGPSPower()
gpsmodule.GetGpsStatus()
gpsmodule.GetNMEALine()
#gpsmodule.StartNMEA()


        
    
