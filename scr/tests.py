def add_str_r(__one, __two, __buffer=3):
    __one_split = __one.splitlines(); __two_split = __two.splitlines(keepends=True)
    __ldelta = len(__two_split)-len(__one_split)
    print(__ldelta)
    return "".join(__one_split[0]+" "*44+__two_split[0]) + \
           "".join([i[0]+" "*(abs(len(i[0])+__buffer-73-17))+i[1] for i in list(zip(__one_split, __two_split))[1:]]) + \
           "".join([" "*(abs(len(i[0].__str__())+__buffer-77-14))+i for i in __two_split[-__ldelta:]])



from wordfreq import zipf_frequency as freq
import nltk
from api import get_related, _get_related
from random import choice
from nltk.tag import pos_tag, map_tag
from tabulate import tabulate
from pattern.text.en import sentiment
import inflect
from bisect import insort
def add_str_r(__one, __two, __buffer=3):
    __one_split = __one.splitlines(); __two_split = __two.splitlines(keepends=True)
    __ldelta = len(__two_split)-len(__one_split)
    print(__ldelta)
    return "".join(__one_split[0]+" "*44+__two_split[0]) + \
           "".join([i[0]+" "*(abs(len(i[0])+__buffer-73-17))+i[1] for i in list(zip(__one_split, __two_split))[1:]]) + \
           "".join([" "*(abs(len(i[0].__str__())+__buffer-77-14))+i for i in __two_split[-__ldelta:]])

def nth_repl(__text, __old, __new, __n):
    a = __text.find(__old)
    i = a != -1
    while a != -1 and i != __n: a = __text.find(__old, a + 1); i += 1
    if i == __n: return __text[:a] + __new + __text[a + len(__old):]
p=inflect.engine()
text = input()
tags = [
        (word, map_tag("en-ptb", "universal", tag))
        for word, tag in pos_tag(nltk.word_tokenize(text))
    ]
rows = []
ind = 1
_word = input(); word = p.singular_noun(_word)
_syns = set(_get_related(_word))
syns = set(_get_related(word))
for syn in syns:
    # word | type (ADJ...) | freq
    s = nth_repl(text, word, syn, 1)
    se = sentiment(s)
    rows.append([f"\033[96m{syn}\033[00m", f"\033[92m{pos_tag(nltk.word_tokenize(syn), tagset='universal')[0][1]}\033[00m",
                 f"\033[95m{round(freq(syn[0], 'en')*12.5, 1)}/100\033[00m", se[0], se[1]])

str_one = f"1. parent word: \033[96m{word}\033[00m \033[92m{tags[ind][1]}\033[00m (SINGULARIZED)\n"
str_one += tabulate(rows, headers=["\033[96mword\033[00m", "\033[92mtype\033[00m", "\033[95mfreq\033[00m", "sentiment", "subjectivity"],
                          showindex=True, tablefmt="outline")

rows = []
for syn in _syns:
    # word | type (ADJ...) | freq
    s = nth_repl(text, _word, syn, 1)
    se = sentiment(s)
    _freq = round(freq(syn[0], 'en') * 12.5, 1)
    rows.append(
        [f"\033[96m{syn}\033[00m", f"\033[92m{pos_tag(nltk.word_tokenize(syn), tagset='universal')[0][1]}\033[00m",
         f"\033[95m{_freq}/100\033[00m", se[0], se[1]])

rows.sort(reverse=True, key=lambda x: float(x[2][5:9]))
str_two = f"2. parent word: \033[96m{_word}\033[00m \033[92m{tags[ind][1]}\033[00m\n"
str_two += tabulate(rows, headers=["\033[96mword\033[00m", "\033[92mtype\033[00m", "\033[95mfreq\033[00m", "sentiment", "subjectivity"],
                          showindex=True, tablefmt="outline")
print(add_str_r(str_one, str_two))

