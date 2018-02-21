import re


class PumpCoinExtractor:
    _letters_pattern = r'([^\s\w]|_)+'
    _emoji_removing_pattern = r'\\[a-z0-9]{5}'
    _pump_minutes_pattern = r'\d+[" "]*min|минут'
    _coin_extraction_pattern = r'(?<=\b\w)[ ]{1,}(?![ ]{0,}\w{2})'

    def extract_pump_signal(self, message_text):
        print(message_text)
        stripped_message_text = self.__remove_special_characters(message_text)
        print(stripped_message_text)
        normalized_message_text = self.__normalize_message(stripped_message_text)
        print(normalized_message_text)

    def __remove_special_characters(self, message):
        message_without_emoji = re.sub(self._emoji_removing_pattern, '', message)
        return re.sub(self._letters_pattern, '', message_without_emoji)

    def __normalize_message(self, message):
        return re.sub(self._coin_extraction_pattern, '', message)

    def extract_minutes_to_pump(self, message_text):
        normalized_message_text = self.__remove_special_characters(message_text).lower().strip()

        if normalized_message_text.isdigit():
            return normalized_message_text  # some groups like countdown using messages which contain only the minutes
        else:
            return self.__find_minutes_to_pump(normalized_message_text)

    def __find_minutes_to_pump(self, message):
        found_substrings = re.findall(self._pump_minutes_pattern, message)
        if not found_substrings:
            return None
        return ''.join((filter(str.isdigit, found_substrings[0])))


PumpCoinExtractor().extract_pump_signal("минут минут\\ude80минут \\ude80A \\ude80C\\ude80   S ++ / //b/[t;yj][3")
# PumpCoinExtractor().extract_pump_signal("минут \\ude80")
