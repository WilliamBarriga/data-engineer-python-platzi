import argparse
import logging
import pandas as pd
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def main(filename):
    logger.info('starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    print(df)

    return df


def _read_data(filename):
    logger.info('reading file {}'.format(filename))

    return pd.read_csv(filename, encoding="ISO-8859-1")


def _extract_newspaper_uid(filename):
    logger.info('extracting news paper uid')
    newspaper_uid = filename.split('_')[0]

    logger.info('newspaper uid detected: {}'.format(newspaper_uid))
    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info('filling newspaper uid column with {}'.format(newspaper_uid))
    df['newspaper_uid'] = newspaper_uid

    return df


def _extract_host(df):
    logger.info('extracting host from urls')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='path to the dirty data',
                        type=str)

    args = parser.parse_args()
    df = main(args.filename)
    print(df)
