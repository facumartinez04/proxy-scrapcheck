import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import colorama

colorama.init()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
}
TIMEOUT = 5
TEST_URL = "http://www.google.com"
MAX_WORKERS = 50

github_proxy_list_urls = [
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/main/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/main/proxy-list-raw.txt"
]

def fetch_proxy_list(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar {url}: {e}")
        return []


def check_proxy(proxy):
    proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
    start_time = datetime.now()
    is_valid = False
    latency = None
    try:
        response = requests.get(TEST_URL, headers=HEADERS, proxies=proxies, timeout=TIMEOUT)
        latency = (datetime.now() - start_time).total_seconds()
        if response.status_code == 200:
            is_valid = True
    except:
        is_valid = False

    if is_valid:
        print(f"{colorama.Fore.GREEN}Proxy Válido: {proxy} (Latencia: {latency:.2f}s){colorama.Style.RESET_ALL}")
        try:
            with open("valid_proxies.txt", "a") as f:
                f.write(f"{proxy}\n")
        except Exception as e:
            print(f"{colorama.Fore.YELLOW}Error al guardar proxy en archivo: {e}{colorama.Style.RESET_ALL}")
        return (proxy, latency)
    else:
        print(f"{colorama.Fore.RED}Proxy No Válido: {proxy}{colorama.Style.RESET_ALL}")
        return None


def main():
    all_proxies = []
    with open("valid_proxies.txt", "w") as f:
        f.write("")

    for url in github_proxy_list_urls:
        proxies = fetch_proxy_list(url)
        all_proxies.extend(proxies)

    print(f"Se descargaron {len(all_proxies)} proxies. Verificando...\n")

    valid_proxies = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in all_proxies}
        for future in as_completed(future_to_proxy):
            result = future.result()
            if result:
                valid_proxies.append(result)

    valid_proxies.sort(key=lambda x: x[1])

    print(f"\n{colorama.Fore.CYAN}Proxies válidos encontrados (ordenados por latencia):{colorama.Style.RESET_ALL}")
    for proxy, latency in valid_proxies:
        print(f"{proxy} (Latencia: {latency:.2f}s)")

    print(f"\n{colorama.Fore.CYAN}Proxies válidos guardados en 'valid_proxies.txt' a medida que se verificaban.{colorama.Style.RESET_ALL}")


if __name__ == "__main__":
    main()
