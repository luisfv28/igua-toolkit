import urllib.request
from urllib.parse import urlencode
import json
import time

lastVal1 = 0
lastVal2 = 0
lastVal3 = 0
lastVal4 = 0

def carriots_get():
    device = "IGUA01@kikomayorga.kikomayorga"
    apikey = "13f622d642b12cc336fa6bfde36e1561c6ac7eea19bd88d7c32246d0fca45691"
    params = urlencode({'max' : 10, 'sort': 'at','order':-1})
    url = 'https://api.carriots.com/devices/IGUA01@kikomayorga.kikomayorga/streams/'.format(device=device)
    url = url+'?'+params
    headers = {
        'User-Agent': 'Raspberry-Carriots',
        'Carriots.apikey': apikey,
    }
 
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    obj = json.loads(response.read().decode('utf-8'))
    
    global lastVal1
    global lastVal2
    global lastVal3
    global lastVal4

    val1Found = False
    val2Found = False
    val3Found = False
    val4Found = False
    for o in obj["result"]:
      nroMaq = o['data']['maquina']
      if not val1Found and nroMaq == '1':
          lastVal1 = float(o['data']['servido litros'])
          val1Found = True
      if not val2Found and nroMaq == '2':
          lastVal2 = float(o['data']['servido litros'])
          val2Found = True
      if not val3Found and nroMaq == '3':
          lastVal3 = float(o['data']['servido litros'])
          val3Found = True
      if not val4Found and nroMaq == '4':
          lastVal4 = float(o['data']['servido litros'])
          val4Found = True
    return {
		'1': lastVal1,
		'2': lastVal2,
		'3': lastVal3,
		'4': lastVal4
    }
    # print(obj["result"][0]["data"])

def write_to_display(litros, dinero):
    print('litros', litros)
    print('dinero', dinero)
    
   
def main():
    # cada 30 segundos
    starttime = time.time()
    duracion = 10
    while True:
        result = carriots_get()
        litros = result['1'] + result['2'] + result['3']
        dinero = result['4']
        write_to_display(litros, dinero)
        time.sleep(duracion - ((time.time() - starttime) % duracion))
 
if __name__ == '__main__':
    main()

# {"_id":"59def5e25c5d754478104f43","_t":"str","at":1507802158,"device":"IGUA01@kikomayorga.kikomayorga","protocol":"v2","data":{"colectado soles":0.1,"servido litros":"0.210"},"id_developer":"d5780fcf69663b695d90402695d4878cdaf64e765e972558111d0cbc8fd51a1c@kikomayorga.kikomayorga","created_at":1507784162,"owner":"kikomayorga"}]}
