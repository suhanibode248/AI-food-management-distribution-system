import os
import requests
import time

url = "http://127.0.0.1:8000/"

for _ in range(5):
    try:
        r = requests.get(url)
        print(r.status_code)
    except:
        pass
    time.sleep(1)
