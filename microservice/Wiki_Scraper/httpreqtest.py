import requests
from sys import argv
req = requests.get(url = "http://localhost:" + argv[1] + "/get/https://en.wikipedia.org/wiki/System")
print(req.text)
