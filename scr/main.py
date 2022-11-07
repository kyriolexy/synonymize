from wordfreq import zipf_frequency as freq
import nltk
from api import get_related, _get_related
from random import choice
from nltk.tag import pos_tag, map_tag
from tabulate import tabulate
from pattern.text.en import sentiment
import inflect
from bisect import insort

# todo: change input method into a selective interface using inquirer or otherwise

text = input()
sentences = text.split(". ")

def add_str_r(__one, __two, __buffer=3):
    __one_split = __one.splitlines(); __two_split = __two.splitlines(keepends=True)
    __ldelta = len(__two_split)-len(__one_split)
    print(__ldelta)
    return "".join(__one_split[0]+" "*44+__two_split[0]) + \
           "".join([i[0]+" "*(abs(len(i[0])+__buffer-73-17))+i[1] for i in list(zip(__one_split, __two_split))[1:]]) + \
           "".join([" "*(abs(len(i[0].__str__())+__buffer-77-14))+i for i in __two_split[-__ldelta:]])

def _add_str_r(__one, __two):
    return '\n'.join([x+"   "+y for x, y in zip(__one.split('\n'), __two.split('\n'))])

def _add_str_r_(__one, __two):
    greater = __one if len(__one.splitlines())>len(__two.splitlines()) else __two; lesser = __one if greater != __one else __two
    greater = greater.splitlines(); lesser = lesser.splitlines()
    final = greater[0]+" "*(max(len(greater[1]), len(lesser[1]))-40)+lesser[0]+"\n"
    final += "\n".join([x+"   "+y for x, y in list(zip(greater, lesser))[1:len(lesser)]])+"\n"
    final += "\n".join(i for i in greater[len(lesser):])
    return final

def nth_repl(__text, __old, __new, __n):
    a = __text.find(__old)
    i = a != -1
    while a != -1 and i != __n: a = __text.find(__old, a + 1); i += 1
    if i == __n: return __text[:a] + __new + __text[a + len(__old):]

p = inflect.engine()
for sentence in sentences:
    _sentence = sentence
    tags = [
        (word, map_tag("en-ptb", "universal", tag))
        for word, tag in pos_tag(nltk.word_tokenize(sentence))
    ]
    print(tags)
    c = 0
    def add(w): global c; c += 1; return w[0], c
    psyns = [add(i) for i in tags if i[1] in ("VERB", "ADJ", "NOUN")]
    print(psyns)

    def gen_str():
        global psyns, _sentence
        _text = _sentence

        dsyn = {}
        SUBSCRIPT = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
        for syn in psyns:
            if syn[0] in dsyn.keys(): dsyn[syn[0]] += 1
            else: dsyn[syn[0]] = 0
            _text = nth_repl(_text,
                             syn[0],
                             f"\033[96m{syn[0]}\033[00m\033[95m{str(syn[1]).translate(SUBSCRIPT)}\033[00m",
                             dsyn[syn[0]]+1)

        return _text

    while True:
        print(gen_str())
        ind = input()
        if ind.isdigit():
            ind = int(ind)
        elif ind == "cont":
            break
        rows = []
        """for syn in get_related(psyns[ind-1][0]):
            # word | type (ADJ...) | freq
            rows.append([f"\033[96m{syn}\033[00m", f"\033[92m{tags[ind][1]}\033[00m", f"\033[95m{freq(syn[0], 'en')}\033[00m"])

        print(f"\033[96m{psyns[ind-1][0]}\033[00m \033[92m{tags[ind][1]}\033[00m")
        print(tabulate(rows, headers=["\033[96mword\033[00m", "\033[92mtype\033[00m", "\033[95mfreq\033[00m"]))"""

        _word = psyns[ind-1][0]; word = p.singular_noun(_word)
        _syns = set(get_related(_word))
        flag = False
        if word:
            flag = True
            syns = set(get_related(word))
            for syn in syns:
                # word | type (ADJ...) | freq
                s = nth_repl(text, word, syn, 1)
                se = sentiment(s)
                rows.append([f"\033[96m{syn}\033[00m", f"\033[92m{pos_tag(nltk.word_tokenize(syn), tagset='universal')[0][1]}\033[00m",
                             f"\033[95m{round(freq(syn[0], 'en')*12.5, 1)}/100\033[00m", se[0], se[1]])

            str_one = f"1. parent word: \033[96m{word}\033[00m \033[92m{tags[ind][1]}\033[00m (SINGULARIZED)\n"
            print(str_one.__repr__(), print(str_one), sep="\n\n")
            str_one += tabulate(rows, headers=["\033[96mword\033[00m", "\033[92mtype\033[00m", "\033[95mfreq\033[00m", "sentiment", "subjectivity"],
                                      showindex=True, tablefmt="outline")
        rows = []
        for syn in _syns:
            # word | type (ADJ...) | freq
            s = nth_repl(text, _word, syn, 1)
            se = sentiment(s)
            _freq = round(freq(syn[0], 'en')*12.5, 1)
            rows.append([f"\033[96m{syn}\033[00m", f"\033[92m{pos_tag(nltk.word_tokenize(syn), tagset='universal')[0][1]}\033[00m",
                         f"\033[95m{_freq}/100\033[00m", se[0], se[1]])

        rows.sort(reverse=True, key=lambda x: float(x[2][5:8]))
        if flag:
            str_two = f"2. parent word: \033[96m{_word}\033[00m \033[92m{tags[ind][1]}\033[00m\n"
            str_two += tabulate(rows, headers=["\033[96mword\033[00m", "\033[92mtype\033[00m", "\033[95mfreq\033[00m", "sentiment", "subjectivity"],
                                      showindex=True, tablefmt="outline")
        else:
            print(f"parent word: \033[96m{_word}\033[00m \033[92m{tags[ind][1]}\033[00m")
            print(tabulate(rows, headers=["\033[96mword\033[00m", "\033[92mtype\033[00m", "\033[95mfreq\033[00m", "sentiment", "subjectivity"],
                                 showindex=True, tablefmt="outline"))
        print()