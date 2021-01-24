import requests
import json, os
import aiohttp, asyncio

# setting all global variables
base_url = 'https://sciencedirect.com'
api_url = '/search/api'
citation_url = '/sdfe/apr/cite'
RESULTS_FOUND = 'resultsFound'
SEARCH_RESULTS = 'searchResults'
PII = 'pii'
SHOW_THRESHOLD = 100
LOG = 'SCIENCEDIRECT# '

citation_url_pre = 'https://www.sciencedirect.com/sdfe/arp/cite?pii='
citation_url_post = '&format=text%2Fx-bibtex&withabstract=true'

headers = {
    'User-Agent': 'Mozilla/5.0'
}

small_search_query_params = {
    'qs' : 'quantum cryptography',
    'tak': 'quantum cryptography',
    'show': 0,
    'offset': 0
}

bibtexts = list()

# method that fetches bibtex of a single article using pii number. 
async def get_bibtex(session, pii):
    try:
        url = citation_url_pre + pii + citation_url_post
        bibtex = await session.get(url=url, headers=headers)
        if bibtex.status == 200:
            bibtexts.append((await bibtex.read()).decode('utf-8'))
        else:
            print(LOG+'Error code when fetching bibtex for pii {} : {}, {}'.format(pii, bibtex.status, e))
    except Exception as e:
        print(LOG+'Error occured while fetching bibtex for pii {}, {}'.format(pii, e))


# getting json of articles info of each page by a get request.
async def get_query_page(session, page_offset, show, query):
    try:
        query['show'] = show
        query['offset'] = page_offset
        page_resp = await session.get(url=base_url+api_url, headers=headers, params=query)

        if page_resp.status == 200:
            resp_json = await page_resp.json()
            search_res = resp_json[SEARCH_RESULTS]
            print(LOG+'Fetched results {} in page {}'.format(len(search_res), page_offset))
            # creating threads for fetching bibtex of each article.
            await asyncio.gather(*[get_bibtex(session, s_res[PII]) for s_res in search_res])
        else:
            print(page_resp.real_url)
            print((await page_resp.read()).decode('utf-8'))
            print(LOG+'Error code in fetching page {} : {}'.format(page_offset, page_resp.status))
    except Exception as e:
        print(LOG+'Error occured while fetching page {}, {}'.format(page_offset, e))


async def main(num_of_results, show, query):
    # creating threads to fetch multiple pages at a time
    session = aiohttp.ClientSession()
    ret = await asyncio.gather(
        *[get_query_page(session, page_offset//show, show, query) 
            for page_offset in range(0, num_of_results, show)
            ]
        )
    await session.close()


async def get_sciencedirect_results(query, folder_name):
    try:
        # initial request to know number of results and making further requests accordingly.
        get_init_results = requests.get(base_url+api_url, 
                params=query,
                headers=headers        
                )

        init_results = get_init_results.json()
        results = init_results[RESULTS_FOUND]
        print(LOG+'Results to be fetched:{}'.format(results))
        await main(results, SHOW_THRESHOLD, query)
        print(LOG+'Fetching done')
        print(LOG+'Bibtexts fetched:{}'.format(len(bibtexts)))
        print(LOG+"Writing citations to a file")
        try:
            # creating a file and storing all bibtex in it.
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)
            file_name = os.path.join(f'./{folder_name}', 'sciencedirect_citations')
            file = open(file_name, 'w+')
            file.write("\n\n".join(bibtexts))
            file.close()
        except Exception as e:
            print(LOG+"Error occured while trying to write to \'sciencedirect_citations\':{}".format(e))

        print(LOG+"Done!!! Check the file 'sciencedirect_citations'.")
    except Exception as e:
        print(f"Exception raised while processing request")