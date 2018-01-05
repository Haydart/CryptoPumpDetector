import time

from psycopg2._json import Json

from database.database_connection import obtain_db_connection
from exchange_services.bittrex_service import BittrexService
from mcafee_pumps.evaluation.words_api_service import fetch_word_definitions_count

COIN_SUFFIX = 'coin'
WORD_VALUE_DENOMINATOR = 40


def create_coin_keywords_eval_dict():
    market_names_list = BittrexService().fetch_active_btc_pairs_with_names()
    db_connection = obtain_db_connection()
    markets_eval_dict = []

    for market in market_names_list[:5]:

        # create different permutations of the coin names that are plausible to be used in the tweeted image
        if market[1] != market[1].capitalize():
            market.append(market[1].capitalize())
        if market[1].lower().endswith(COIN_SUFFIX):
            market.append(market[1][:-4].lower().capitalize())
        if market[0] == market[1]:
            del market[1]

        # convert to definition count punishment partial dictionary
        current_market_dictionary = []
        for index, market_alias in enumerate(market):
            print(index, market_alias)
            if index is 0 or market_alias.lower().endswith(COIN_SUFFIX):
                # cannot punish coin names. also coins with names "*coin" are definitely not proper english words
                current_market_coin_tuple = (market_alias, 1)
            else:
                # calculate the word trust value depending on english dictionary definitions count
                current_market_word_value = 1 - fetch_word_definitions_count(market_alias) / WORD_VALUE_DENOMINATOR
                current_market_coin_tuple = (market_alias, current_market_word_value)
            current_market_dictionary.append(current_market_coin_tuple)
        print("Punishment dictionary for current coin: ", current_market_dictionary)
        print("")

        markets_eval_dict.append(current_market_dictionary)

    print(markets_eval_dict)

    db_cursor = db_connection.cursor()
    db_cursor.execute('INSERT into coins (timestamp, dict) values (%s, %s)',
                      [time.time(), Json(markets_eval_dict)])
    db_connection.commit()
    db_connection.close()


def fetch_word_evaluation_dictionary():
    db_connection = obtain_db_connection()
    db_cursor = db_connection.cursor()
    db_cursor.execute('SELECT dict FROM coins')
    word_eval_dict = db_cursor.fetchone()
    db_connection.close()
    return word_eval_dict[0]
