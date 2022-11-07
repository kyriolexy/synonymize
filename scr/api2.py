import httpx
from bs4 import BeautifulSoup
def get_syn(word: str):
    soup = BeautifulSoup(str(httpx.get(f"https://en.wiktionary.org/wiki/{word}").content), "html.parser")
    syn = soup.find_all("span", {"class": "nyms synonym"})
    syns = []
    th_exist = False
    adj = None
    for i in syn:
        soup = BeautifulSoup(str(i), "html.parser")
        a = soup.find_all("a")
        for k in a:
            if k.get("title").__contains__("Thesaurus:"):
                th_exist=True
                m = k.get("title")
                adj = m[m.index("Thesaurus:") + 10:]

        a = [l.string for l in a if not l.get("title").__contains__("Thesaurus:")]
        [syns.append(j) for j in a if not j.__contains__("\\")]

    return syns, th_exist, adj

print(get_syn(input()))
