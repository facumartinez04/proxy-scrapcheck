import requests
from colorama import Fore, Back, Style, init
from datetime import datetime
import threading
import queue

proxies = []
proxies_checked = []

date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
nameofproxyGuardado =  f'proxies-checked-{date}.txt'
queue_proxies = queue.Queue()
num_threads = 10

apis = [
    "https://raw.githubusercontent.com/mmpx12/proxy-list/refs/heads/master/http.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/refs/heads/master/proxylist.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/refs/heads/master/http.txt"
]

def check_proxy(proxy, tipo_proxy="http"):
    proxies_config = {
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

        response = requests.get(url_google, proxies=proxies_config, timeout=5)
        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        return False

def getProxies(url):
    response = requests.get(url)

    if response.status_code == 200:
        proxies_list = response.text.split('\n')
        return proxies_list
    return []


def guardarProxies():
    date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    print(f'Guardando proxies en {date}')
    
    nombreArchivo = f'proxies-{date}.txt'
    with open(nombreArchivo, 'w') as f:
        for proxy in proxies:
            proxy = proxy.strip()
            if proxy:
                f.write(proxy + '\n')


def guardarcheckedProxies(proxies_checked):
    with open(nameofproxyGuardado, 'a') as f:
        for proxy in proxies_checked:
            proxy = proxy.strip()
            if proxy:
                f.write(proxy + '\n')

def worker_check_proxies(tipo_proxy):
    while True:
        proxy = queue_proxies.get()
        if proxy is None:
            break

        if check_proxy(proxy, tipo_proxy):
            print(Fore.GREEN + f"Proxy {tipo_proxy.upper()} {proxy}: Funciona")
            proxies_checked.append(proxy)
            guardarcheckedProxies(proxies_checked)
        else:
            print(Fore.RED + f"Proxy {tipo_proxy.upper()} {proxy}: No funciona")
        queue_proxies.task_done()


def checkProxiesMultiThread():
    tipos_proxy = ["http", "https"]

    for tipo_proxy in tipos_proxy:
        print(f"\nVerificando proxies {tipo_proxy.upper()}:")
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=worker_check_proxies, args=(tipo_proxy,))
            threads.append(thread)
            thread.start()

        for proxy in proxies:
            queue_proxies.put(proxy)

        for _ in range(num_threads):
            queue_proxies.put(None)

        queue_proxies.join()

        for thread in threads:
            thread.join()

    guardarcheckedProxies(proxies_checked)


if __name__ == '__main__':
    init(autoreset=True)

    try:
        for api in apis:
            proxies.extend(getProxies(api))
        guardarProxies()

        checkProxiesMultiThread()
    except Exception as e:
        print(Fore.RED + f"Ocurrió un error: {e}")
