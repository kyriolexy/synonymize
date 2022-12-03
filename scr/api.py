from wiktionaryparser import WiktionaryParser
import httpx
from nltk.corpus import wordnet as wn
from bs4 import BeautifulSoup
import re

_parser = WiktionaryParser()
_PATTERN_PATTERN = re.compile(r"(\([\w\s:]+\): )(.+)")

def _get_syn(word: str):
    soup = BeautifulSoup(
        str(httpx.get(f"https://en.wiktionary.org/wiki/{word}").content), "html.parser"
    )
    syn = soup.find_all("span", {"class": "nyms synonym"})
    syns = []
    th_exist = False
    adj = None
    for i in syn:
        soup = BeautifulSoup(str(i), "html.parser")
        a = soup.find_all("a")
        for k in a:
            if k.get("title").__contains__("Thesaurus:"):
                th_exist = True
                m = k.get("title")
                adj = m[m.index("Thesaurus:") + 10 :]

        a = [l.string for l in a if not l.get("title").__contains__("Thesaurus:")]
        [syns.append(j) for j in a if not j.__contains__("\\")]

    return syns, th_exist, adj


def j(adj_word):
    a = httpx.get(f"https://en.wiktionary.org/wiki/Thesaurus:{adj_word}").content
    soup = BeautifulSoup(a, "html.parser")
    if len(soup.find_all("div", {"class": "noarticletext mw-content-ltr"}))!=0:
        return []
    try:
        b = str(soup.find_all("div", {"class": "ul-column-count"})[0])
    except:
        return []
    soup = BeautifulSoup(b, "html.parser")
    c = [
        i.string
        for i in soup.find_all("a")
        if not i.get("title").__contains__("Thesaurus:")
    ]
    return c

def _get_related(word: str, __a):
    flag = False
    try:
        parsed = _parser.fetch(word)[0]["definitions"][0]["relatedWords"][0]["words"]
        if (
            _parser.fetch(word)[0]["definitions"][0]["relatedWords"][0][
                "relationshipType"
            ]
            == "antonyms"
        ):
            raise IndexError
    except IndexError:
        flag = True
        parsed, exists, adj = _get_syn(word)
        if len(parsed) == 0:
            if len((a := j(word))) != 0:
                return a
            b = wn.synsets(word)
            if len(b)!=0:
                return [str(lemma.name()) for lemma in b[0].lemmas()]
            else:
                return []

    if not flag:
        for i in parsed:
            i: str
            if i.__contains__("Thesaurus:"):
                adj_word = i[i.index("Thesaurus:") + 10 :]
                return j(adj_word)
    else:
        if exists:
            return j(adj)

    if len(parsed) != 0:
        udef: str
        _parsed = []
        for udef in parsed:
            udef = udef.split(", ")
            try:
                udef[0] = udef[0][(udef[0].index(":") + 2) :]
            except ValueError:
                return parsed
            [_parsed.append(i) for i in udef]
    return _parsed

def get_related(word: str):
    flag = False
    final = []
    try:
        # print(f"adding1 {j(word)}")
        final.append(j(word))
    except Exception:
        pass
    try:
        parsed = _parser.fetch(word)[0]["definitions"][0]["relatedWords"][0]["words"]
        if (
            _parser.fetch(word)[0]["definitions"][0]["relatedWords"][0][
                "relationshipType"
            ]
            == "antonyms"
        ):
            raise IndexError
        # print(f"adding2 {parsed}")
        final.append(parsed)
    except IndexError:
        pass

    parsed, exists, adj = _get_syn(word)
    if len(parsed) == 0:
        if len((a := j(word))) != 0:
            # print(f"adding3 {a}")
            final.append(a)
        try:
            b = wn.synsets(word)
        except AttributeError:
            b = []
        if len(b) != 0:
            # print(f"adding4 {[str(lemma.name()) for lemma in b[0].lemmas()]}")
            final.append([str(lemma.name()) for lemma in b[0].lemmas()])
    # print(f"adding5 {parsed}")
    final.append(parsed)

    if not flag:
        for i in parsed:
            i: str
            if i.__contains__("Thesaurus:"):
                adj_word = i[i.index("Thesaurus:") + 10 :]
                # print(f"adding6 {j(adj_word)=}")
                final.append(j(adj_word))
                # print(f"adding7 {adj_word=}")
                final.append(adj_word)
    else:
        if exists:
            # print(f"adding8 {j(adj)=}")
            final.append(j(adj))
            # print(f"adding9 {adj=}")
            final.append(adj)

    _flag = False
    if not flag:
        if len(parsed) != 0:
            udef: str
            _parsed = []
            for udef in parsed:
                udef = udef.split(", ")
                try:
                    udef[0] = udef[0][(udef[0].index(":") + 2) :]
                except ValueError:
                    _flag = True
                    # print(f"adding10 {parsed}")
                    final.append(parsed)
                [_parsed.append(i) for i in udef]
                # print(f"adding11 {_parsed=}")
                final.append(_parsed)

        if _flag:
            # print(f"adding12 {_parsed}")
            final.append(_parsed)

    final = [_i for _l in final for _i in _l]
    for i in final:
        if i[0]=="(":
            final.remove(i)
            [final.append(q) for q in re.findall(_PATTERN_PATTERN, i)[0][1].split(", ")]

    return list(set(final))