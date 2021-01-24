import requests
import json
import asyncio
import aiohttp
import os
from bs4 import BeautifulSoup
from .gscholar import get_google_bibtex

# setting up global variables
base_url = "https://ieeexplore.ieee.org"
rest_loc = "/rest/search"
citations_loc = "/xpl/downloadCitations"
rest_headers = {
    "Accept" : "application/json, text/plain, */*",
    "Content-Type" : "application/json",
    "Accept-Encoding" : "gzip, deflate, br",
    "Host" : "ieeexplore.ieee.org",
    "Origin" : "https://ieeexplore.ieee.org"
}
LOG = 'IEEE# '

citations_headers = {
    "Accept" : "application/json, text/plain, */*",
    "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept-Encoding" : "gzip, deflate, br",
    "Host" : "ieeexplore.ieee.org",
    "Origin" : "https://ieeexplore.ieee.org"
}

rest_params = {
    "queryText" : "\"text\" AND \"analytics\"\"OR\"music",
    "returnType" : "SEARCH",
    "pageNumber" : "2",
}

citations_params = {
    "recordIds" : "",
    "download-format" : "download-bibtex",
    "citations-format" : "citation-abstract"
}

responses = list()
citations = list()

# making dois string to request to server
def get_dois_str(records):
    dois_list = list()
    for record in records:
        dois_list.append(record['articleNumber'])
    return ','.join(dois_list)

async def get_citations(session, page_num, resp_json):
    try:
        # fetching citations for a list of dois
        citations_params["recordIds"] = get_dois_str(resp_json["records"])
        citations_resp = await session.post(url = base_url+citations_loc, 
                                headers=citations_headers, 
                                params=citations_params)
        if citations_resp.status == 200:
            citations.append(await citations_resp.text())
    except Exception as e:
        print(LOG+"Exception raised when fetching from IEEE. Fetching from Google Scholar")
        try:
            gbibtext = await get_google_bibtex(dois_str)
            if len(gbibtexts > 0):
                citations.append(gbibtext)
        except Exception as e:
            print(LOG+'Error occured while fetching citations:{}'.format(page_num))

async def page_fetch(session, page_num):
    try:
        # fetching json of details that are displayed in HTML page.
        rest_params["pageNumber"] = page_num
        resp = await session.post(url = base_url+rest_loc, headers=rest_headers, data=json.dumps(rest_params))
        resp_json = await resp.json()
        responses.append(resp_json)
        await get_citations(session, page_num, resp_json)
       
    except Exception as e:
        print(LOG+"Error occured while fetching page {} : {}".format(page_num, e))


async def main(total_pages):
    # creating separate threads for each page fetch.
    session = aiohttp.ClientSession()
    ret = await asyncio.gather(*[page_fetch(session, page_num) for page_num in range(1, total_pages+1)])
    await session.close()


async def get_ieee_results(query, folder_name):
    # prepaing query from given query
    rest_params["queryText"] = query["queryText"]
    if "ranges" in query:
        rest_params["ranges"] = query["ranges"]

    # making initial fetch to find total pages to be fetched.    
    resp_str = requests.post(base_url+rest_loc, headers=rest_headers, data=json.dumps(rest_params))
    json_resp = json.loads(resp_str.content)
    total_pages = json_resp["totalPages"]
    print(LOG+"Initial Fetch done. Total pages to be fetched are:{}".format(total_pages))

    # fetching all pages
    print(LOG+"Fetching {} pages....Have patience. Get a coffee.".format(total_pages))
    await main(total_pages)
    print(LOG+"Fetching done.")

    # removing <br> tags from downloaded citations
    print(LOG+"Sanitising citations text")
    for index, citation in enumerate(citations):
        soup = BeautifulSoup(citation, "html.parser")
        for s in soup.find_all("br"):
            s.extract()
        citations[index] = soup.prettify()

    print(LOG+"Writing citations to a file")
    try:
        # creating file and storing all citations in it.
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        file_name = os.path.join(f'./{folder_name}', 'ieee_citations')
        file = open(file_name, 'w+')
        file.write("\n\n".join(citations))
        file.close()
    except Exception as e:
        print(LOG+"Error occured while trying to write to \'ieee_citations\':{}".format(e))

    print(LOG+"Done!!! Check the file 'ieee_citations'.")