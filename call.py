import time
import requests

for i in range(41):
    responce = requests.get('http://localhost:8000/home/')
    print('status', responce.status_code)
    time.sleep(2)