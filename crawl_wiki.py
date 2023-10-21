from urllib.error import HTTPError
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


try:
    html = urlopen("https://en.wikipedia.org/wiki/Beautiful_Soup_(HTML_parser)#:~:text=Beautiful%20Soup%20is%20a%20Python,is%20useful%20for%20web%20scraping.")
except HTTPError:
    print("error")
else:    
    bsObj = BeautifulSoup(html)
    for link in bsObj.find("div", {"id":"bodyContent"}).findAll("a",
    href = re.compile("^(/wiki/)((?!:).)*$")):
        if 'href' in link.attrs:
            print(link.attrs['href'])
