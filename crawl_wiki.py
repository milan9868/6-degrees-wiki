from urllib.error import HTTPError
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


visited_pages = set()


def get_links(url, depth = 0):
    if depth > 2:
        return
    global visited_pages
    try:
        html = urlopen("https://sr.wikipedia.org"+url)
    except HTTPError:
        print("error")
    else:    
        bsObj = BeautifulSoup(html, features = 'html.parser')
        for link in bsObj.find("div", {"id":"bodyContent"}).findAll("a",
                                href = re.compile("^(/wiki/)((?!:).)*$")):
            if 'href' in link.attrs:
                if link.attrs['href'] not in visited_pages:
                    visited_pages.add(link.attrs['href'])
                    print(link.attrs['href'])
                    get_links(link.attrs['href'], depth + 1)


get_links("/wiki/Андрус_Ансип")