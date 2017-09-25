#!/usr/bin/python import os

# sleep(15)

# how to set to autostart:
# sudo nano etc/profile
# comment or uncomment python line
# solo un comentario para agregar un cambio a git

#importando modulos genericos
from time import sleep
from time import strftime 
import time
import serial
import re

# configuaracion de entradas/saldas del RPI
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

button = 4				# GPIO04, pin nro 07 
valve_relay = 17		# GPIO17, pin nro 11   
button2 = 27			# GPIO27, pin nro 13
spritz_relay = 22		# GPIO22, pin nro 15
coinhibitor_relay = 23	# GPIO23, pin nro 16
UV_relay = 18			# GPIO18, pin nro 12

GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(button2, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(valve_relay, GPIO.OUT)
GPIO.setup(spritz_relay, GPIO.OUT)
GPIO.setup(coinhibitor_relay, GPIO.OUT)
GPIO.setup(UV_relay, GPIO.OUT)

#para carriots
from urllib.request import urlopen, Request
from time import mktime, sleep
from datetime import datetime
from json import dumps

class Client (object):
    api_url = "http://api.carriots.com/streams"

    def __init__(self, api_key=None, client_type='json'):
        self.client_type = client_type
        self.api_key = api_key
        self.content_type = "application/vnd.carriots.api.v2+%s" % self.client_type
        self.headers = {'User-Agent': 'Raspberry-Carriots',
                        'Content-Type': self.content_type,
                        'Accept': self.content_type,
                        'Carriots.apikey': self.api_key}
        self.data = None
        self.response = None

    def send(self, data):
        self.data = dumps(data).encode('utf8')
        request = Request(Client.api_url, self.data, self.headers)     
        self.response = urlopen(request)
        return self.response
        
def rc_time(pipin):
    measurement = 0
    GPIO.setup(pipin, GPIO.OUT)
    GPIO.output(pipin, GPIO.LOW)
    sleep(0.1)

    GPIO.setup(pipin, GPIO.IN)

    while GPIO.input(pipin) == GPIO.LOW:
        measurement += 1

    return measurement
    
    
#fin para carriots 

ser = serial.Serial('/dev/ttyACM0',9600,timeout = 0)
ser2 =  serial.Serial('/dev/ttyACM2',9600,timeout = None)
ser3 =  serial.Serial('/dev/ttyACM1',9600,timeout = None, parity = serial.PARITY_NONE, xonxoff = False, rtscts = False, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS)

#modulos custom
from igua_display import startdisplay, refreshdisplay 
from igua_display import display_bienvenida_linear, display_bienvenida_pwyw
from igua_display import display_acumula_pwyw, display_acumula_linear
from igua_display import display_servidos_lt, display_agradece 

# import flowmeter
# import valve

#from display + coinacceptor

last = 0.0
running = 1


solesacumulados = 0   			#transaction-wise accumulator
ferrosacumulados = 0  			#transaction-wise accumulator
cuenta_de_ciclos = 0				#transactions counter on eeprom	

process_id = 0                  #
modo_maquina = 0  # 1: pay what you want , 0: linear mode
button_state = 0
now = 0
now_1 = 0

#setup
startdisplay()
		
#main loop

#para carriots
device = "IGUA01@kikomayorga.kikomayorga"  # Replace with the id_developer of your device
apikey = "13f622d642b12cc336fa6bfde36e1561c6ac7eea19bd88d7c32246d0fca45691"  # Replace with your Carriots apikey
client_carriots = Client(apikey)
#para carriots


#para lcd
def lcd_bienvenida_linear(now):
	if  now == 0:
		ser3.write('agua pura!         toma igua!!! '.encode())
	elif now == 1:
		ser3.write('hola mundo!!!      hola igua!!! '.encode())
	elif now == 2:
		ser3.write('chauuuuuuu!!!      hola igua!!! '.encode())
	elif now == 3:
		ser3.write('hola mundo!!!      hola igua!!! '.encode())
	elif now == 4:
		ser3.write('chauuuuuuu!!!      hola igua!!! '.encode())
	elif now == 5:
		ser3.write('hola mundo!!!      hola igua!!! '.encode())
	
	return 1

def lcd_bienvenida_pwyw(now):
	if  now == 0:
		ser3.write('agua pura!         toma igua!!! '.encode())
	elif now == 1:
		ser3.write('hola mundo!!!      hola igua!!! '.encode())
	elif now == 2:
		ser3.write('chauuuuuuu!!!      hola igua!!! '.encode())
	elif now == 3:
		ser3.write('hola mundo!!!      hola igua!!! '.encode())
	elif now == 4:
		ser3.write('chauuuuuuu!!!      hola igua!!! '.encode())
	elif now == 5:
		ser3.write('hola mundo!!!      hola igua!!! '.encode())
	
	return 1

def lcd_acumula_linear(solesacumulados):
	# ser3.write('hola mundo!!!      hola igua!!! '.encode())	
	ser3.write(('tu saldo: S/. ' + str(format(solesacumulados, '.2f'))).encode())
	# msgSurfaceObj = fontObj.render('tu saldo: S/. ' + format(solesacumulados, '.2f'), False,whiteColor)
	# msgSurfaceObj2 = fontObj2.render('deposita o sirvete ' + format(solesacumulados / 0.5, '.2f') + ' litros.', False,whiteColor)
	return 1
	
def lcd_acumula_pwyw(solesacumulados):
	# ser3.write('hola mundo!!!      hola igua!!! '.encode())	
	# msgSurfaceObj = fontObj.render('tu aporte: S/. ' + format(solesacumulados, '.2f'), False,whiteColor)
	ser3.write(('tu aporte: S/. ' + str(format(solesacumulados, '.2f'))).encode())	
	# msgSurfaceObj2 = fontObj2.render('deposita mas o sirvete! ', False,whiteColor)	

	
def lcd_servidos_lt(servidos_lt,diff):
	ser3.write(('te quedan: ' + str(format(servidos_lt/1000, '.3f')) + ' litros!').encode())	
	# msgSurfaceObj = fontObj.render('te quedan: ' + format(servidos_lt/1000, '.3f') + ' litros!', False,whiteColor)
	# msgSurfaceObj = fontObj.render('te quedan: ' + format(servidos_lt/1000, '.3f') + ' litros!', False,whiteColor)
	# msgSurfaceObj2 = fontObj2.render('aun tienes: ' + format(diff) + ' segs. ', False,whiteColor)

	
def lcd_agradece():
	ser3.write('gracias!!!! igua ague pe ! '.encode())	

	
		
#para lcd
	
while 1 == 1:
	#pantalla de bienvenida
	GPIO.output(valve_relay, 1)
	GPIO.output(spritz_relay, 0)
	if process_id == 0:  #espera monedas
		ferrosacumulados = 0
		now_1 = now
		now = time.time()
		now = int((now/2)%6)
		if now != now_1:
			if modo_maquina == 0:
				display_bienvenida_linear(now)
				lcd_bienvenida_linear(now)
			if modo_maquina == 1:
				display_bienvenida_pwyw(now)
				lcd_bienvenida_pwyw(now)  # cuidado CUIDADO!!!!
	
    #leer aceptador de monedas
		before = int(time.time())
		
		bytesToRead = ser.inWaiting()
		if bytesToRead > 0:
			now = int(time.time())
			process_id = 1
			
			
	#acepta monedas
	elif process_id == 1:
		secondcycle = 0   #variable que inicializa el p_id #2
		bytesToRead = ser.inWaiting()
		if bytesToRead > 0:
			sleep(0.5)
			bytesToRead = ser.inWaiting()
			# print("bytes to read: ", bytesToRead)
			# string_igua = str(ser.readline(),'utf-8')
			string_igua = ser.read(2)		
			# print("bytes read: ", string_igua)
			# string_igua = string_igua.replace('\n','')
			# string_igua = string_igua.replace('b\'\\x','')
			# string_igua = string_igua.replace('\'','')
			# string_igua = string_igua.replace('b\\n','')
			# string_igua_2 = int(re.search(r'\d+', string_igua).group())
			# string_igua = string_igua_2
			ferros = int(string_igua)
			ferrosacumulados = ferrosacumulados + ferros
			solesacumulados = ferrosacumulados / 10.0
			if modo_maquina == 0:
				display_acumula_linear(solesacumulados)
				lcd_acumula_linear(solesacumulados)
			if modo_maquina == 1:
				display_acumula_pwyw(solesacumulados)
				lcd_acumula_pwyw(solesacumulados)
			before = int(time.time()) 
			# print("before: ", before)
		
		#TIMEOUT 
		now = int(time.time())
		# print("now: ", now)	
		diff = now - before
		# print("diff: ", diff)
		if diff > 10:
			process_id = 2
			cuenta_de_ciclos = cuenta_de_ciclos + 1
			# print("van n monedas:", cuenta_de_ciclos)
			# print("pasaremos al prcid 2")
			diff = 0
			before = int(time.time()) 
				
		
		#tap_button pressed
		button_state = GPIO.input(button)
		if button_state == GPIO.LOW:
			diff = 0
			# print ("button is LOW - OR PRESSED")
			time.sleep(0.5)	
			latch = 1
			process_id = 2
		else:
			process_id = 1
			# print ("button is NOT PRESSED")	
		
	
	# habilita vavula y muestra litros
	elif process_id == 2:
				           
		# ser2.write(1)  habilitar valvula
		GPIO.output(valve_relay, 0)
		GPIO.output(spritz_relay, 1)
		
		ser2.flushInput()
		sleep(.1)
		servidos_lt = 0
		precio = 0.5
		if modo_maquina == 0:
			litros_servir = 1000 * (solesacumulados / precio) 
		if modo_maquina == 1:
			litros_servir = 1000
		
	
		while process_id == 2:
			
						
			bytesToRead = ser2.inWaiting()
			if bytesToRead > 0:
				
				sleep(0.2)
				bytesToRead = ser2.inWaiting()
				# print("bytes to read on ser2: ", bytesToRead)
				string_igua = str(ser2.readline(),'utf-8')
				# print("received on ser2: ", string_igua)
				string_igua = string_igua.lstrip('r')		
				if secondcycle == 0:
					countstart = int(string_igua)
					
				secondcycle = 1  #flag que indica que ya se corrio una vuelta de inicializon
				
				# print("bytes striped from ser2: ", string_igua)
				servidos_total = int(string_igua)
				servidos_lt = 0.9 * ((servidos_total - countstart) * 2640)/2000
				diff = 10 - diff
				display_servidos_lt((litros_servir - servidos_lt),diff)
				lcd_servidos_lt((litros_servir - servidos_lt),diff)
				
			if (servidos_lt - litros_servir) > 0:
				GPIO.output(valve_relay, 1)
				GPIO.output(spritz_relay, 0)
				#send collected data to carriots
				timestamp = int(mktime(datetime.utcnow().timetuple()))
				timestamp = int(mktime(datetime.utcnow().timetuple()))
				solesstring = str(solesacumulados)
				data = {"protocol": "v2", "device": device, "at": timestamp, "data": {"colectado soles": solesacumulados, "servido litros": format(servidos_lt/1000, '.3f')}}
				carriots_response = client_carriots.send(data)
				print(carriots_response.read())
				#fin bloque carriots 
				process_id = 3
					
			now = int(time.time())
			# print("before: ", before)
			# print("now: ", now)	
			diff = now - before
			# print("diff: ", diff)
			if diff > 10:
				GPIO.output(valve_relay, 1)
				GPIO.output(spritz_relay, 0)
				#send collected data to carriots
				timestamp = int(mktime(datetime.utcnow().timetuple()))
				solesstring = str(solesacumulados)
				data = {"protocol": "v2", "device": device, "at": timestamp, "data": {"colectado soles": solesacumulados, "servido litros": format(servidos_lt/1000, '.3f')}} 
				carriots_response = client_carriots.send(data)
				print(carriots_response.read())
				#fin bloque carriots 
				process_id = 3
				
			
			# codigo para direct button:
			button_state = GPIO.input(button)
			if button_state == GPIO.LOW: 
				before = int(time.time())
				now = before
				diff = 0
				# print ("button is LOW - OR PRESSED")
				time.sleep(0.05)
				GPIO.output(valve_relay, 0)
				GPIO.output(spritz_relay, 1)
								
			else:
				time.sleep(0.05)
				GPIO.output(valve_relay, 1)
				GPIO.output(spritz_relay, 0)
			# print ("button is NOT PRESSED")	
			'''
			#aca el boton resetea el tiempo
			if latch == 1:
				before = int(time.time())
				now = before
				diff = 0

			# para detectar flancos se almacena estado previo y se lee 
			# de nuevo el boton
			last_buttonstate = button_state
			button_state = GPIO.input(button)
			sleep(0.1)
							
			#aca se detecta el flanco y se togglea el latch			
			if ((button_state == GPIO.LOW)&(last_buttonstate == GPIO.HIGH)):
				sleep(0.5)
				# print ("button is LOW - OR PRESSED")
				latch = 1 - latch
				GPIO.output(relay, (1 - latch))   #imprime el valor de valvula
				
			else:
				# print ("no se ha detectado flanco")	
				GPIO.output(relay, (1 - latch))   #imprime el valor de valvula
			'''	
					

	# deshabilita vavula y agradece
	elif process_id == 3:
		#ser2.write(0)  # deshabilitar valvula
		sleep(0.5)
		display_agradece()
		lcd_agradece()
		before = int(time.time()) 
		# print("before: ", before)
		while process_id==3:
			now = int(time.time())
			# print("now: ", now)	
			diff = now - before
			# print("diff: ", diff)
			if diff > 3:
				process_id = 0
	
	


# todo: rfid
	
