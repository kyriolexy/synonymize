from wiktionaryparser import WiktionaryParser
import httpx
from nltk.corpus import wordnet as wn
from bs4 import BeautifulSoup

parser = WiktionaryParser()


def get_syn(word: str):
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
        parsed = parser.fetch(word)[0]["definitions"][0]["relatedWords"][0]["words"]
        if (
            parser.fetch(word)[0]["definitions"][0]["relatedWords"][0][
                "relationshipType"
            ]
            == "antonyms"
        ):
            raise IndexError
    except IndexError:
        flag = True
        parsed, exists, adj = get_syn(word)
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
        final.append(j(word))
    except Exception:
        pass
    try:
        parsed = parser.fetch(word)[0]["definitions"][0]["relatedWords"][0]["words"]
        if (
            parser.fetch(word)[0]["definitions"][0]["relatedWords"][0][
                "relationshipType"
            ]
            == "antonyms"
        ):
            raise IndexError
        final.append(parsed)
    except IndexError:
        pass

    parsed, exists, adj = get_syn(word)
    if len(parsed) == 0:
        if len((a := j(word))) != 0:
            final.append(a)
        try:
            b = wn.synsets(word)
        except AttributeError:
            b = []
        if len(b) != 0:
            final.append([str(lemma.name()) for lemma in b[0].lemmas()])
    final.append(parsed)

    if not flag:
        for i in parsed:
            i: str
            if i.__contains__("Thesaurus:"):
                adj_word = i[i.index("Thesaurus:") + 10 :]
                final.append(j(adj_word))
                final.append(adj_word)
    else:
        if exists:
            final.append(j(adj))
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
                    final.append(parsed)
                [_parsed.append(i) for i in udef]
                final.append(_parsed)

        if _flag:
            final.append(_parsed)

    """final =  [_i for _l in final for _i in _l]
    if not __a:
        for i in final:
            final.append(get_related(i, True))"""

    return [_i for _l in final for _i in _l]