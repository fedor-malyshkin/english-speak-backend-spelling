# -*- coding: utf-8 -*-


import getopt
import os
import sys
from datetime import date
from random import randint
from random import seed
from typing import Tuple, Callable, List, Generator

import boto3
import inflect
from faker import Faker
from playsound import playsound

inflect_engine = inflect.engine()
usage_rule_msg = '{app_name} -type (phone|digit|name) -s (true|false) -c <repeat_count>'
app_name = "english-speak-spelling"
faker = Faker()
seed(a=None, version=2)


def generator_phone(is_slow) -> Tuple[str, str]:
    """
    generate phone number for pronunciation

    :param is_slow:
    :return: tuple of (text, ssml)
    """
    text_to_convert = faker.phone_number()
    return text_to_convert, "<speak><say-as interpret-as='telephone'>{}</say-as></speak>".format(text_to_convert)


def generator_name(is_slow) -> Tuple[str, str]:
    # text_to_convert = faker.city()
    # text_to_convert = faker.postcode()
    # text_to_convert = faker.street_address()
    # text_to_convert = faker.street_name()
    # text_to_convert = faker.iban()
    # text_to_convert = faker.first_name()
    text_to_convert = faker.last_name()
    # text_to_convert = faker.name()
    pronounciation = "<break/>".join(text_to_convert)
    pronounciation = "{}, {}".format(text_to_convert, pronounciation)
    return text_to_convert, "<speak>{}</speak>".format(pronounciation)


def generator_number(is_slow) -> Tuple[str, str]:
    text_to_convert = str(random_number(3))
    return text_to_convert, "<speak><say-as interpret-as='cardinal'>{}</say-as></speak>".format(text_to_convert)


def generator_date(is_slow) -> Tuple[str, str]:
    day = randint(1, 30)
    month = randint(1, 12)
    year = randint(1980, 2021)
    date_obj = date(year, month, day)
    text_to_convert = f"{day}-{month}-{year}"
    suffix = "th"
    if day == 1: suffix = "st"
    if day == 2: suffix = "nd"
    if day == 3: suffix = "rd"

    text_to_show = date_obj.strftime("the %-d{} of %B, %Y".format(suffix))
    return text_to_show, '<say-as interpret-as="date" format="dmy">{}</say-as>'.format(text_to_convert)


def get_generator_by_name(val: str) -> Callable:
    mapping = {
        "phone": generator_phone,
        "name": generator_name,
        "number": generator_number,
        "date": generator_date
    }
    return mapping[val.strip().lower()]


def parse_text_generator(argv: List[str]) -> Generator:
    try:
        options, rest = getopt.getopt(argv, "t:s:c:", ['type=',
                                                       'slow=',
                                                       'count=',
                                                       ])
    except getopt.GetoptError:
        print(usage_rule_msg.format(app_name=app_name))
        sys.exit(2)

    generator_function = None
    is_slow = False
    count = 1
    for opt, val in options:
        if opt in ('-t', '--type'):
            generator_function = get_generator_by_name(val)
        elif opt in ('-s', '--slow'):
            is_slow = bool(val)
        elif opt in ('-c', '--count'):
            count = int(val)

    for i in range(0, count):
        yield generator_function(is_slow)


def random_number(length: int) -> int:
    fr = 10 ** (length - 1)
    to = 10 ** length
    return randint(fr, to)


def say_it(text: str):
    temp_file = 'temp.mp3'
    polly_client = boto3.Session(region_name='eu-central-1').client('polly')

    response = polly_client.synthesize_speech(Engine='standard',
                                              LanguageCode='en-GB',
                                              VoiceId='Brian',
                                              OutputFormat='mp3',
                                              TextType='ssml',
                                              Text=text)

    file = open(temp_file, 'wb')
    file.write(response['AudioStream'].read())
    file.close()
    playsound(temp_file)
    os.remove(temp_file)


def process_generated_text(generated_texts: List[str]) -> None:
    for t in range(0, len(generated_texts)):
        print("{}) {}".format(t, generated_texts[t][0]))
        say_it(generated_texts[t][1])


if __name__ == "__main__":
    text_generator = parse_text_generator(sys.argv[1:])
    generated_texts = list((w for w in text_generator))
    process_generated_text(generated_texts)
