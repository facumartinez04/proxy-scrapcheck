import requests
from colorama import Fore, Back, Style, init
from datetime import datetime
import threading
import queue
import signal
import sys
import os

proxies = []
proxies_verificados = []
queue_proxies = queue.Queue()
num_threads = 10
nombre_archivo_guardado_verificados = ""
total_proxies_descargados = 0
proxies_funcionales_http = 0
proxies_funcionales_https = 0
proxies_no_funcionales = 0
proxies_checkeados_count = 0 # Contador de proxies checkeados
lock_contadores = threading.Lock()
color_cycle = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
color_index = 0

apis_fuentes_proxy = [
    "https://raw.githubusercontent.com/mmpx12/proxy-list/refs/heads/master/http.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/refs/heads/master/proxylist.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/refs/heads/master/http.txt"
]

def checkear_proxy(proxy, tipo_proxy="http"):
    config_proxies = {
        tipo_proxy: f"{tipo_proxy}://{proxy}"
    }

    try:
        if tipo_proxy == "http":
            url_google = "http://www.google.com"
        elif tipo_proxy == "https":
            url_google = "https://www.google.com"
        else:
            print("Tipo de proxy no válido. Debe ser 'http' o 'https'.")
            return False

        response = requests.get(url_google, proxies=config_proxies, timeout=5)
        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        return False

def obtenerProxies(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        proxies_list = response.text.split('\n')
        return proxies_list
    except requests.exceptions.RequestException as e:
        print(Fore.YELLOW + f"Advertencia: No se pudieron obtener proxies de {url} - {e}")
        return []


def guardarProxiesVerificados(proxies_verificados):
    global nombre_archivo_guardado_verificados
    print(f'Guardando proxies verificados en {nombre_archivo_guardado_verificados}')
    with open(nombre_archivo_guardado_verificados, 'a') as archivo:
        for proxy in proxies_verificados:
            proxy = proxy.strip()
            if proxy:
                archivo.write(proxy + '\n')

def worker_checkear_proxies(tipo_proxy):
    global proxies_funcionales_http, proxies_funcionales_https, proxies_no_funcionales, proxies_checkeados_count

    while True:
        proxy = queue_proxies.get()
        if proxy is None:
            break

        funciona = checkear_proxy(proxy, tipo_proxy)
        with lock_contadores:
            proxies_checkeados_count += 1 # Incrementa contador de checkeados
            if funciona:
                proxies_verificados.append(proxy)
                if tipo_proxy == "http":
                    proxies_funcionales_http += 1
                elif tipo_proxy == "https":
                    proxies_funcionales_https += 1
            else:
                proxies_no_funcionales += 1
            actualizar_titulo()
            imprimir_status() # Imprimir status actualizado en pantalla
        queue_proxies.task_done()


def checkearProxiesMultiThread():
    tipos_proxy = ["http", "https"]

    imprimir_status() # Imprimir status inicial antes de empezar

    for tipo_proxy in tipos_proxy:
        print(f"\nVerificando proxies {tipo_proxy.upper()}...")
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=worker_checkear_proxies, args=(tipo_proxy,))
            threads.append(thread)
            thread.start()

        for proxy in proxies:
            queue_proxies.put(proxy)

        for _ in range(num_threads):
            queue_proxies.put(None)

        queue_proxies.join()

        for thread in threads:
            thread.join()

    guardarProxiesVerificados(proxies_verificados)
    imprimir_status() # Imprimir status final


def actualizar_titulo():
    titulo = f"Proxy Scraper and Checker by Mahada | " \
             f"Totales: {total_proxies_descargados} | " \
             f"Verificados: {len(proxies_verificados)} | " \
             f"HTTP OK: {proxies_funcionales_http} | " \
             f"HTTPS OK: {proxies_funcionales_https} | " \
             f"Fallidos: {proxies_no_funcionales} | " \
             f"Threads: {num_threads}"
    print(f'\033]0;{titulo}\007', end='', flush=True)

