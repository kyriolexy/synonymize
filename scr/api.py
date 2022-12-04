import string

from wiktionaryparser import WiktionaryParser
import httpx
from nltk.corpus import wordnet as wn
from bs4 import BeautifulSoup
import re
import json
from typing import List
import pprint
import string

_parser = WiktionaryParser()
_PATTERN_PATTERN = re.compile(r"(\([\w\s:]+\): )(.+)")

def pprint_def(word: str) -> str:
    _def = get_def(word)
    final = ""
    temp = '\n'.join([f'{i+1}. {j}' for i, j in enumerate(_def[0]["def"])])
    final += f"Definitions\n+--- {temp}\n"
    final += f"Etymology\n+--- {_def[0]['ety']}\n"
    if len(_def) == 2:
        key, val = list(_def[1].items())
        print(key, val, sep = "\n||||\n")
        final += f"\nSingularized ({key[0]})\n"
        temp = '\n+--- '.join([f'{i + 1}. {j}' for i, j in enumerate(key[1]["def"])])
        final += f"Definitions\n+--- {temp}\n"
        final += f"Etymology\n+--- {val[1]}"

    return final

def get_def(word: str) -> List[str]:
    parsed = _parser.fetch(word)
    if parsed[0]["definitions"] == []:
        return ""
    _parsed: list = [
        {
            "def": parsed[0]["definitions"][0]["text"][1:],
            "ety": (ety if (ety := parsed[0]["etymology"]) != "" else "Unknown"),
        }
    ]
    print(_parsed)
    if (ind := (_def := _parsed[0]["def"][0]).find("plural of")) != -1:
        non_plural = _def[ind + 10 :]
        if _def[-1] in string.punctuation:
            non_plural = non_plural[:-1]
        print(ind, non_plural)
        _parsed.append(
            {
                non_plural: {
                    "def": (non_plural_parsed := _parser.fetch(non_plural))[0][
                        "definitions"
                    ][0]["text"][1:]
                },
                "ety": ety
                if (ety := non_plural_parsed[0]["etymology"]) != ""
                else "Unknown",
            }
        )

    return _parsed


def _get_syn(word: str) -> List[str]:
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


def get_uses(word, type):
    # thanks rhymezone for not having a complete api
    raise NotImplementedError
    # All
    # ---- Books <font size=2> href +
    # ----       <font size=1>
    # ---- Poetry&Shakespeare
    # -------- Poetry <font size=2> href includes "by {author}"
    # -------- Shakespeare else
    soup = BeautifulSoup(
        httpx.get(
            f"https://www.rhymezone.com/r/rhyme.cgi?Word={word}&typeofrhyme=wke&org1=syl&org2=l&org3=y"
        ),
        "html.parser",
    )
    print(soup.prettify())
    uses = ""
    for i in uses:
        print(i)

    if type == "All":
        pass
    elif type == "Books":
        pass
    elif type == "Poetry":
        pass
    else:
        pass


def j(adj_word: str) -> List[str]:
    a = httpx.get(f"https://en.wiktionary.org/wiki/Thesaurus:{adj_word}").content
    soup = BeautifulSoup(a, "html.parser")
    if len(soup.find_all("div", {"class": "noarticletext mw-content-ltr"})) != 0:
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
            if len(b) != 0:
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


def get_rhym(word: str, type: str) -> List[str]:
    parsed = json.loads(
        BeautifulSoup(
            httpx.get(
                f"https://api.datamuse.com/words?{type}={'+'.join(word.split(' '))}"
            ),
            "html.parser",
        ).text
    )
    for i in parsed:
        yield i["word"]


def get_related(word: str) -> List[str]:
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
                final.append(get_rhym(adj_word, "ml"))
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

    final.append(list(get_rhym(word, "ml")))
    final = [_i for _l in final for _i in _l]
    for i in final:
        if i[0] == "(":
            final.remove(i)
            [final.append(q) for q in re.findall(_PATTERN_PATTERN, i)[0][1].split(", ")]

    return list(set(final))


if __name__ == "__main__":
    print(pprint_def(input()))
