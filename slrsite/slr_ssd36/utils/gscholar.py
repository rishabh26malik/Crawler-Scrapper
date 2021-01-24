import aiohttp, asyncio, requests, json
from bs4 import BeautifulSoup

gscholar_url = "https://scholar.google.com"
scholar_loc = "/scholar"
ginit_req_str1="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q="
ginit_req_str2="&oq="
LOG="GSCHOLAR# "

ginit_params = {
    "hl" : "en",
    "as_sdt" : "0,5",
    "q" : "",
    "oq" : ""
}

bib_url_params = {
    "q" : "",
    "output" : "cite",
    "scrip" : "0",
    "hl" : "en"
}

headers = {
    "Host" : "scholar.google.com",
    "Referer" : "https://scholar.google.com",
    "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0"
}

real_url = ""
status = 0



def get_query_doi(doi):
    d_list = doi.split('/')
    return "%2F".join(d_list)

async def get_bib_url(soup, doi, url, session):
    try:
        print(soup.prettify())
        gs_ri = soup.find('div', class_='gs_ri')
        a_list = gs_ri.find_all('a')
        related_articles = list(filter(lambda a: a.get_text()=='Related articles', a_list))[0]
        unique_id = related_articles['href'].split(':')[1]

        bib_url_params["q"] = "info:"+unique_id+":scholar.google.com/"
        hdrs = headers
        hdrs["Referrer"]=url
        resp = await session.get(url=gscholar_url+scholar_loc, params=bib_url_params, headers=hdrs)

        resp= BeautifulSoup(await resp.text(), "html.parser")
        bib_url = resp.find('a', class_='gs_citi')["href"]
        if bib_url is None or bib_url == "":
            print(LOG+"Error fetching doi:{}".format(doi))
            return ""
        bib = requests.get(url=bib_url)
        return bib.text
    except Exception as e:
        print(LOG+'Exception while fetching bibtex: {}'.format(e))
        return ""

async def get_google_bibtex(dois_str):
    bibtexts = list()
    try:
        dois_list = dois_str.split(',')
        doi = dois_list[0]

        session = aiohttp.ClientSession()
    
        for doi in dois_list:
            url = ginit_req_str1 + get_query_doi(doi) + ginit_req_str2 + get_query_doi(doi)
            resp = await session.get(url=url, headers=headers)
            if resp.status != 200:
                print(LOG+"Error fetching doi:{}".format(doi))
                continue
        
            soup = BeautifulSoup(await resp.text(), "html.parser")
            bib = await get_bib_url(soup, doi, url, session)
            if bib is None or bib == "":
                print(LOG+"Error fetching doi:{}".format(doi))
                continue
            bibtexts.append(bib)
    
            await session.close()
        return bibtexts

    except Exception as e:
        print(LOG+"Exception while fetching from Google scholar:{}", e)
        return bibtexts
        await session.close()

# asyncio.get_event_loop().run_until_complete(get_google_bibtex("10.1145/1276318.1276320"))