def imprimir_titulo_centrado():
    global color_index
    terminal_width = os.get_terminal_size().columns
    titulo_principal_line1 = " ________    ____  ____  "
    titulo_principal_line2 = "/  _____/  _/ ___\/ __ \ "
    titulo_principal_line3 = "/   \  ___ \___ \\  ___/ "
    titulo_principal_line4 = "\    \_\  /____/ \___  >"
    titulo_principal_line5 = " \______  /          \/ "
    titulo_principal_line6 = "        \/             "
    titulo_secundario = "BY MAHADA"

    color_titulo = color_cycle[color_index % len(color_cycle)]
    color_index += 1

    lines_principal = [titulo_principal_line1, titulo_principal_line2, titulo_principal_line3, titulo_principal_line4, titulo_principal_line5, titulo_principal_line6]
    padding_secundario = (terminal_width - len(titulo_secundario)) // 2

    print("\n" * 1)

    for line in lines_principal:
        padding_line = (terminal_width - len(line)) // 2
        print(color_titulo + "." * padding_line + line + "." * padding_line + Style.RESET_ALL)

    print(color_titulo + "." * padding_secundario + titulo_secundario + "." * padding_secundario + Style.RESET_ALL)
    print("\n" * 1)

def imprimir_status():
    global proxies_checkeados_count, total_proxies_descargados, proxies_funcionales_http, proxies_funcionales_https, proxies_no_funcionales
    terminal_width = os.get_terminal_size().columns
    status_message = f"Checkeados: {proxies_checkeados_count} / {total_proxies_descargados} | " \
                     f"Buenos HTTP: {proxies_funcionales_http}  HTTPS: {proxies_funcionales_https} | " \
                     f"Malos: {proxies_no_funcionales}"
    padding_status = (terminal_width - len(status_message)) // 2
    status_line = Fore.CYAN + "-" * terminal_width + Style.RESET_ALL # Línea separadora

    # ANSI escape codes para limpiar la línea y mover el cursor al inicio de la línea
    clear_line = '\033[K'
    cursor_up_one_line = '\033[F'

    # Imprimir o actualizar el mensaje de estado
    print(cursor_up_one_line + clear_line + status_line) # Mueve cursor arriba, limpia línea y re-imprime línea separadora
    print(clear_line + " " * padding_status + status_message + Style.RESET_ALL) # Limpia línea y imprime mensaje centrado
    print(clear_line + status_line) # Limpia línea y re-imprime línea separadora


def signal_handler(sig, frame):
    print(Fore.RED + "\n\n[!] Recibida señal de interrupción (Ctrl+C). Cerrando...")
    guardarProxiesVerificados(proxies_verificados)
    print(Fore.GREEN + "[+] Proxies verificados guardados. Saliendo.")
    sys.exit(0)


if __name__ == '__main__':
    init(autoreset=True)
    actualizar_titulo()
    signal.signal(signal.SIGINT, signal_handler)

    imprimir_titulo_centrado()

    try:
        num_threads_input = input(Fore.CYAN + "Introduce el número de threads a usar (por defecto 10): " + Style.RESET_ALL)
        if num_threads_input:
            try:
                num_threads = int(num_threads_input)
                if num_threads <= 0:
                    num_threads = 10
                    print(Fore.YELLOW + "Número de threads inválido. Usando el valor por defecto: 10")
            except ValueError:
                num_threads = 10
                print(Fore.YELLOW + "Entrada inválida. Usando el valor por defecto: 10")

        fecha_actual_archivo = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        nombre_archivo_guardado_verificados = f'proxies-verificados-{fecha_actual_archivo}.txt'

        print(Fore.GREEN + f"Guardando proxies verificados en: {nombre_archivo_guardado_verificados}" + Style.RESET_ALL)

        print(Fore.CYAN + "\nDescargando listas de proxies..." + Style.RESET_ALL)
        for api in apis_fuentes_proxy:
            lista_proxies_api = obtenerProxies(api)
            proxies.extend(lista_proxies_api)
            total_proxies_descargados += len(lista_proxies_api)
        print(Fore.GREEN + f"Total de proxies descargados: {total_proxies_descargados}" + Style.RESET_ALL)

        print(Fore.CYAN + "\nVerificando proxies con Multi-Thread..." + Style.RESET_ALL)
        checkearProxiesMultiThread()
        print(Fore.GREEN + f"\nVerificación de proxies completada. Proxies verificados guardados en: {nombre_archivo_guardado_verificados}" + Style.RESET_ALL)
        print(Fore.GREEN + f"Proxies HTTP Funcionales: {proxies_funcionales_http}" + Style.RESET_ALL)
        print(Fore.GREEN + f"Proxies HTTPS Funcionales: {proxies_funcionales_https}" + Style.RESET_ALL)
        print(Fore.RED + f"Proxies No Funcionales: {proxies_no_funcionales}" + Style.RESET_ALL)


    except Exception as e:
        print(Fore.RED + f"Ocurrió un error inesperado: {e}" + Style.RESET_ALL)
    finally:
        actualizar_titulo()
        print(Style.RESET_ALL)
