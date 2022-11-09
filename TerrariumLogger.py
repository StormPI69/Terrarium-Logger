import blynklib
BLYNK_AUTH='kERy60dic_nYrOXRdbLuGeSO2g9w_1yv'
import threading
import os
import datetime
import time
import busio
import digitalio
import board
import ES2EEPROMUtils
import adafruit_mcp3xxx.mcp3008 as MCP 
from adafruit_mcp3xxx.analog_in import AnalogIn
import RPi.GPIO as GPIO

blynk=blynklib.Blynk(BLYNK_AUTH)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17,GPIO.OUT)
eeprom = ES2EEPROMUtils.ES2EEPROM()
interval=5
state=False
flag=True
Time=0
count=0



@blynk.handle_event("write v1")
def v1_write_handler(pin,value):
    print(value)
    global state
    global flag
    if (state==True):
	    state=False
	    os.system('clear')
	    flag=True
	    print("Logging has been paused , Press button again to resume\n")
			
    else:
	    os.system('clear')
	    state=True
	    print("Time\t\tSystem Timer\t\tTemp")



@blynk.handle_event("write v4")
def v4_write_handler(pin,value):
    global interval
    print(value)
    if value==0:
        if(interval==5):
            interval=10
            blynk.virtual_write(5,interval)
        elif(interval==10):
            interval=2
            blynk.virtual_write(5,interval)
        elif(interval==2):
            interval=5
            blynk.virtual_write(5,interval)
    
    
    


def threadPrinter():
	global interval
	global Time
	global count
	global flag
	global buzzThread
	thread =threading.Timer(interval,threadPrinter)
	thread.daemon=True
	thread.start()
	if(state==True):
		if Time==0:
			Time=time.time()	
		t=datetime.datetime.now()
		print(t.strftime("%H:%M:%S"),' \t',time.strftime("%H:%M:%S",time.gmtime(round(time.time()-Time))),' \t\t',round(((chan.voltage-0.5)/0.01)),'C')
		blynk.virtual_write(0,round(((chan.voltage-0.5)/0.01)))
		blynk.virtual_write(2,t.strftime("%H:%M:%S"))
		if(round(((chan.voltage-0.5)/0.01))>=31):
			flag=False
		eeprom.write_byte(count,t.hour)
		eeprom.write_byte(count+1,t.minute)
		eeprom.write_byte(count+2,t.second)
		eeprom.write_byte(count+3,round(((chan.voltage-0.5)/0.01)))
		count+=4
		#print(list(eeprom.read_block(0,4)))
		if  count>=80:
			count=0


def threadBuzzer():
	global flag
	thread =threading.Timer(1,threadBuzzer)
	thread.daemon=True
	thread.start()
	if flag==False:
		GPIO.output(17,GPIO.HIGH)
		blynk.virtual_write(3,255)
		time.sleep(1)
		GPIO.output(17,GPIO.LOW)
		blynk.virtual_write(3,0)
		


def IntervalButton(self):
    global interval
    if(interval==5):
        interval=10
        blynk.virtual_write(5,interval)
    elif(interval==10):
        interval=2
        blynk.virtual_write(5,interval)
    elif(interval==2):
        interval=5
        blynk.virtual_write(5,interval)
    
		



def buttonPushed(self):
	global state
	global flag
	if (state==True):
		state=False
		os.system('clear')
		flag=True
		print("Logging has been paused , Press button again to resume\n")
			
	else:
		os.system('clear')
		state=True
		print("Time\t\tSystem Timer\t\tTemp")

if __name__=="__main__":
	blynk.run()
	blynk.virtual_write(5,interval)
	counter=0
	GPIO.add_event_detect(4,GPIO.RISING,callback=buttonPushed,bouncetime=300)	
	spi = busio.SPI(clock=board.SCK,MISO=board.MISO,MOSI=board.MOSI)
	cs =digitalio.DigitalInOut(board.D5)
	mcp =MCP.MCP3008(spi,cs)
	chan =AnalogIn(mcp,MCP.P1)
	threadPrinter()
	threadBuzzer()
	
	
	while True:
		blynk.run()
		pass
