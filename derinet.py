import os, sys
from time import time
from collections import namedtuple, defaultdict

Lexeme = namedtuple('Lexeme', ['id', 'lemma', 'deriv', 'pos', 'parent', 'children'])

class DeriNet:
    def __init__(self):
        self.data = []
        self.index = defaultdict(list)
        self.origin = None

    def load(self, fname):
        """
        Load DeriNet tsv file.
        """
        if not os.path.exists(fname):
            print('DeriNet file "{}" not found'.format(fname), file=sys.stderr)
            candidates = [path for path in os.listdir()
                            if 'derinet' in path and path.enswith('.tsv')]
            if candidates != []:
                print('Did you mean:', file=sys.stderr)
                for path in candidates:
                    print(path, file=sys.stderr)
            sys.exit(1)

        print('Loading DeriNet file...')
        btime = time()

        with open(fname, 'r', encoding='utf-8') as ifile:
            for i, line in enumerate(ifile):
                lex_id, lemma, deriv, pos, parent = line.strip('\n').split('\t')
                self.data.append(Lexeme(lex_id, lemma, deriv, pos, int(parent) if parent !='' else '', []))
                self.index[lemma].append(int(lex_id))

        if len(self.data) != i + 1:
            print('Lexeme numeration in DeriNet file inconsistent:')
            print('Discovered {} lexemes total but the last was indexed {}'.format(len(self.data), i))

        for lemma, lex_id_list in self.index.items():
            lex_id_list.sort()

        for i, lexeme in enumerate(self.data):
            if lexeme.parent != '':
                self.data[lexeme.parent].children.append(lexeme)

        self.origin = fname

        print('Loaded in {:.2f} s.'.format(time() - btime))

    def save(self, fname):
        """
        Save tsv snapshot of current data.
        """
        with open(fname, 'w', encoding='utf-8') as ofile:
            for lexeme in self.data:
                print(*lexeme[:-1], sep='\t', file=ofile)

    def get_lexeme_by_id(self, lex_id):
        return self.data[lex_id]

    def get_parent_by_id(self, lex_id):
        parent = self.data[lex_id].parent
        if parent is None:
            return None
        return self.data[parent]

    def get_ids_by_lemma(self, lemma):
        return self.index[lemma]

    def get_children_by_id(self, lex_id):
        pass


if __name__ == "__main__":
    derinet = DeriNet()
    derinet.load('derinet-1-2.tsv')
