import requests
from bs4 import BeautifulSoup
import wikipedia


def get_wiki(ticker, name):
    url, page = get_url_page(ticker, name)
    summary = get_summary(page)
    img = get_img(url)
    wiki_data = {
        "summary": summary,
        "url": url,
        "img": img,
    }
    return wiki_data


def get_url_page(ticker, name):
    # TODO - fix TSLA
    if ticker == "TSLA":
        results = wikipedia.search(name + "Inc")
    else:
        results = wikipedia.search(name)
    page = results[0].replace(" ", "_").replace(".", "")
    try:
        url = "https://en.wikipedia.org/wiki/" + page
        return url, page
    except:
        raise Warning("Page Not Found")


def get_summary(page):
    tick_page = wikipedia.WikipediaPage(page)
    return tick_page.summary


def get_img(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        raise Warning("Page Not Found")
    info_table = soup.find_all("table", {"class": "infobox"})

    img_links = []
    for box in info_table:
        img_links.extend(box.find_all("img"))

    img = "https:" + img_links[0].get("src")
    return img
