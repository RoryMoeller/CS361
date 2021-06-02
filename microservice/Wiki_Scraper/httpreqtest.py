import requests
from sys import argv
# req = requests.post(url = "http://localhost:" + argv[1] + "/saveimgs/https://en.wikipedia.org/wiki/System")
req = requests.get(url = "http://localhost:" + argv[1] + "/get/https://en.wikipedia.org/wiki/System")
print(req.text)
