import requests, os
from bs4 import BeautifulSoup
import aiohttp, asyncio, json
import re
lim=2
LOG='SPRINGER# '

search_link = "https://link.springer.com/advanced-search"
subsequent_link = "https://link.springer.com/search/page/"
rest_query = {
	"all-words" : "",
	"exact-phrase" : "",
	"least-words" : "",
	"without-words" : "",
	"title-is" : "",
	"author-is" : "",
	"date-facet-mode" : "between",
	"facet-start-year" : "",
	"facet-end-year" : "",
	"show-locked-results" : "true"
}

subsequent_reqs = {
	"date-facet-mode" : "between",
	"facet-start-year" : "",
	"facet-end-year" : "",
	"showAll" : "true",
	"dc.title" : "",
	"dc.creator" : ""
}

addr="https://link.springer.com/"
writable_citations = list()

async def parse_page(session, soup, pg_num):
	try:
		href=soup.find_all('a', class_='title')
		content=soup.find_all('p', class_='content-type')
		contents=[]
		title=soup.find_all('a', class_='title')
		titles=[]
		for i in content:
			contents.append(i.get_text())
		for i in title:
			titles.append(i.get_text())
		links=[]
		for i in href:
			links.append(i['href'])
		
		n=len(contents)
		for i in range(0,n):
			toWrite="";
			authors_names=[]
			keywords=[]
			authors=[]
			DOI=[]
			pageNo=[]
			dates=[]
			######  ***********	  ARTICLES      ************  #########
			if(contents[i].strip()=="Article" ):	
			
				link=addr+links[i]
				#DOI EXTRACTION FROM FULL LINK
				m=len(links[i])
				for j in range(1,m):
					if(links[i][j]=="/"):
						j+=1
						break
				doi=links[i][j:]

				pg = await session.get(link)
				sp = BeautifulSoup(await pg.text(), 'html.parser')
				body=sp.find('body')
				u_vh_full=body.find('div',class_="u-vh-full")
				u_position_relative=u_vh_full.find('div',class_="u-position-relative")
				c_popup=u_vh_full.find('div',class_="u-container u-mt-32 u-mb-32 u-clearfix")
				c_article_main_column=c_popup.find('main',class_="c-article-main-column u-float-left js-main-column")
				article=c_article_main_column.find('article')
			
				c_article_body=article.find('div', class_="c-article-body")
				section=c_article_body.find('section')
				c_article_section=section.find('div', class_="c-article-section")
			
				#---------------ABSTRACT-------------
				Abs1_content=c_article_section.find('div', id="Abs1-content")
				Abstract=""
				if(Abs1_content != None):
					abs_para=Abs1_content.find('p')
					if(abs_para != None):
						Abstract=abs_para.get_text()
					else:
						Abstract=""
				#------------------------------------
				c_article_header=article.find('div',class_="c-article-header")
				header=c_article_header.find('header')
			
				#-----------AUTHORS-------------
				auth_list=header.find('ul',class_="c-author-list js-etal-collapsed")
				LIs=auth_list.find_all('li')
				for li in LIs:
					span=li.find('span',)
					a_tag=span.find('a')
					authors.append(a_tag.get_text())
				#------------------------------
				#------START - END PAGE NUMBER-----
				c_article_info_details=header.find('p',class_="c-article-info-details")
				startPage=c_article_info_details.find('span', itemprop="pageStart")
				endPage=c_article_info_details.find('span', itemprop="pageEnd")
				if(startPage != None):
					start_page=startPage.get_text()
					pageNo.append(start_page)
				else:
					start_page=""

				if(endPage != None):
					end_page=endPage.get_text()
					pageNo.append(end_page)
				else:
					end_page=""
				#------------------------------
				#----------KEYWORDS------------
				div_560=c_article_body.find('div', class_="c-article-buy-box c-article-buy-box--article")
				ul=sp.find('ul', class_="c-article-subject-list")
				if(ul != None):
					LI=ul.find_all('li')
					for li in LI:
						keywords.append(li.find('span').get_text())
				#------------------------------
				#------------DOI---------------
				doi_li=sp.find('li',class_="c-bibliographic-information__list-item c-bibliographic-information__list-item--doi")
				para_tag=doi_li.find('p')
				span_tag=para_tag.find('span', class_="c-bibliographic-information__value")
				DOI.append(span_tag.find('a').get_text())
				#------------------------------
				#-----------DATES--------------
				ul=sp.find('ul', class_="c-bibliographic-information__list")
				LI=ul.find_all('li')
				li_len=len(LI)
				for i in range(0,li_len-1):
					para=LI[i].find('p')
					dates.append(para.get_text())
				#------------------------------
				#--------FILE WRITING CONTENT EDITING------------------
				toWrite="@article{"+doi+",\n"
				toWrite+="title = {"+titles[i]+"},\n"
				toWrite+="link = {"+str(link)+"},\n"
				tmp="{ "+authors[0]
				m=len(authors)
				for k in range(1,m):
					tmp+=", "+authors[k];
				tmp+=" },\n"
				toWrite+="authors = "+tmp
				toWrite+="abstract = {"+Abstract+"},\n"

				m=len(keywords)
				if(m>0):
					tmp="{ "+keywords[0]

					for k in range(1,m):
						tmp+=", "+keywords[k];
					tmp+=" },\n"
				toWrite+="keywords = "+tmp

				toWrite+="doi = {"+DOI[0]+"},\n"
				if(len(pageNo)==2):
					toWrite+="page = {"+pageNo[0]+"-"+pageNo[1]+"},\n"
				elif(len(pageNo)==1):	
					toWrite+="page = {"+pageNo[0]+"},\n"
				else:
					toWrite+="page = { },\n"
				for date in dates:
					if(date[0:3]=='Pub'):
						toWrite+="year = {"+date[-4:]+"},\n"
				#-------------------------------------------------------
			
				toWrite+="}\n\n"
				writable_citations.append(toWrite)

			#################      **** ARTICLE END ****         #######################


			authors_names=[]

			if(contents[i].strip()=="Chapter and Conference Paper" or contents[i].strip()=="Chapter" ):	
				link=addr+links[i]
				#DOI EXTRACTION FROM FULL LINK
				m=len(links[i])
				for j in range(1,m):
					if(links[i][j]=="/"):
						j+=1
						break
				doi=links[i][j:]
				toWrite="@"+str(contents[i].strip())+"{"+doi+",\n"
			
				pg = await session.get(link)
				sp = BeautifulSoup(await pg.text(), 'html.parser')	
				body=sp.find('body')
				page_wrapper=body.find('div',class_="page-wrapper")
				main_wrapper=page_wrapper.find('main', id="main-content")
				main_container_uptodate_recommendations_off=page_wrapper.find('div', class_='main-container uptodate-recommendations-off')

				aside=main_container_uptodate_recommendations_off.find('aside')
			
				main_sidebar_left__content=aside.find('div', class_='main-sidebar-left__content')
				cover_image_test_cover=main_sidebar_left__content.find('div', class_='cover-image test-cover')
				a_tag=cover_image_test_cover.find('a', class_="test-cover-link")
				u_screenreader_only=a_tag.find('span',class_="u-screenreader-only")					

				main_body=main_container_uptodate_recommendations_off.find('div', class_='main-body')
			


				article=main_body.find('article', class_='main-body__content')
				ArticleHeader_main_context=article.find('div',class_="ArticleHeader main-context")
				authors_u_clearfix=ArticleHeader_main_context.find('div',class_="authors u-clearfix")
			
				## AUTHOR NAMES
				authors__list=authors_u_clearfix.find('div',class_="authors__list")
				test_contributor_names=authors__list.find('ul',class_="test-contributor-names")
				LI=test_contributor_names.find_all('li')
				for li in LI:
					span=li.find('span')
					authors_names.append(span.get_text())

				## PAPER CATEGORY, FIRST ONLINE DATE	
				main_context__container=ArticleHeader_main_context.find('div',class_="main-context__container")
				main_context__column=main_context__container.find('div',class_="main-context__column")
				span=main_context__column.find('span')
				article_dates=main_context__column.find('div',class_="article-dates")

				#------------------ABSTRACT----------------------------------
				#first div inside class="main-body"
				FulltextWrapper=article.find('div',class_="FulltextWrapper")
				section=FulltextWrapper.find('section', class_="Abstract")
				Para=section.find('p',class_="Para")
				abstract=str(Para.get_text())
				#------------------------------------------------------------
				#---------ALL DETAILS - Publisher, Dates, print/online ISBN, DOI----------------------------------
				details=[]
				if(sp != None):
					ul=sp.find('ul', class_="bibliographic-information__list bibliographic-information__list--inline")
					if(ul!=None):
						LI=ul.find_all('li')
						if(LI != None):
							for li in LI:
								spans=li.find_all('span')
								if(spans != None):
									tmp=""
									span_title=str(spans[0].get_text())
									span_value=str(spans[1].get_text())
									tmp=span_title+" : "+span_value
									details.append(span_title+" - "+span_value)
				#-------------------------------------------------------------------------------------------------
				#----------------KEYWORDS-----------------------
				keywords=[]
				if(sp != None):
					keywrd=sp.find('div', class_="KeywordGroup")
					if(keywrd != None):
						spans=keywrd.find_all('span')
					for span in spans:
						keywords.append(span.get_text().strip())
				#-----------------------------------------------

				#-----------FILE WRITING-------------------------
				# toWrite="@"+str(contents[i].strip())+"{"+doi+",\n"
				toWrite+="title = {"+titles[i]+"},\n"
				toWrite+="link = {"+str(link)+"},\n"

				tmp="{ "+keywords[0]
				m=len(keywords)
				for k in range(1,m):
					tmp+=", "+keywords[k];
				tmp+=" },\n"
			
				tmp="{ "+authors_names[0]
				m=len(authors_names)
				for k in range(1,m):
					tmp+=", "+authors_names[k];
				tmp+=" },\n"
				toWrite+="authors = "+tmp

				toWrite+="keywords = "+tmp

				toWrite+="abstract ={"+abstract+"},\n"

				for dt in details:
					if(dt[0:3]==DOI):
						toWrite+="doi = {"+dt[6:]+"},\n"
					elif(dt[0:3]=="Pub"):
						toWrite+="publisher = {"+dt[17:]+"},\n"
					elif(dt[0:3]=="Onl"):
						toWrite+="online isbn = {"+dt[14:]+"},\n"
					elif(dt[0:3]=="Pri"):
						toWrite+="print isbn = {"+dt[13:]+"},\n"
				toWrite+="}\n\n"
				writable_citations.append(toWrite)
				#---------------------------------------------------------
			print(LOG+"Pasing done from page {}".pg_num)

	except Exception as e:
		print(f"Exception while parsing {pg_num}")

