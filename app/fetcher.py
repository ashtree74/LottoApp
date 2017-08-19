import urllib
from bs4 import BeautifulSoup


def fetch_page(url):
    web = urllib.urlopen(url)
    content = web.read()
    return content


def get_links(url):
    html_doc = fetch_page(url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    linksList = []
    for link in soup.find_all('a'):
        linkHref = link.get('href')
        try:
            if linkHref.find(url) == -1 and linkHref[:4] == 'http':
                linksList.append(linkHref)
        except:
            continue
    return linksList


def get_movies(url):
    html_doc = fetch_page(url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    linksList = []
    for link in soup.find_all('a', 'topictitle'):
        linkHref = link.string
        linksList.append(linkHref)
    return linksList[3:]