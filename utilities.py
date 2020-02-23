from difflib import SequenceMatcher
from itertools import combinations
from sys import stdout
import logging
import json
import os



def get_logger():
    '''
    initializes logger
    '''
    logger = logging.getLogger('gaybot')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename='gaybot.log', encoding='utf-8', mode='w')
    file_handler.setFormatter(logging.Formatter('%(asctime)s:   %(message)s'))
    console_handler = logging.StreamHandler(stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s:   %(message)s'))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger



def get_max_word_count() -> int:
    '''
    returns the longest word count of all soundboard files
    '''
    max_word_count = 0
    for file_name in os.listdir('soundboard/'):
        word_count = len(file_name.split(' '))
        if word_count > max_word_count:
            max_word_count = word_count
    return max_word_count



def generate_clip_bank():
    '''
    generates a json file with combinations of every soundboard file name
    clip_bank[3] is a dict with keys being combinations of 3 words of every soundboard file name and keys being the file name
    ex: file name = 'you stole all my glory'
    clip_bank[3] = {'you stole all': 'you stole all my glory.mp3',
                    'you stole my': 'you stole all my glory.mp3'} etc
    '''
    # initialize the bank
    clip_bank = {}
    for i in range(1, get_max_word_count()+1):
        clip_bank[i] = {}

    # populate
    for file_name in os.listdir('soundboard/'):
        fixed_file_name = file_name[:-4]
        word_list = fixed_file_name.split(' ')
        word_count = len(word_list)

        clip_bank[word_count][fixed_file_name] = file_name # combinations doesn't count the full string
        for words in range(word_count):
            combos = list(combinations(word_list, words))
            for phrase_list in combos:
                if phrase_list:
                    phrase = ' '.join(phrase_list)
                    clip_bank[words][phrase] = file_name

    with open('clip_bank.json', 'w+') as file:
        json.dump(clip_bank, file)



def load_file(filename: str) -> dict:
    with open(filename, 'r') as file:
        contents = json.load(file)
    return contents



def get_clip(search: str, focused_clip_bank: dict) -> str:
    '''
    finds the soundboard filename with the highest confidence
    for each filename, we've generated all the possible combinations of every word-length and sorted it all by word count
    we then only check combinations with word count equal to the search's word count and determine how far off it is
    then we return the filename with the highest confidence
    '''
    selected_clip = ''
    best_confidence = 0

    for phrase in focused_clip_bank:
        confidence = SequenceMatcher(None, search, phrase).ratio()
        if confidence > best_confidence:
            selected_clip = focused_clip_bank[phrase]
            best_confidence = confidence

    return selected_clip