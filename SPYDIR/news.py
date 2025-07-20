from yahooquery import search


def get_news(ticker):

    methods = {"YQ": YQ_news}

    for key, method in methods.items():
        try:
            related = method(str(ticker))
            if related:
                return related
        except RuntimeError as e:  # If API fails, continue to next
            continue
    return None


def YQ_news(ticker):

    search_response = search(ticker, news_count=5)
    articles = []
    for row in search_response["news"]:
        articles.append(
            {"title": row["title"], "link": row["link"], "source": row["publisher"]}
        )
    return articles
