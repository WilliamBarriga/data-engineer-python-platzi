import argparse
import logging
import pandas as pd
import hashlib
import nltk
from urllib.parse import urlparse
from nltk.corpus import stopwords

# nltk.download('punkt')
# nltk.download('stopwords')


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

stop_words = set(stopwords.words('spanish'))


def main(filename):
    logger.info('starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    df = _fill_missing_titles(df)
    df = _generate_uids_for_rows(df)
    df = _remove_new_lines_from_body(df)
    df = _tokenize_column_title(df)
    df = _tokenize_column_body(df)
    df = _remove_duplicates_entries(df, 'title')
    df = _drop_rows_with_missing_values(df)
    _save_data(df, filename)
    # print(df)

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


def _fill_missing_titles(df):
    logger.info('filling missing titles')
    missing_titles_mask = df['title'].isna()

    missing_titles = (df[missing_titles_mask]['url']
                      .str.extract(r'(?P<missing_titles>[^/]+)$')
                      .applymap(lambda title: title.split('-'))
                      .applymap(lambda title_word_list: ' '.join(title_word_list))
                      )
    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:, 'missing_titles']

    return df


def _generate_uids_for_rows(df):
    logger.info('generating uids for rows')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )
    df['uid'] = uids
    return df.set_index('uid')


def _remove_new_lines_from_body(df):
    logger.info('remove new lines from body')

    stripped_body = (df
                     .apply(lambda row: row['body'], axis=1)
                     .apply(lambda body: list(body))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\n', ''), letters)))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\r', ''), letters)))
                     .apply(lambda letters: ''.join(letters))
                     )
    df['body'] = stripped_body

    return df


def _tokenize_column(df, column_name):
    return (df.dropna()
            .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
            .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
            .apply(lambda tokens: list(map(lambda token: token.lower(), tokens)))
            .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
            .apply(lambda valid_word_list: len(valid_word_list))
            )


def _tokenize_column_title(df):
    logger.info('tokenize title')

    df['n_tokens_title'] = _tokenize_column(df, 'title')

    return df


def _tokenize_column_body(df):
    logger.info('tokenize body')

    df['m_tokens_body'] = _tokenize_column(df, 'body')

    return df


def _remove_duplicates_entries(df, column_name):
    logger.info('removing duplicate entries')

    df.drop_duplicates(subset=[column_name], keep='first', inplace=True)

    return df


def _drop_rows_with_missing_values(df):
    logger.info('dropping rows without values')

    return df.dropna()


def _save_data(df, filename):
    clean_filename = 'clean_{}'.format(filename)

    logger.info('saving data at location {}'.format(clean_filename))

    df.to_csv(clean_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='path to the dirty data',
                        type=str)

    args = parser.parse_args()
    df = main(args.filename)

    print(df)
