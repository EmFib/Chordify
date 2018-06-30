from __future__ import division
from math import sqrt
from flask import Flask, render_template, request, jsonify

import re 

from ..LogisticChordAnalyzer import fit_lca, save_lca, load_lca, LogisticChordAnalyzer

# from /Users.emilynaftalin.Data_Science.Galvanize.dsi.Chordify.chordify.LogisticChordAnalyzer import fit_lca, save_lca, load_lca, LogisticChordAnalyzer

## to run: python -m chordify.app.app (out ouf Chordify directory)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('chordify.html')


# @app.route('/solve', methods=['POST'])
# def solve():
#
#     user_data = request.json

#     a, b, c = user_data['a'], user_data['b'], user_data['c']
#     root_1, root_2 = _solve_quadratic(a, b, c)
#     return jsonify({'root_1': root_1, 'root_2': root_2})
#
#
# def _solve_quadratic(a, b, c):
#     disc = b*b - 4*a*c
#     root_1 = (-b + sqrt(disc))/(2*a)
#     root_2 = (-b - sqrt(disc))/(2*a)
#     return root_1, root_2

@app.route('/solve', methods=['POST'])

def solve():
    print("solving...")
    user_data = request.json
    entry = user_data['words']
    lines = _submit_words(entry)
    _chord_preds = _get_chords(lines)
    root_1 = print_prediction(chord_preds)
    print(lines)
    # print(_chord_preds)
    return jsonify({'chord_preds': _chord_preds})

def _submit_words(entry):
    '''
    Gets words as user input and splits into lines by punctuation.
    '''
    while True:
        if 3 <= len(entry.split()):
            lines = re.split('[?.,!-]', entry)
            return lines


def _get_chords(lines):
    lca = load_lca()
    lines = _submit_words()
    for line in lines:
        if len(line) >= 2:
            best_line_chord = lca.predict(line)
            return ("{}:".format(line), best_line_chord)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
