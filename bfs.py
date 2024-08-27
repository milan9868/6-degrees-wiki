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


def bfs_search(start_page_title, target_page_title):
    # Get the start and target page IDs from the database
    cursor.execute("SELECT id FROM pages WHERE title = %s", (start_page_title,))
    start_page_id = cursor.fetchone()
    cursor.execute("SELECT id FROM pages WHERE title = %s", (target_page_title,))
    target_page_id = cursor.fetchone()

    if not start_page_id or not target_page_id:
        print("One of the pages does not exist in the database.")
        return

    start_page_id = start_page_id[0]
    target_page_id = target_page_id[0]

    # BFS setup
    queue = [(start_page_id, [start_page_id])]  # Queue of (current_page_id, path_to_current_page)
    visited = set()

    while queue:
        current_page_id, path = queue.pop(0)
        if current_page_id == target_page_id:
            # Convert the path of page IDs to titles
            cursor.execute("SELECT title FROM pages WHERE id IN %s", (tuple(path),))
            path_titles = [row[0] for row in cursor.fetchall()]
            return path_titles

        if current_page_id not in visited:
            visited.add(current_page_id)
            # Get all linked pages from the current page
            cursor.execute("SELECT to_page_id FROM links WHERE from_page_id = %s", (current_page_id,))
            linked_pages = cursor.fetchall()

            for linked_page in linked_pages:
                if linked_page[0] not in visited:
                    queue.append((linked_page[0], path + [linked_page[0]]))

    return None  # No path found

# Example usage
path = bfs_search("Kevin Bacon", "U.S. Securities and Exchange Commission")
if path:
    print(" -> ".join(path))
else:
    print("No connection found.")
