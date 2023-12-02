# -- coding: utf-8 --

import json
import requests

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# Defining the Proxy and ProxyManager classes
class Proxy:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def __repr__(self):
        return f"Proxy(host={self.host}, port={self.port}, user={self.user}, password={self.password})"

class RequestTool(metaclass=SingletonMeta):
    def __init__(self):
        self.proxies = []
        self.last_proxy_index = -1

    def add_proxy(self, proxy):
        self.proxies.append(proxy)
        self.last_proxy_index += 1

    def get_last_proxy(self):
        if self.last_proxy_index >= 0:
            return self.proxies[self.last_proxy_index]
        return None

    def read_from_proxy_file(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                proxy_data = data['proxies']
                print(f"Loaded {len(proxy_data)} proxies from '{filename}'.")
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading proxy file: {e}")
            return []

        self.proxies = []  # Resetting the list
        try:
            for p in proxy_data:
                proxy_obj = Proxy(p['host'], p['port'], p['user'], p['pass'])
                self.proxies.append(proxy_obj)
        except KeyError as e:
            print(f"Error: Missing key in proxy data: {e}")
            self.proxies = []  # Resetting the list in case of error
            return []

        return self.proxies

    def get_proxy(self):
        if len(self.proxies) == 0:
            print("Error: No proxies loaded.")
            return None

        proxy = self.proxies[self.last_proxy_index]
        self.last_proxy_index += 1
        if self.last_proxy_index >= len(self.proxies):
            self.last_proxy_index = 0

        return proxy


    def get(self, url, **kwargs ):

        if len(self.proxies) == 0:
            print("No proxies available, making a direct request.")
            return requests.get(url, **kwargs)

        proxy = self.get_proxy()
        if proxy is None:
            print("Failed to retrieve a proxy, making a direct request.")
            return requests.get(url, **kwargs)


        ### Be careful
        ### Both http and https are set to http
        ### This is because the proxy is not https
        ### If you are using an https proxy, change it to https
        proxies = {
            "http": f"http://{proxy.user}:{proxy.password}@{proxy.host}:{proxy.port}",
            "https": f"http://{proxy.user}:{proxy.password}@{proxy.host}:{proxy.port}"
        }

        try:
            response = requests.get(url, proxies=proxies, **kwargs)
            return response
        except requests.exceptions.RequestException:
            print("Request Exception while while fetching", url)
            return None
        except Exception as e:
            print(f"Unaccounted exception while fetching {url}")
            return None