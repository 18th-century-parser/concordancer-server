from pathlib import Path

from pymystem3 import Mystem
import pymorphy3 as mf


class Concardancer:
    def __init__(self, all_forms=False, en=False):
        self.stem = Mystem(entire_input=en)
        self.word_m = {}
        self.all_forms = all_forms

    @staticmethod
    def read_from_file(path: Path):
        with open(path, encoding='utf-8') as file:
            lines = file.readlines()
        s = ""
        for line in lines:
            s += line
        s = s.replace('\n', ' ')
        return s

    @staticmethod
    def get_seqs(txt):
        seqs = txt.split('.')
        res = []
        for seq in seqs:
            if len(seq) > 0:
                res.append(seq)
        return res

    def get_all_forms(self, word):
        info = {}
        forms = []
        morph = mf.MorphAnalyzer()
        a = morph.parse(word)[0]
        for _ in a.lexeme:
            st = (str(_.word), str(_.tag).replace(' ', ',').split(','))
            forms.append(st)
        forms_ = []
        for form in forms:
            forms_.append(form[0])
        for form in forms_:
            if len(form) == 0:
                continue
            a = self.stem.analyze(form[0])
            if len(a) == 0:
                continue
            if len(a[0]) == 0 or len(a[0]['analysis']) == 0:
                continue
            analysis = a[0]['analysis'][0]['gr']
            tags = []
            tmp = ""
            flag = False
            for i in analysis:
                if i == '(':
                    tmp = ""
                    flag = True
                elif i == ')':
                    tmp = tmp.replace('|', ',')
                    a = tmp.split(',')
                    res = set()
                    if len(a) == 1:
                        tags.append(a[0])
                        continue
                    elif len(a) == 0:
                        continue
                    for j in a:
                        res.add(j)
                    for j in res:
                        tags.append(j)
                    flag = False
                    tmp = ""
                if i == ',' and not flag and i != ')':
                    tags.append(tmp)
                    tmp = ""
                elif i.isalpha() or i == ',' or i == '|':
                    tmp += i
            if len(tmp) > 0:
                tags.append(tmp)
            if info.get(form) is None:
                info[form] = {}
            if info[form].get('tags') is None:
                info[form]['tags'] = {}
            info[form] = {}
            info[form]['tags'] = tags
        return info

    def get_forms(self, filename: Path):
        txt = self.read_from_file(filename)
        all_forms = {}
        seqs = self.get_seqs(txt)
        seq_ind = 1
        for seq in seqs:
            words = seq.split(' ')
            a = self.stem.analyze(seq)
            ind = 0
            for word in words:
                if len(word) == 0:
                    continue
                if not word[0].isalpha():
                    word = word[1:]
                if ind >= len(a):
                    break
                if len(word) > 0 and not word[-1].isalpha():
                    word = word[:-1]
                if len(a[ind]) == 0 or a[ind] is None or type(a[ind]) == str:
                    continue
                try:
                    # noinspection PyTypeChecker
                    lemma = a[ind]['analysis'][0]['lex']
                    # noinspection PyTypeChecker
                    analysis = a[ind]['analysis'][0]['gr']
                except:
                    break
                tags = []
                tmp = ""
                flag = False
                for i in analysis:
                    if i == '(':
                        tmp = ""
                        flag = True
                    elif i == ')':
                        tmp = tmp.replace('|', ',')
                        tmp = tmp.replace('=', ',')
                        a = tmp.split(',')
                        res = set()
                        if len(a) == 1:
                            tags.append(a[0])
                            continue
                        elif len(a) == 0:
                            continue
                        for j in a:
                            res.add(j)
                        for j in res:
                            tags.append(j)
                        flag = False
                        tmp = ""
                    if i == '=':
                        tags.append(tmp)
                        tmp = ""
                        continue
                    if i == ',' and not flag and i != ')':
                        tags.append(tmp)
                        tmp = ""
                    elif i.isalpha() or i == ',' or i == '|':
                        tmp += i
                if len(tmp) > 0:
                    tags.append(tmp)
                if all_forms.get(lemma) is None:
                    all_forms[lemma] = {}
                    all_forms[lemma]['occurrences'] = 1
                    if self.all_forms:
                        all_forms[lemma]['other forms'] = self.get_all_forms(word)
                    else:
                        all_forms[lemma]['other forms'] = {}
                    all_forms[lemma][word] = {}
                    all_forms[lemma][word]['info'] = {}
                    all_forms[lemma][word]['info']['tags'] = []
                    all_forms[lemma][word]['info']['seq'] = []
                    all_forms[lemma][word]['info']['index'] = []
                    all_forms[lemma][word]['info']['tags'].append(tags)
                    all_forms[lemma][word]['info']['seq'].append(seq)
                    all_forms[lemma][word]['info']['index'].append(seq_ind)

                else:
                    if all_forms[lemma].get(word) is None:
                        all_forms[lemma][word] = {}
                        all_forms[lemma][word]['info'] = {}
                        all_forms[lemma][word]['info']['seq'] = []
                        all_forms[lemma][word]['info']['index'] = []
                        all_forms[lemma][word]['info']['tags'] = []
                    all_forms[lemma]['occurrences'] += 1
                    all_forms[lemma][word]['info']['tags'].append(tags)
                    all_forms[lemma][word]['info']['seq'].append(seq)
                    all_forms[lemma][word]['info']['index'].append(seq_ind)
                ind += 1
            seq_ind += 1
        return all_forms


concardancer = Concardancer()
