import requests
response = requests.get("http://http://api.open-notify.org/iss-now.json")

print(response.status_code)
