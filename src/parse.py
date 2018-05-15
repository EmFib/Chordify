# from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import pymongo
import datetime
import time
import pandas as pd
import re
import warnings


def get_lines_from_song(html_doc):
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
    song_lines = get_lines_from_song(html_doc)
    lines = []
    for i, song_line in enumerate(song_lines):
        if '_3L0Da' in song_line:
            lines.append({'chords': strip_html(song_line)})
        elif (('_3L0Da' in song_lines[i-1]) and (song_line == song_line) and (strip_html(song_line) == song_line)):
            lines[-1]['words'] = song_line
    return lines


def get_chords(line):
    chord_idxs = []
    chords = []
    c_string = line['chords']
    for chord in re.finditer('\w+', c_string):
        chord_idxs.append(chord.start())
        chords.append(chord.group())
    chord_tups = list(zip(chord_idxs, chords))
    return chord_idxs, chords, chord_tups


def get_words(line):
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
    chord_idx_list_1, word_list_1 = merged_line_1
    chord_idx_list_2, word_list_2 = merged_line_2
    new_chord_tups = []
    for chord_idx_tup in chord_idx_list_2:
        new_chord_tups.append( ( ( (chord_idx_tup)[0] + len(word_list_1) ), chord_idx_tup[1] ) )
    all_chords_tups = chord_idx_list_1 + new_chord_tups
    all_words_list = word_list_1 + word_list_2
    return all_chords_tups, all_words_list


def parse_lines(lines):
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
    lines = separate_lines(html_doc)
    parsed_song = parse_lines(lines)
    return parsed_song


def parse_many(html_docs):
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

    parse_many(html_docs[:12])
