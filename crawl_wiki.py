import urllib
from urllib.error import HTTPError
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pymysql

conn = pymysql.connect(unix_socket='/var/run/mysqld/mysqld.sock'
                       , host='localhost'
                       , user='milanstojanovic'
                       , password='xx'
                       , db='mysql'
                       , charset='utf8'
                    )

cursor = conn.cursor()
cursor.execute("USE scraping")

def insert_page(title):
    try:
        cursor.execute("INSERT IGNORE INTO pages (title) VALUES (%s)", (title,))
        conn.commit()
    except pymysql.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()

def insert_link(from_page_title, to_page_title):
    try:
        sql = """
        INSERT IGNORE INTO links (from_page_id, to_page_id)
        SELECT p1.id, p2.id
        FROM pages p1, pages p2
        WHERE p1.title = %s AND p2.title = %s
        """
        cursor.execute(sql, (from_page_title, to_page_title))
        conn.commit()
    except pymysql.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()

def get_title_from_url(url):
    # Remove the '/wiki/' prefix
    title = url.split('/wiki/')[-1]
    # Replace underscores with spaces and URL-decode
    title = urllib.parse.unquote(title.replace('_', ' '))
    return title

def get_links(url, depth=0, visited_pages=None):
    if visited_pages is None:
        visited_pages = set()
    if url not in visited_pages:
        visited_pages.add(url)
    if depth >= 2:
        return
    try:
        html = urlopen("https://en.wikipedia.org" + url)
        bsObj = BeautifulSoup(html, features='html.parser')
        title = get_title_from_url(url)
        insert_page(title)

        for link in bsObj.find("div", {"id": "bodyContent"}).findAll("a",
                                                                     href=re.compile("^(/wiki/)((?!:).)*$")):
            if 'href' in link.attrs:
                if link.attrs['href'] not in visited_pages:
                    new_title = get_title_from_url(link.attrs['href'])
                    insert_page(new_title)
                    insert_link(title, new_title)
                    get_links(link.attrs['href'], depth + 1, visited_pages)
    except HTTPError:
        print("error")

try:
    get_links("/wiki/Kevin_Bacon", visited_pages=set())
finally:
    cursor.close()
    conn.close()