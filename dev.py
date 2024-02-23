import time
import network
import requests
from machine import UART, Pin

ssid = 'Datasys2'
password = 'Datasys504'

uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

wlan = network.WLAN(network.STA_IF)

url = 'https://fastlineapidemo.azurewebsites.net/api/Consultas/Verificaciontiquete'

entradas = 0

def abriTorniquete():
    print('Abriendo torniquete')
    time.sleep(5)
    print('Cerrar el paso')

#function to connect to Wi-Fi network
def cnctWifi():
    
    wlan.active(True)
    wlan.connect(ssid, password)
    
    # Wait for connection to establish
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
                break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
    
    # Manage connection errors
    if wlan.status() != 3:
        print('Network Connection has failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )

#function to send http get request
def getData():
    try:
        lectura_qr = uart1.read()
        if lectura_qr is not None:
            #fecha_hora_actual = datetime.datetime.now()
            #fecha_hora_formateada = fecha_hora_actual.strftime("%Y-%m-%d %H:%M:%S")
            entradas += 1
            data = {
                "idvalidador" : "1",
                "verificacion": "Rasp8erry",
                "qr": lectura_qr,
                "idbus": "Bus_1",
                "accion":  "ENTRADA",
                "fecha":  "",
                "entradas":  entradas,
                "salidas":  "0",
            }
            response = requests.post(url, json=data)

            if response.status_code == 200:
                print('Respuesta:', response.json())
                abriTorniquete()
            else:
                print('Error en la petición POST. Código de estado:', response.status_code)
        data.close()

    except:
        print("could not connect (status =" + str(wlan.status()) + ")")

cnctWifi() 
   
while True:
    if wlan.isconnected():
        print("sending get request...")
        getData()
    else:
        print("attempting to reconnect...")
        wlan.disconnect()
        cnctWifi()
    time.sleep(1)