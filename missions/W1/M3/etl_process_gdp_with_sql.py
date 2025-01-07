import requests
import json
import pandas as pd
import pycountry
import pycountry_convert

def getGDPJsonFromIMF():
    response = requests.get("https://www.imf.org/external/datamapper/api/v1/NGDPD?periods=2025,2025")
    js = response.json()
    with open("missions/W1/M3/Countries_by_GDP_from_IMF.json", "w") as f:
        f.write(response.text)
    return js

def getCountryNameDictFromIMF():
    response = requests.get("https://www.imf.org/external/datamapper/api/v1/countries")
    countryNames = response.json()["countries"]
    with open("missions/W1/M3/Country_Names.json", "w") as f:
        f.write(response.text)
    return countryNames

def getDFFromJson(js):
    js_values = js.get("values")
    js_NGDPD = js_values.get("NGDPD")
    print(js_NGDPD)
    df = pd.DataFrame(js_NGDPD).T
    return df

def addCountryName(df, countryNames):
    # 나라 아니면 행 제거
    df.reset_index(inplace = True)
    df.rename(columns = {"index":"code"}, inplace = True)
    df.rename(columns = {"2025":"GDP_USD_billion"}, inplace = True)
    df = df[df["code"].isin(countryNames)]
    col = []
    for code in df["code"]:
        col.append(countryNames[code]["label"])
    df.insert(loc = 0,column = "Country", value = col)
    return df

def addRegion(df):
    regions = []
    for code in df["code"]:
        if code == "UVK":
            region = "Europe"
        elif code == "TLS":
            region = "Asia"
        else:
            alpha2 = pycountry_convert.country_alpha3_to_country_alpha2(code)
            regionCode = pycountry_convert.country_alpha2_to_continent_code(alpha2)
            region = pycountry_convert.convert_continent_code_to_continent_name(regionCode)
        regions.append(region)
    df["Region"] = regions
    return df

def main():
    jsGDP = getGDPJsonFromIMF()
    countryNames = getCountryNameDictFromIMF()
    df = getDFFromJson(jsGDP)
    df = addCountryName(df, countryNames)
    df = addRegion(df)
    print(df)

main()

# 할 프로세스
# 국가코드 -> 국가명 -> region