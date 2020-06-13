import argparse
import logging
import news_page_objects as news
import re
from common import config
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')


def _news_scraper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']
    logging.info('begin scraper for {}'.format(host))
    homepage = news.HomePage(news_site_uid, host)

    articles = []

    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)

        if article:
            logger.info('article fetched!! ')
            articles.append(article)
            #print(article.title)

    print(len(articles))


def _fetch_article(news_site_uid, host, link):
    logger.info('start fetching article ar{}'.format(link))

    article = None
    try:
        article = news.Articlepage(news_site_uid, _build_link(host, link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning('error while fetching the article', exc_info=False)

    if article and not article.body:
        logger.warning('invalid article. there is no body')
        return None

    return article


def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return '{}{}'.format(host, link)
    else:
        return '{}/{}'.format(host, link)


if __name__ == '__main__':
    Parser = argparse.ArgumentParser()

    news_site_choices = list(config()['news_sites'].keys())
    Parser.add_argument('news_site',
                        help='The news site that you want to scrape',
                        type=str,
                        choices=news_site_choices)

    args = Parser.parse_args()
    _news_scraper(args.news_site)
