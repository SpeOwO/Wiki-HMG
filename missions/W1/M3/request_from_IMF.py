import requests
import json
import pandas as pd

response = requests.get("https://www.imf.org/external/datamapper/api/v1/NGDPD?periods=2025,2025")
js = response.json()

with open("missions/W1/M3/Countries_by_GDP_from_IMF.json", "w") as f:
    f.write(response.text)

js_values = js.get("values")
js_NGDPD = js_values.get("NGDPD")
print(js_NGDPD)

df = pd.DataFrame(js_NGDPD).T
print(df)