a = """1. parent word: \x1b[96mextreme\x1b[00m \x1b[92mNOUN\x1b[00m (SINGULARIZED)\n+----+--------------+--------+----------+-------------+----------------+\n|    | \x1b[96mword\x1b[00m         | \x1b[92mtype\x1b[00m   | \x1b[95mfreq\x1b[00m     |   sentiment |   subjectivity |\n+====+==============+========+==========+=============+================+\n|  0 | \x1b[96mhighest\x1b[00m      | \x1b[92mADJ\x1b[00m    | \x1b[95m63.2/100\x1b[00m |         0   |            0   |\n|  1 | \x1b[96moutermost\x1b[00m    | \x1b[92mNOUN\x1b[00m   | \x1b[95m64.0/100\x1b[00m |         0   |            0   |\n|  2 | \x1b[96mmost distant\x1b[00m | \x1b[92mADV\x1b[00m    | \x1b[95m67.4/100\x1b[00m |         0.5 |            0.5 |\n|  3 | \x1b[96mgreatest\x1b[00m     | \x1b[92mADJ\x1b[00m    | \x1b[95m62.5/100\x1b[00m |         0   |            0   |\n|  4 | \x1b[96mremotest\x1b[00m     | \x1b[92mNOUN\x1b[00m   | \x1b[95m66.9/100\x1b[00m |         0   |            0   |\n|  5 | \x1b[96mdrastic\x1b[00m      | \x1b[92mADJ\x1b[00m    | \x1b[95m68.2/100\x1b[00m |         0   |            0   |\n|  6 | \x1b[96mdangerous\x1b[00m    | \x1b[92mADJ\x1b[00m    | \x1b[95m68.2/100\x1b[00m |         0   |            0   |\n|  7 | \x1b[96mfinal\x1b[00m        | \x1b[92mADJ\x1b[00m    | \x1b[95m63.5/100\x1b[00m |         0   |            0   |\n|  8 | \x1b[96mlast\x1b[00m         | \x1b[92mADJ\x1b[00m    | \x1b[95m64.8/100\x1b[00m |         0   |            0   |\n|  9 | \x1b[96mexcessive\x1b[00m    | \x1b[92mADJ\x1b[00m    | \x1b[95m66.0/100\x1b[00m |         0   |            0   |\n| 10 | \x1b[96mfurthest\x1b[00m     | \x1b[92mNOUN\x1b[00m   | \x1b[95m63.5/100\x1b[00m |         0   |            0   |\n| 11 | \x1b[96mfarthest\x1b[00m     | \x1b[92mNOUN\x1b[00m   | \x1b[95m63.5/100\x1b[00m |         0   |            0   |\n| 12 | \x1b[96msevere\x1b[00m       | \x1b[92mADJ\x1b[00m    | \x1b[95m73.2/100\x1b[00m |         0   |            0   |\n| 13 | \x1b[96multimate\x1b[00m     | \x1b[92mADJ\x1b[00m    | \x1b[95m63.9/100\x1b[00m |         0   |            0   |\n| 14 | \x1b[96mtoo much\x1b[00m     | \x1b[92mADV\x1b[00m    | \x1b[95m67.9/100\x1b[00m |         0   |            0   |\n+----+--------------+--------+----------+-------------+----------------+'"""

b = """2. parent word: \x1b[96mextremes\x1b[00m \x1b[92mNOUN\x1b[00m\n+----+--------------+--------+----------+-------------+----------------+\n|    | \x1b[96mword\x1b[00m         | \x1b[92mtype\x1b[00m   | \x1b[95mfreq\x1b[00m     |   sentiment |   subjectivity |\n+====+==============+========+==========+=============+================+\n|  0 | \x1b[96msevere\x1b[00m       | \x1b[92mADJ\x1b[00m    | \x1b[95m73.2/100\x1b[00m |       0     |            0   |\n|  1 | \x1b[96mdrastic\x1b[00m      | \x1b[92mADJ\x1b[00m    | \x1b[95m68.2/100\x1b[00m |       0     |            0   |\n|  2 | \x1b[96mdangerous\x1b[00m    | \x1b[92mADJ\x1b[00m    | \x1b[95m68.2/100\x1b[00m |       0     |            0   |\n|  3 | \x1b[96mtoo much\x1b[00m     | \x1b[92mADV\x1b[00m    | \x1b[95m67.9/100\x1b[00m |       0     |            0   |\n|  4 | \x1b[96mmost distant\x1b[00m | \x1b[92mADV\x1b[00m    | \x1b[95m67.4/100\x1b[00m |       0.5   |            0.5 |\n|  5 | \x1b[96mremotest\x1b[00m     | \x1b[92mNOUN\x1b[00m   | \x1b[95m66.9/100\x1b[00m |       0     |            0   |\n|  6 | \x1b[96mexcessive\x1b[00m    | \x1b[92mADJ\x1b[00m    | \x1b[95m66.0/100\x1b[00m |       0     |            0   |\n|  7 | \x1b[96mextreme\x1b[00m      | \x1b[92mNOUN\x1b[00m   | \x1b[95m66.0/100\x1b[00m |      -0.125 |            1   |\n|  8 | \x1b[96mlast\x1b[00m         | \x1b[92mADJ\x1b[00m    | \x1b[95m64.8/100\x1b[00m |       0     |            0   |\n|  9 | \x1b[96moutermost\x1b[00m    | \x1b[92mNOUN\x1b[00m   | \x1b[95m64.0/100\x1b[00m |       0     |            0   |\n| 10 | \x1b[96multimate\x1b[00m     | \x1b[92mADJ\x1b[00m    | \x1b[95m63.9/100\x1b[00m |       0     |            0   |\n| 11 | \x1b[96mfinal\x1b[00m        | \x1b[92mADJ\x1b[00m    | \x1b[95m63.5/100\x1b[00m |       0     |            0   |\n| 12 | \x1b[96mfurthest\x1b[00m     | \x1b[92mNOUN\x1b[00m   | \x1b[95m63.5/100\x1b[00m |       0     |            0   |\n| 13 | \x1b[96mfarthest\x1b[00m     | \x1b[92mNOUN\x1b[00m   | \x1b[95m63.5/100\x1b[00m |       0     |            0   |\n| 14 | \x1b[96mhighest\x1b[00m      | \x1b[92mADJ\x1b[00m    | \x1b[95m63.2/100\x1b[00m |       0     |            0   |\n| 15 | \x1b[96mgreatest\x1b[00m     | \x1b[92mADJ\x1b[00m    | \x1b[95m62.5/100\x1b[00m |       0     |            0   |\n+----+--------------+--------+----------+-------------+----------------+"""

print(add_str_r(a, b, 3))