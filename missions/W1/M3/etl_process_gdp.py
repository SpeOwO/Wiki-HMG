import requests
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd
import json
import pycountry
import pycountry_convert as pc

# Extract

# loadSoup
def loadSoup(url):
    html = requests.get(url).text # html Text format으로 요청
    soup = BeautifulSoup(html, "html.parser") # soup 인스턴스 생성
    return soup

# findTable
def findTable(soup):
    table = soup.find("table", class_ = "wikitable sortable sticky-header-multi static-row-numbers") # GDP Table 선택, find와 select 차이 공부해야겠다
    df = pd.read_html(StringIO(str(table)))[0] # pandas dataframe으로 리딩
    return df

# saveDfToJson
def saveDfToJson(df):
    filePath = "missions/W1/M3/Countries_by_GDP.json"
    with open(filePath, "w") as f:
        json.dump(df.to_json(), f)

# Transform

# filterTable
def filterTable(df):
    df = df.iloc[:,[0, 1]] # 국가명, GDP 추출
    df = df.droplevel(axis = 1, level = 0) # 열 멀티인덱스 제거
    df.columns = ["Country", "GDP"] # 컬럼명 변경
    for idx, row in enumerate(df["GDP"]): # GDP - 인 국가 0으로 변경
        if row == "—":
            df.loc[idx, "GDP"] = 0
    df = df.astype({"GDP":"float"}) # GDP열 float 타입으로 변환
    df["GDP"] = (df["GDP"] / 1000).round(2)
    df.drop(0, inplace=True)
    df.sort_values("GDP", ascending = False, inplace = True)
    return df

# fillRegion
def fillRegion(df):
    region = []
    for countryName in df["Country"]:
        region.append(getContinentFromCountry(countryName))
    df["Region"] = region
    return df

# getContinent
def getContinentFromCountry(countryName):
    if countryName == "DR Congo" or countryName == "Zanzibar":
        return "Africa"
    elif countryName == "Kosovo" or countryName == "Sint Maarten":
        return "Europe"
    elif countryName == "East Timor":
        return "Asia"
    countryAlpha2 = pc.country_name_to_country_alpha2(countryName)
    continentCode = pc.country_alpha2_to_continent_code(countryAlpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(continentCode)
    return country_continent_name


# Load

# getCountriesOverGDP
def getCountriesOverGDP(df, Num):
    return df.loc[df.GDP >= Num]

def getTable(df):
    table = []
    regions = df["Region"].unique()
    for region in regions:
        table.append(getTop5CountryFromRegion(df, region))
    return table

# getTop5CountryFromRegion
def getTop5CountryFromRegion(df, region):
    return df[df["Region"] == region].head(5).drop(labels = "Region", axis = 1)


# main

def main():
    # Extract
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)" # 국가별 GDP
    soup = loadSoup(url) # soup에 추출한 html 저장
    df = findTable(soup)
    saveDfToJson(df)

    # Transform
    df = filterTable(df)
    df = fillRegion(df)

    # Load
    print(getCountriesOverGDP(df, 100))
    for table in getTable(df):
        print(table)
main()