import time
import network
import requests
import ujson as json
from machine import UART, Pin

ssid = 'Datasys2'
password = 'Datasys504'

uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))

wlan = network.WLAN(network.STA_IF)

url = 'https://fastlineapidemo.azurewebsites.net/api/Consultas/Verificaciontiquete'

#Descomentar para enviar el puso
#pin_salida = Pin(15, Pin.OUT)

def cargar_contador():
    try:
        with open('contador.json', 'r') as f:
            return json.load(f)['contador']
    except:
        return 0

def guardar_contador(contador):
    with open('contador.json', 'w') as f:
        json.dump({'contador': contador}, f)

def abriTorniquete():
    print('Abriendo torniquete')
     #pin_salida.on()
    time.sleep(5)
    print('Cerrar el paso')
     #pin_salida.off()

def cnctWifi():
    wlan.active(True)
    wlan.connect(ssid, password)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
    if wlan.status() != 3:
        print('Network Connection has failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

def getData():
    try:
        lectura_qr = uart1.read()
        if lectura_qr is not None:
            contador = cargar_contador()
            contador += 1
            data = {
                "idvalidador" : "1",
                "verificacion": "Rasp8erry",
                "qr": "lectura_qr",
                "idbus": "Bus_1",
                "accion":  "ENTRADA",
                "fecha":  "2024-02-22T18:29:49.368",
                "entradas":  contador,
                "salidas":  "0",
            }
            guardar_contador(contador)
            #response = requests.post(url, json=data)
            #if response.status_code == 200:
            if 200 == 200:#Eliminar luego
                #print('Respuesta:', response.json())
                abriTorniquete()
            else:
                print('Error en la petición POST. Código de estado:', response.status_code)
    except Exception as e:
        print("Error:", e)

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