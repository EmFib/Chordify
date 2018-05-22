from bs4 import BeautifulSoup
import pymongo
import datetime
import time
import pandas as pd
import re
import warnings


def get_lines_from_song(html_doc):
    '''
    From raw html for one song, finds & returns portion that is actual body of song and splits into lines
    '''
    if 'html' in html_doc:
        html = html_doc['html']
    elif 'song_html' in html_doc:
        html = html_doc['song_html']
    else:
        raise KeyError (f"Html not found for {html_doc.get('_id')}")
    soup = BeautifulSoup(html, 'html.parser')
    song_body = soup.select_one('pre._1YgOS')
    song_lines = str(song_body).split('\n')
    return song_lines


def strip_html(text):
    '''
    Removes < and > from the html lines
    '''
    result = []
    in_tag = False
    for char in text:
        if char == '<':
            in_tag = True
        if not in_tag:
            result.append(char)
        if char == '>':
            in_tag = False
    return ''.join(result)


def separate_lines(html_doc):
    '''
    Separates chords and words; returns list of dictionaries for the song; each dictionary has 'chords' and 'words' as keys.
    '''
    song_lines = get_lines_from_song(html_doc)
    lines = []
    for i, song_line in enumerate(song_lines):
        if '_3L0Da' in song_line:
            lines.append({'chords': strip_html(song_line)})
        elif (('_3L0Da' in song_lines[i-1]) and (song_line == song_line) and (strip_html(song_line) == song_line)):
            lines[-1]['words'] = song_line
    return lines


def get_chords(line):
    '''
    For single line of song, returns:
        chord_idxs: list of character index at which each chord appears
        chords: lists of chords
        chord_tups: list of tuples matching above two results
    '''
    chord_idxs = []
    chords = []
    c_string = line['chords']
    for chord in re.finditer('\w+', c_string):
        chord_idxs.append(chord.start())
        chords.append(chord.group())
    chord_tups = list(zip(chord_idxs, chords))
    return chord_idxs, chords, chord_tups


def get_words(line):
    '''
    For single line of song, returns:
        word_idxs: list of character index at which each word appears (index of the first character of the word)
        words: lists of words in line
        word_tups: list of tuples matching above two results
    '''
    word_idxs = []
    words = []
    if 'words'in line:
        w_string = line['words']
        for word in re.finditer(r"\w[\w']*", w_string):
            word_idxs.append(word.start())
            words.append(word.group())
    word_tups = list(zip(word_idxs, words))
    return word_idxs, words, word_tups


def merge_chord_word(line):
    '''
    For given line of song, returns tuple of two lists:
    - chord_idx_list: chords and the index of word it is closest to (matching the index of the word in the word_list)
    - word_list
    '''
    chord_tups = get_chords(line)[2]
    word_tups = get_words(line)[2]
    word_list = get_words(line)[1]
    chord_idx_list = []
    for chord_tup in chord_tups:
        for i, word_tup in enumerate(word_tups):
            if word_tup[0] > chord_tup[0]:
                chord_idx_list.append((i-1, chord_tup[1]))
                break
    return (chord_idx_list, word_list)


def combine_ch_wd_lists(merged_line_1, merged_line_2):
    '''
    stacks two chord-idx and word lists on top of each other with appropriate indices
    '''
    chord_idx_list_1, word_list_1 = merged_line_1
    chord_idx_list_2, word_list_2 = merged_line_2
    new_chord_tups = []
    for chord_idx_tup in chord_idx_list_2:
        new_chord_tups.append( ( ( (chord_idx_tup)[0] + len(word_list_1) ), chord_idx_tup[1] ) )
    all_chords_tups = chord_idx_list_1 + new_chord_tups
    all_words_list = word_list_1 + word_list_2
    return all_chords_tups, all_words_list


def parse_lines(lines):
    '''
    Makes chord_idx_list and word_list for entire song
    '''
    if len(lines) == 0:
        raise ValueError("Bad song.")
    for i, line in enumerate(lines):
        if i == 0:
            parsed_line = merge_chord_word(line)
        else:
            parsed_line_next = merge_chord_word(line)
            parsed_line = combine_ch_wd_lists(parsed_line, parsed_line_next)
    return parsed_line


def parse_song(html_doc):
    '''
    parses song into chord-idx and word lists from html_doc
    '''
    lines = separate_lines(html_doc)
    parsed_song = parse_lines(lines)
    return parsed_song


def parse_many(html_docs):
    '''
    Parses list of songs into chord-idx and word lists from html_docs
    Returns list of parsed songs 
    '''
    parsed_songs = []
    for html_doc in html_docs:
        print ('.', end='')
        try:
            parsed_song = parse_song(html_doc)
            parsed_songs.append(parsed_song)
        except KeyError as e:
            warnings.warn(e.message)
            continue
        except ValueError as e:
            warnings.warn(str(e))
            continue
    return parsed_songs


if __name__ == "__main__":

    mc = pymongo.MongoClient()
    db = mc['chordify']
    raw_html = db['raw_html']
    html_docs = list(raw_html.find())

    parsed_songs = parse_many(html_docs[:7000])

    parsed_songs_db = db["parsed_songs"]

    for song in parsed_songs:
        song_dict = {
            "chord_idxs": song[0],
            "words": song[1]
        }
        parsed_songs_db.update(song_dict, song_dict, upsert=True)