# getting a page by setting appropriate parameters
async def scrape_page(session, page_num, query):
	try:
		print(LOG+"searching page {}".format(page_num))
		if "date-facet-mode" in query and len(query["date-facet-mode"])>0:
			subsequent_reqs["date-facet-mode"] = query["date-facet-mode"]
		if "facet-start-year" in query and len(query["facet-start-year"])>0:
			subsequent_reqs["facet-start-year"] = query["facet-start-year"]
		if "facet-end-year" in query and len(query["facet-end-year"])>0:
			subsequent_reqs["facet-end-year"] = query["facet-end-year"]
		if "title-is" in query and len(query["title-is"])>0:
			subsequent_reqs["dc.title"] = query["title-is"]
		if "author-is" in query and len(query["author-is"])>0:
			subsequent_reqs["dc.creator"] = query["author-is"]

		for key, value in subsequent_reqs.items():
			if subsequent_reqs[key] == "":
				print(key, subsequent_reqs[key])
				subsequent_reqs.pop(key, None)

		resp = await session.get(subsequent_link+str(page_num), params=subsequent_reqs)
		soup = BeautifulSoup(await resp.text(), 'html.parser')
		await parse_page(session, soup, page_num)
		print(LOG+"Fetched from page {}".page_num)
	except Exception as e:
		print('Exception in page {}: {}'.format(page_num, e))



async def get_springer_results(query, folder_name):
	print(LOG+"In springer query")
	print(f"{LOG}{query}")

	# making an initial fetch to learn how many pages need to be fetched.
	session = aiohttp.ClientSession()
	resp = await session.post(url=search_link, data=query)
	sp = BeautifulSoup(await resp.text(), 'html.parser')
	body=sp.find('body')
	NumPages=body.find('span',class_="number-of-pages")
	if NumPages is None:
		await parse_page(session, sp, 0)
	else:
		no_of_pages=int(NumPages.get_text().replace(',',''))
		await asyncio.gather(*[scrape_page(session, i, query) for i in range(1, no_of_pages+1)])

	# creating a file and storing bibtex in it.
	if not os.path.exists(folder_name):
            os.mkdir(folder_name)
	file_name = os.path.join(f'./{folder_name}', 'springer_citations')
	myFile = open(file_name, 'w+')
	print(LOG+str(len(writable_citations)))
	myFile.write("\n".join(writable_citations))
	await session.close()