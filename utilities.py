from difflib import SequenceMatcher
from itertools import combinations
from random import randint
import db_handler as db
from sys import stdout
from os import listdir
import logging
import json



commands = ('```'
            'bot COMMANDS\n'
            'note: all commands must be preceeded by "gay ". ex: "gay help"\n'
            'note: all instances of <user> can be pings with @ or name shorthands. ex: "gay mock @GayZach" is the same as "gay mock j-zach"\n'
            'github link: https://github.com/rexosorous/discord-bot\n\n'
            'help                       displays this message.\n'
            'checknicknames             shows all the users who have nicknames for quick referencing\n'
            'mock <user>                randomizes the capitlization in that user\'s last message in this channel.\n'
            'yikes <user>               awards that user with a yikes.\n'
            'checkyikes <user>          checks how many yikes that user has been awarded.\n'
            'bruh                       shows the bruh copy pasta.\n'
            'emoji <emoji name>         uses this server\'s emoji even if it\'s nitro gated. note: don\'t surround the emoji name with colons.\n'
            'quote <user> <num>         posts in the quote channel with the user\'s last num messages in this channel\n'
            'soundboard <clip name>     joins the voice channel and plays the specified clip\n'
            'cliproulette               selects a random soundboard clip to play\n'
            'checksoundboard            shows all the clips names that the soundboard can play\n'
            'stop                       stops the soundboard clip and leaves the audio channel\n'
            'leave                      same as stop\n'
            'scan                       scans the server\'s users to update the self.bot\'s database. use if new users join.'
            '```')



def load_file(filename: str) -> dict:
    with open(filename, 'r') as file:
        contents = json.load(file)
    return contents



def get_logger():
    '''
    initializes logger
    '''
    logger = logging.getLogger('gaybot')
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename='gaybot.log', encoding='utf-8', mode='a')
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
    for file_name in listdir('soundboard/'):
        word_count = len(file_name.split(' '))
        if word_count > max_word_count:
            max_word_count = word_count
    return max_word_count



def generate_clip_bank() -> dict:
    '''
    generates a json file with all consecutive combinations of every soundboard file name
    clip_bank[2] is a dict with keys being combinations of 3 consecutive words of every soundboard file name and keys being the file name
    ex: file name = 'you stole all my glory'
    clip_bank[2] = {'you stole': 'you stole all my glory.mp3',
                    'stole all': 'you stole all my glory.mp3',
                    'all my': 'you stole all my gloyr.mp3'} etc
                NOT 'you stole' and 'you all'
    '''
    # initialize the bank
    clip_bank = {}
    clipNameList = []
    for i in range(1, get_max_word_count()+1):
        clip_bank[i] = {}
    skip = []

    # populate
    for file_name in listdir('soundboard/'):
        fixed_file_name = file_name[:-4]
        clipNameList.append(fixed_file_name)
        word_list = fixed_file_name.split(' ')
        word_count = len(word_list)
        combos = [word_list[i:j] for i, j in combinations(range(word_count+1), 2)] # gets all consecutive combos
        for phrase_list in combos:
            phrase = ' '.join(phrase_list) # make sure to turn them back into strings and not [str]
            if phrase in clip_bank[len(phrase_list)]: # ignore common word combinations like "all" or "i'm gonna"
                del clip_bank[len(phrase_list)][phrase]
                skip.append(phrase)
            if phrase not in skip:
                clip_bank[len(phrase_list)][phrase] = file_name
    return clip_bank, clipNameList



def get_clip(search: str, clip_bank: dict) -> str:
    '''
    finds the soundboard filename with the highest confidence
    for each filename, we've generated all the possible combinations of every word-length and sorted it all by word count
    we then only check combinations with word count equal to the search's word count and determine how far off it is
    then we return the filename with the highest confidence
    '''
    selected_clip = ''
    best_confidence = 0

    for phrase in clip_bank:
        confidence = SequenceMatcher(None, search, phrase).ratio()
        if confidence > best_confidence:
            selected_clip = clip_bank[phrase]
            best_confidence = confidence

    return selected_clip


def get_clipv2(clip_bank, searchTerms) -> str:
    # Fuck me this is computationally intensive
    bestClip = ''
    bestConfidence = 100000
    for clipStr in clip_bank:
        totalConfidence = 0
        for searchWord in searchTerms:
            index = clipStr.find( searchWord )
            if( index < 0 ):
                #Word not found. looking for next best...
                clipWordList = clipStr.split(' ')
                bestDistance = 100000
                bestWord = clipWordList[0]
                for clipWord in clipWordList:
                    curDistance,subs = levenshteinDistance( searchWord, clipWord )
                    curDistance += subs * 100
                    if( curDistance < bestDistance ):
                        bestDistance = curDistance
                        bestWord = clipWord
                index = clipStr.find( bestWord )
                index += bestDistance
            totalConfidence += index
            if( totalConfidence > bestConfidence ):
                # Minor optimization
                totalConfidence = 100000
                break
        if( totalConfidence < bestConfidence ):
            bestClip = clipStr
            bestConfidence = totalConfidence
    return bestClip





def levenshteinDistance(s, t):
    """
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """

    subs = 0

    rows = len(s)+1
    cols = len(t)+1
    dist = [[0 for x in range(cols)] for x in range(rows)]

    # source prefixes can be transformed into empty strings
    # by deletions:
    for i in range(1, rows):
        dist[i][0] = i

    # target prefixes can be created from an empty source string
    # by inserting the characters
    for i in range(1, cols):
        dist[0][i] = i

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = 1
            deletion = dist[row-1][col] + 1
            insertion = dist[row][col-1] + 1
            substitution = dist[row-1][col-1] + cost
            dist[row][col] = min(deletion,      # deletion
                                 insertion,     # insertion
                                 substitution)  # substitution
            if( substitution < insertion and substitution < deletion ):
                subs += 1

    return dist[row][col],subs



def get_nicknames() -> str:
    '''
    searches the users db and gets a list of all users and their respective nicknames
    '''
    nicknames = db.get_nicknames()
    msg = 'all users with nicknames\n```username: nickname'
    for user in nicknames:
        msg += f"\n{user['username']}: {user['nickname']}"
    msg += '```\nif a name is not on here, they either don\'t have a nickname or are not initialized in the database'
    msg += '\nif you would like to change or add a nickname, message j-zach'
    return msg



def mock_msg(original: str) -> str:
    '''
    randomizes the capitalization of every character in a string
    '''
    mocked = ''
    for char in original:
        if randint(0, 1) == 1:
            mocked += char.upper()
        else:
            mocked += char.lower()
    return mocked



def get_filenames(dir: str) -> [str]:
    return listdir(dir)



def build_quote(quote: str, add) -> str:
    '''
    builds quotes with correct formatting
    because crawling messages goes from recent to old, we need to make sure when we print it,
    it shows the old on top of the new without and hanging newlines
    '''
    if quote:
        quote = add + '\n' + quote
    else:
        quote = add
    return quote