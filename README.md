## Systematic Literature Review - Crawler and Scraper

Project by:
- Rishabh Malik
- Prudhvi Koppuravuri
- Rahul Valluri

Mentors:
- Sai Raju Ram Chander Chikkala
- VD Shanmukha Mitra

Teaching Assistant:
- Salay Jain

### **Problem Statement and Solution**

Researchers have the need to find all the relevant literature regarding their respective area of expertise. Often, they find it difficult to organise these searches as there are many libraries that they will have to traverse. Our proect tries to solve this problem by providing a single interface for the researcher to fetch information from different digital libraries.

### **Technology Requirement**

**Python** - General Purpose Language for backend
\
**Beautiful Soup** - Library to crawl websites.
\
**Django** - Framework to manage backend code.
\
**requests** - For fetching of web pages.
\
**aiohttp, asyncio** - For asynchronous fetching of web pages through threading.
\
**HTML, CSS, Javascript, Bootstrap, jQuery** - To provide web interface for the user.

### **Constraints**

**Functional Requirements**

- To get the most relevant research papers as per the user search query from ACM, ScienceDirect, Springer, IEEE.
- To provide basic search options to filter research papers.
- Eliminating the duplicate search results.

**Non-functional Requirements**
- To minimise the search extraction time.

**Unmet Requirements in the implementation**
- Elimination of duplicate search results.

### **Contributions**

- Rishabh M - ACM, Springer
\
- Prudhvi K - ScienceDirect, Frontend
\
- Rahul V - IEEEXplore, Backend

### **Installation Instructions**

```
git clone https://github.com/rahulv4667/SSD36-SLR-Tool-Crawlers.git

cd SSD36-SLR-Tool-Crawlers/

# you can initialise a virtualenv if needed here

pip3 install -r requirements.txt

cd slrsite/

python3 manage.py collectstatic
#press 'yes' when asked for confirmation

python3 manage.py runserver
```

The server must have started to serve at `127.0.0.1:8000`. 