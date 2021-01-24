import requests
import math
from random import choice
import asyncio
import aiohttp
import os
import json
from bs4 import BeautifulSoup

# setting necessary global variables
base_url = "https://dl.acm.org"
main_page_loc = "/action/doSearch"
citations_loc = "/action/exportCiteProcCitation"
LOG = 'ACM# '


per_page_size = 50

base_query = {
    "expand" : "dl",
    "AllField" : "Title:(text analytics)",
    "pageSize" : str(per_page_size)
}

small_base_query = {
    "fillQuickSearch" : "false",
    "expand" : "dl",
    "Ppub" : "[20200424 TO 20201024]",
    "AllField": "Title:(text analytics)"
}

medium_base_query = {
    "fillQuickSearch":	"false",
    "expand":"dl",
    "field1":"Abstract",
    "text1":"quantum cryptography"
	
}

bibtex_base_query = {
    "targetFile" : "custom-bibtex",
    "format" : "bibTex"
}


bibtexts = list()

def get_dois(markup):
    try:
        # parse dois from the page 
        soup = BeautifulSoup(markup, "html.parser")
        ul = soup.find('ul', class_ = 'search-result__xsl-body items-results rlist--inline')
        papers_list = ul.find_all('li', class_ = 'search__item issue-item-container')

        dois = list()

        for paper in papers_list:
            span = paper.find('span', class_ = "hlFld-Title")
            a = span.find('a')
            href = a["href"]

            # obtaining doi from a full url
            doi_l = href.split("/")
            doi = doi_l[-2] + "/" + doi_l[-1]
            dois.append(doi)

        dois_str = ",".join(dois)
        return dois_str

    except Exception as e:
        print(LOG+"Exception occured while parsing for dois", e)



async def get_bibtex(session, dois_str):
    try:
        # getting bibtex from as json by a direct post call to backend with all dois
        bibtex_query = bibtex_base_query
        bibtex_query["dois"] = dois_str
        resp = await session.post(url = base_url + citations_loc, data = bibtex_query)
        print(LOG+"Bibtex status:", resp.status)
        json_resp = await resp.json()
        return json_resp["items"]
    except Exception as e:
        print(LOG+"Exception occured while fetching bibtex", e)



async def page_fetch(session, start_pg):
    try:
        # get page of offset start_pg
        base_query["startPage"] = str(start_pg)
        resp = await session.get(url = base_url + main_page_loc, params = base_query)
        print(f"{LOG}{resp.status}")
        resp_text = await resp.text()
        dois_str = get_dois(resp_text)
        bibtext_resp = await get_bibtex(session, dois_str)
        bibtexts.extend(bibtext_resp)

    except Exception as e:
        print(LOG+"Exception occured in fetching page: {}".format(start_pg))
        print(LOG+"Exception is ", e)


async def main(pages):
    session = aiohttp.ClientSession()
    ret = await asyncio.gather(*[page_fetch(session, start_pg) for start_pg in range(pages)])
    print(LOG+"Finalized all. ret is a list of len {} outputs.".format(len(ret)))
    await session.close()


async def get_acm_results(query, folder_name):
    try:
        base_query = query

        # fetching initially to learn number of results and accordingly make requests
        first_page = requests.get(base_url+main_page_loc, params= base_query)
        print(first_page.status_code)

        soup = BeautifulSoup(first_page.content, "html.parser")

        hitsLength = soup.find('span', class_ = 'hitsLength')
        if hitsLength is None:
            pages = 1
        else:
            results = int(hitsLength.get_text().replace(",", ""))
            print(LOG+str(results))
            pages = math.ceil(results/per_page_size)
            print(LOG+str(pages))
        
        
        await main(pages)
        print(LOG+"Bibtexts length: {}".format(len(bibtexts)))

        # creating file to store citations in
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        file_name = os.path.join(f'./{folder_name}', 'acm_citations')
        acm_citations = open(file_name, 'w+')

        # building bibtex from json responses
        for bibtext in bibtexts:
            for key in bibtext:
                try:
                    toWrite='@'+bibtext[key]['type']+"{"
                    toWrite+=key+",\n"
                    for val in bibtext[key]:
                        authors="{"
                        if(val=='id' or val=='accessed' or val=='issued' or val == 'type'):
                            continue
                        if(val=='author'):
                            names=bibtext[key][val]
                            name=names[0]
                            n=len(names)
                            authors+=name['given']+" "+name['family']
                            for j in range(1, n):
                                authors+=", "+names[j]['given']+" "+names[j]['family']
                            authors+="}"
                            toWrite+="authors = "+authors+",\n"
                        elif(val=='original-date'):
                            tmp=bibtext[key][val]['date-parts'][0]
                            year="Year = {"+str(tmp[0])+"},\n"
                            toWrite+=year
                        else:
                            toWrite+=val+" = {"+str(bibtext[key][val])+"},\n"
            
                    toWrite+="}\n\n"
                    acm_citations.write(toWrite)
                except Exception as e:
                    print(LOG+ "Exception in writing a record to a file ", e)

    except Exception as e:
        print(LOG+ "Exception occured in ACM RESULTS: ", e)