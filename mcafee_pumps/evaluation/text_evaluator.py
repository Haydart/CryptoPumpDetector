from mcafee_pumps.detection.coin_dictionary import fetch_word_evaluation_dictionary
import operator

word_eval_dict = fetch_word_evaluation_dictionary()
print(word_eval_dict)
print('')


def extract_mentioned_coin_abbr(text):
    coin_occurrence_points = {}

    for coin_name_variants in word_eval_dict:
        coin_occurrence_points.update({coin_name_variants[0][0]: 0})
        for coin_value_tuple in coin_name_variants:
            coin_name = coin_value_tuple[0].lower()
            if count_occurrences(coin_name, text) > 0:
                occurrence_count = count_occurrences(coin_name, text)
                coin_abbr = coin_name_variants[0][0]
                coin_occurrence_points[coin_abbr] += coin_name_variants[0][1] * occurrence_count
                print(coin_name, ' found ', occurrence_count, ' times at value ', coin_value_tuple[1])

    print("")
    print(coin_occurrence_points)
    coin_to_buy = max(coin_occurrence_points.keys(), key=(lambda key: coin_occurrence_points[key]))
    print('Coin to buy is: ', coin_to_buy)
    return coin_to_buy


def count_occurrences(word, text):
    return text.lower().count(word)


# extract_mentioned_coin_abbr("""FACTOM (FCT)
# A powerhouse platform being applied to a
# wide range of fields. FCT has been endorsed
# by the Bill Gates Foundation and Homeland
# Security has a fully implemented technology
# China. It is one the few Blockchain
# and already has contracts with 25 cities in
# companies with a fully functional API that
# integrates directly with most existing software,
# allowing sharing, auditing and exchange of a
# wide range of sensitive documents. FACTOM.
# COM.""")
