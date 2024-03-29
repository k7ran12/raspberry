import time
import network
import requests
import ujson as json

from machine import UART, Pin

redes_wifi = [
    
    {'ssid': 'Hola', 'password': 'Datasys504'},
    {'ssid': 'Escrib', 'password': ''},
]

pin_salida = Pin(15,Pin.OUT)


uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
wlan = network.WLAN(network.STA_IF)
url = 'https://fastlineapidemo.azurewebsites.net/api/Consultas/Verificaciontiquete'

led = Pin("LED", Pin.OUT)

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
    pin_salida.on()
    time.sleep(3)
    print('Cerrar el paso')
    pin_salida.off()

def cnctWifi():
    for wifi in redes_wifi:
        ssid = wifi['ssid']
        password = wifi['password']
        wlan.active(True)
        wlan.connect(ssid, password)
        max_wait = 10
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('Waiting for connection to', ssid)
            time.sleep(1)
        if wlan.status() == 3:
            print('Connected to', ssid)
            status = wlan.ifconfig()
            print('IP:', status[0])
            led.on()
            return True
        else:
            print('Failed to connect to', ssid)
    return False

def getData():
    try:
        lectura_qr = uart1.read()
        if lectura_qr is not None:
            contador = cargar_contador()
            contador += 1
            data = {
                "idvalidador": "1",
                "verificacion": "Rasp8erry",
                "qr": lectura_qr,
                "idbus": "Bus_1",
                "accion": "ENTRADA",
                "fecha": "2024-02-22T18:29:49.368",
                "entradas": contador,
                "salidas": "0",
            }
            print(data)
            led.off()
            time.sleep(0.1)
            led.on()
            time.sleep(0.1)
            led.off()
            time.sleep(0.1)
            led.on()
            guardar_contador(contador)
            abriTorniquete()
            response = requests.post(url, json=data,timeout=1.50)
            if response.status_code == 200:
                print('Respuesta:', response.json())
            else:
                print('Error en la petición POST. Código de estado:', response.status_code)
    except Exception as e:
        print("Error:", e)

while not cnctWifi():
    print("Failed to connect to any Wi-Fi network. Retrying...")
    time.sleep(5)

print("Connected to Wi-Fi network. Starting main loop...")

ultimo_envio = time.ticks_ms()

while True:
    if wlan.isconnected():
        print("Sending GET request...")
        getData()
        try:
            if time.ticks_diff(time.ticks_ms(), ultimo_envio) >= 10000:
                contador = cargar_contador()
                print("Cada 10 segundos")
                data = {
                    "verificacion": "Conex1on",
                    "qr": "",
                    "idBus": "",
                    "accion": "",
                    "fecha": "2024-02-22T18:29:49.368",
                    "entradas": contador,
                    "salidas": 0
                }
                ultimo_envio = time.ticks_ms()
                response = requests.post(url, json=data,timeout=1.50)
                if response.status_code == 200:
                    res = response.json()
                    print('Respuesta:', res)
                    if res['limpiar'] == 1:
                        guardar_contador(0)

            
        except Exception as e:
            print("Error: ",e)
    else:
        print("Lost connection to Wi-Fi. Attempting to reconnect...")
        wlan.disconnect()
        led.off()
        while not cnctWifi():
            getData()
            print("Failed to reconnect. Retrying...")
            time.sleep(5)

    time.sleep(1)