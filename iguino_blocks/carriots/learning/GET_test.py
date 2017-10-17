import urllib.request
from urllib.parse import urlencode
 
def main():
    device = "IGUA01@kikomayorga.kikomayorga"
    apikey = "13f622d642b12cc336fa6bfde36e1561c6ac7eea19bd88d7c32246d0fca45691"
    params = urlencode({'max' : 1, 'sort': 'at','order':-1})
    url = 'https://api.carriots.com/devices/IGUA01@kikomayorga.kikomayorga/streams/'.format(device=device)
    url = url+'?'+params
    headers = {
        'User-Agent': 'Raspberry-Carriots',
        'Carriots.apikey': apikey,
    }
 
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    print(response.read())
 
if __name__ == '__main__':
    main()

# {"_id":"59def5e25c5d754478104f43","_t":"str","at":1507802158,"device":"IGUA01@kikomayorga.kikomayorga","protocol":"v2","data":{"colectado soles":0.1,"servido litros":"0.210"},"id_developer":"d5780fcf69663b695d90402695d4878cdaf64e765e972558111d0cbc8fd51a1c@kikomayorga.kikomayorga","created_at":1507784162,"owner":"kikomayorga"}]}
