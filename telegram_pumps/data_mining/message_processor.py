from datetime import datetime
from time import time

from telegram_pumps.data_mining.expected_pumps import ExpectedPumpsHandler
from telegram_pumps.database.database_retriever import *
from telegram_pumps.database.database_writer import DatabaseWriter
from telegram_pumps.pump_coin_extraction.signal_message_recognition import MessageInfoExtractor


class MessageProcessor:
    _all_groups_id_list = []
    _text_signal_groups = []
    _image_signal_groups = []
    _unknown_signal_groups = []

    _waste_message_fragments = ['joinchat', 't.me/', 'register', 'sign', 'timeanddate', 'youtu.be']

    _exchange_coin_links_prefixes = ['https://yobit', 'https://www.coinexchange.io', 'https://www.cryptopia',
                                     'https://www.binance.com']

    _info_extractor = MessageInfoExtractor()
    _database_writer = DatabaseWriter()
    _expected_pumps_handler = ExpectedPumpsHandler(_info_extractor)

    def __init__(self):
        self.__refresh_fetched_groups()

    def __refresh_fetched_groups(self):
        self._all_groups_id_list = [group[0] for group in fetch_all_group_ids(True)]
        self._text_signal_groups = fetch_text_signal_groups(True)
        self._image_signal_groups = fetch_image_signal_groups(True)
        self._unknown_signal_groups = fetch_unknown_signal_groups(True)

    def handle_channel_updates(self, message):
        group_id = message.to_id.channel_id
        message_text = message.message

        if any(unwanted in message_text for unwanted in self._waste_message_fragments) or not message_text:
            return None

        self.process_text_signal_group_message(message_text, group_id)

        # if group_id in self._text_signal_groups:
        # self.__process_text_signal_group_message(message_text)

        if group_id in self._image_signal_groups:
            self.__process_image_signal_group_message(message)

        if group_id in self._unknown_signal_groups:
            self._database_writer.save_unknown_group_message(message)

        if group_id not in self._all_groups_id_list:
            print('- Message from a non-listed group, saving message and group to db..')
            self._database_writer.save_unlisted_group(group_id)
            self.__refresh_fetched_groups()
            self._database_writer.save_unknown_group_message(message)

    def process_text_signal_group_message(self, message_text, group_id):
        exchange_from_direct_link, coin = self._info_extractor.extract_possible_pump_signal(message_text)
        # exchange will only be present if it is from a direct link containing both the exchange and the coin

        if coin:  # if no coin found, the exchange will be extracted by "extract_pump_minutes_and_exchange_if_present"
            if self._expected_pumps_handler.is_within_expected_pump_date_range(group_id):
                current_time = time()

                expected_lower_range_date = datetime.utcfromtimestamp(
                    self._expected_pump_timestamps[group_id] - self._sec_epsilon).strftime(
                    "%Y-%m-%d %H:%M:%S.%f+00:00 (UTC)")
                expected_higher_range_date = datetime.utcfromtimestamp(
                    self._expected_pump_timestamps[group_id] + self._sec_epsilon).strftime(
                    "%Y-%m-%d %H:%M:%S.%f+00:00 (UTC)")

                print('|||||||||| PUMP DETECTED at: ', exchange_from_direct_link, 'coin: ', coin, 'expected time was',
                      expected_lower_range_date, '-', expected_higher_range_date, 'actual time ',
                      datetime.utcfromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S.%f+00:00 (UTC)"))

        minutes_to_pump, pump_exchange = self._info_extractor.extract_pump_minutes_and_exchange_if_present(message_text)
        self._expected_pumps_handler.save_expected_pump_time_if_present(group_id, minutes_to_pump)
        self._expected_pumps_handler.save_expected_pump_exchange_if_present(group_id, minutes_to_pump)

    def __process_image_signal_group_message(self, message):
        print('- Message from an image signal group \n')
