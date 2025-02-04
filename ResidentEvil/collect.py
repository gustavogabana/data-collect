# %%

import requests as req
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'DNT': '1',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

def get_content(url):
    res = req.get(url, headers=headers)
    return res

def get_basic_infos(soap):
    div_page = soap.find("div", class_="td-page-content")
    paragrafo = div_page.find_all("p")[1]
    ems = paragrafo.find_all("em")
    data = {}
    for i in ems:
        chave, valor, *_ = i.text.split(":")
        chave.strip(" ")
        valor.strip(" ")
        data[chave] = valor
    return data

def get_aparitions(soap):
    lis = (soap.find("div", class_="td-page-content")
        .find("h4")
        .find_next()
        .find_all("li"))

    aparicoes = [i.text for i in lis]
    return aparicoes

def get_personagem_infos(url):
    res = get_content(url)
    if res.status_code != 200:
        print("Não foi possível obter os dados da página")
        return {}
    else :
        soap = BeautifulSoup(res.text)
        data = get_basic_infos(soap)
        data["Aparicoes"] = get_aparitions(soap)
    return data

def get_links():
    url = 'https://www.residentevildatabase.com/personagens/'
    res = req.get(url, headers=headers)
    soap_personagens = BeautifulSoup(res.text)
    ancoras = (soap_personagens.find("div", class_="td-page-content")
    .find_all("a"))

    links = [i["href"] for i in ancoras]
    return links

# %%

links = get_links()
data = []
for i in tqdm(links):
    d = get_personagem_infos(i)
    d['Link'] = i
    nome = i.strip("/").split("/")[-1].replace("-", " ").title()
    d['Nome'] = nome
    data.append(d)
data


# %%
df = pd.DataFrame(data)
df.to_parquet("data-re.parquet", index=False)
df_new = pd.read_parquet("data-re.parquet")
df.to_pickle("data-re.pkl")
