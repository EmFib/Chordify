from __future__ import division
from math import sqrt
from flask import Flask, render_template, request, jsonify

from ..src.LogisticChordAnalyzer import fit_lca, save_lca, load_lca, LogisticChordAnalyzer

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
    user_data = request.json
    entry = user_data['words']
    lines = _submit_words(entry)
    _chord_preds = _get_chords(lines)
    return jsonify({'chord_preds': _chord_preds})

def _submit_words():
    '''
    Gets words as user input and splits into lines by punctuation.
    '''
    while True:
        entry = user_data['words']
        if 3 <= len(entry.split()):
            lines = re.split('[?.,!-]', entry)
            return lines


def _get_chords():
    lca = load_lca()
    lines = _submit_words()
    for line in lines:
        if len(line) >= 2:
            best_line_chord = lca.predict(line)
            return ("{}:".format(line), best_line_chord)


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
