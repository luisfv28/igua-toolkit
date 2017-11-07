from time import sleep
from time import strftime 
import time
import serial
import re
import socket
REMOTE_SERVER = "www.google.com"

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

button = 4			# GPIO04, pin nro 07 
valve_relay = 17		# GPIO17, pin nro 11   
button2 = 27			# GPIO27, pin nro 13
spritz_relay = 22		# GPIO22, pin nro 15
coinhibitor_relay = 23		# GPIO23, pin nro 16
UV_relay = 18			# GPIO18, pin nro 12

#Inicio Conexion con Carriots

GPIO.setup(button, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(button2, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(valve_relay, GPIO.OUT)
GPIO.setup(spritz_relay, GPIO.OUT)
GPIO.setup(coinhibitor_relay, GPIO.OUT)
GPIO.setup(UV_relay, GPIO.OUT)

from urllib.request import urlopen, Request
from time import mktime, sleep
from datetime import datetime
from json import dumps

class Client (object):
    api_url = "http://api.carriots.com/streams"
    api_read_url = "http://api.carriots.com/streams/IGUA01@kikomayorga.kikomayorga/"

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
       

def is_connected():
    try:
        host = socket.gethostbyname(REMOTE_SERVER)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

#Final Conexion con Carriots

ser2 =  serial.Serial('/dev/ttyACM1',9600,timeout = None)  
ser3 =  serial.Serial('/dev/ttyACM0',9600,timeout = None, parity = serial.PARITY_NONE, xonxoff = False, rtscts = False, stopbits = serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS)

from igua_display import startdisplay, refreshdisplay 
from igua_display import display_bienvenida_linear, display_bienvenida_pwyw
from igua_display import display_acumula_pwyw, display_acumula_linear
from igua_display import display_servidos_lt, display_agradece 

last = 0.0
running = 1


solesacumulados = 0   		#transaction-wise accumulator
ferrosacumulados = 0  		#transaction-wise accumulator
cuenta_de_ciclos = 0		#transactions counter on eeprom	

process_id = 0                  #
modo_maquina = 0  		# 1: pay what you want , 0: linear mode
button_state = 0
now = 0
now_1 = 0

startdisplay()

device = "IGUA01@kikomayorga.kikomayorga"  
apikey = "13f622d642b12cc336fa6bfde36e1561c6ac7eea19bd88d7c32246d0fca45691"  
client_carriots = Client(apikey)

# ejemplo de curl "para traer todos los ulktimos streams"
# curl --header carriots.apikey:13f622d642b12cc336fa6bfde36e1561c6ac7eea19bd88d7c32246d0fca45691 
#               http://api.carriots.com/streams/?device=IGUA01@kikomayorga.kikomayorga

#Inicio Definiciones de Pantalla

def lcd_bienvenida_linear(now):
	if  now == 0:
		ser3.write('agua pura!      toma igua!!!    '.encode())
	elif now == 1:
		ser3.write('hola mundo!!!   hola igua!!!    '.encode())
	elif now == 2:
		ser3.write('chauuuuuuu!!!   hola igua!!!    '.encode())
	elif now == 3:
		ser3.write('hola mundo!!!   hola igua!!!    '.encode())
	elif now == 4:
		ser3.write('chauuuuuuu!!!   hola igua!!!    '.encode())
	elif now == 5:
		ser3.write('hola mundo!!!   hola igua!!!    '.encode())
	
	return 1

def lcd_bienvenida_pwyw(now):
	if  now == 0:
		ser3.write('agua pura!      toma igua!!!    '.encode())
	elif now == 1:
		ser3.write('hola mundo!!!   hola igua!!!    '.encode())
	elif now == 2:
		ser3.write('chauuuuuuu!!!   hola igua!!!    '.encode())
	elif now == 3:
		ser3.write('hola mundo!!!   hola igua!!!    '.encode())
	elif now == 4:
		ser3.write('chauuuuuuu!!!   hola igua!!!    '.encode())
	elif now == 5:
		ser3.write('hola mundo!!!   hola igua!!!    '.encode())
	
	return 1

def lcd_acumula_linear(solesacumulados):
	ser3.write(('tu saldo: S/. ' + str(format(solesacumulados, '.2f'))).encode())
	return 1
	
def lcd_acumula_pwyw(solesacumulados):
	ser3.write(('tu aporte: S/. ' + str(format(solesacumulados, '.2f'))).encode())	

	
def lcd_servidos_lt(servidos_lt,diff):
	ser3.write(('  + ' + str(format(servidos_lt/1000, '.3f')) + ' litros! ').encode())	

def lcd_ahorradas_bot(ahorradas_bot,diff):
	ser3.write(('  - ' + str(format(ahorradas_bot/1000, '.0f')) + ' botellas! ').encode())	
	
def lcd_agradece():
	ser3.write('gracias!!!! igua ague pe ! '.encode())	

#Fin Definiciones de Pantalla


servidos_lt = 0
servidos_lt_old = 0
servidos_litros_older = 0
loopcounter = 0	
servidos_total_old = 0
		
#Inicio Procesos de Servir Agua

while 1 == 1:
	#pantalla de bienvenida
	
	now_1 = now
	now = time.time()
	now = int((now/2)%6)
	if now != now_1:
		if modo_maquina == 0:
			nada = 0
		if modo_maquina == 1:
			nada = 0
	
	before = int(time.time())
		
	if modo_maquina == 0:
		nada = 0
	if modo_maquina == 1:
		nada = 0
		
	
	ser2.flushInput()
	sleep(.1)
	# servidos_lt = 0
	servidos_push = 0
	precio = 0.5
	
	secondcycle = 0 
	
	bytesToRead = ser2.inWaiting()
	if bytesToRead > 0:
		sleep(0.1)
		diff = 0
		bytesToRead = ser2.inWaiting()
		# print("bytes to read on ser2: ", bytesToRead)
		string_igua = str(ser2.readline(),'utf-8')
		# print("received on ser2: ", string_igua)
		string_igua = string_igua.lstrip('r')
		string_igua = string_igua.strip('\n\r')
		string_igua = string_igua.strip('\r\n')		
		if secondcycle == 0:
			try:
			    countstart = int(string_igua)
			except ValueError:
				print('error')
							
			secondcycle = 1  
			servidos_total = int(string_igua)
			servidos_litros_older = servidos_lt_old
			servidos_lt_old = servidos_lt
			servidos_lt = 0.9 * ((servidos_total) * 2640)/(22*2000)
			countstart_lt = 0.9 * ((countstart) * 2640)/(22*2000)
			ahorradas_bot = servidos_lt / 0.75
			diff = 10 - diff
			loopcounter = loopcounter + 1
			if int(loopcounter/int(2))%3 == 0:
				lcd_servidos_lt((servidos_lt),diff)
				nada = 0
			if int(loopcounter/int(2))%3 == 1:
				lcd_ahorradas_bot(ahorradas_bot,diff)
				nada = 0
			if int(loopcounter/int(2))%3 == 2:
				ser3.write('mAs agua pura!'.encode())
				nada = 0
			
			if (servidos_lt_old == servidos_lt) and (servidos_litros_older != servidos_lt_old):
				# servidos_servida = servidos_lt - servidos_lt_last
				timestamp = int(mktime(datetime.utcnow().timetuple()))
				data = {"protocol": "v2", "device": device, "at": timestamp, "data": {"colectado soles": solesacumulados, "servido litros": format(servidos_lt/1000, '.3f'), "maquina": "2"}}
				if is_connected() == True:
					carriots_response = client_carriots.send(data)
					print('conexion ok!')
					print(carriots_response.read())
				else:
					print('no connectivity available')

#Fin Procesos de Servir Agua
			# print("una vuelta mas")
					

	# deshabilita vavula y agradece
	
#		sleep(0.5)
#		display_agradece()
#		lcd_agradece()
#		before = int(time.time()) 
		# print("before: ", before)

	
