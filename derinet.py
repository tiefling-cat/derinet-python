#! /usr/bin/python3

import os
import sys
from time import time
from collections import namedtuple

Lexeme = namedtuple('Lexeme', ['lex_id', 'lemma', 'morph', 'pos', 'parent_id', 'children'])


class DeriNet(object):

    __slots__ = ['data', 'index', 'fname']

    def __init__(self):
        self.data = []
        self.index = {}
        self.fname = None

    def _read_nodes_from_file(self, fname):
        data, index = [], {}
        with open(fname, 'r', encoding='utf-8') as ifile:
            for i, line in enumerate(ifile):
                lex_id, lemma, morph, pos, parent_id = line.strip('\n').split('\t')
                data.append(Lexeme(int(lex_id), lemma, morph, pos, '' if parent_id == '' else int(parent_id), []))
                index.setdefault(lemma, {})
                index[lemma][morph] = int(lex_id)
        return data, index

    def _populate_children(self):
        """Populate children for all nodes."""
        for node in self.data:
            if node.parent_id != '':
                self.data[node.parent_id].children.append(node)

    def load(self, fname):
        """Load DeriNet tsv file."""
        if not os.path.exists(fname):
            raise Exception('file "{}" not found'.format(fname))

        print('Loading DeriNet from "{}" file...'.format(fname), file=sys.stderr)
        btime = time()

        self.data, self.index = self._read_nodes_from_file(fname)

        if len(self.data) - 1 != self.data[-1].lex_id:
            print('Warning: Lexeme numeration in DeriNet file inconsistent:', file=sys.stderr)
            print('Discovered {} lexemes total but the last was indexed {}'.format(len(self.data), i), file=sys.stderr)

        self._populate_children()

        print('Loaded in {:.2f} s.'.format(time() - btime), file=sys.stderr)
        self.fname = fname
        return fname

    def lex_sort(self):
        """Sort nodes regarding lemmas and morphological info."""
        print('Sorting DeriNet...', file=sys.stderr)
        btime = time()
        # sort
        self.data.sort(key=lambda x: (x.lemma.lower(), x.morph))

        # reindex
        reverse_id_index = [0] * len(self.data) # used for parent_ids only
        for i, node in enumerate(self.data):
            reverse_id_index[node[0]] = i
        for i, node in enumerate(self.data):
            self.data[i] = node._replace(lex_id=i, parent_id='' if node.parent_id == '' else reverse_id_index[node.parent_id], children=[])

        self._populate_children()

        print('Sorted in {:.2f} s.'.format(time() - btime), file=sys.stderr)

    def save(self, fname=None):
        """Save tsv snapshot of current data."""
        if fname is None:
            fname = self.fname
        print('Saving snapshot to "{}"'.format(fname), file=sys.stderr)
        btime = time()
        with open(fname, 'w', encoding='utf-8') as ofile:
            for lexeme in self.data:
                print(*lexeme[:-1], sep='\t', file=ofile)
        print('Saved in {:.2f} s.'.format(time() - btime), file=sys.stderr)

    def update_from_file(self, fname):
        pass

    def update(self, new_data):
        for new_node in new_data:
            lex_id = self.get_id_by_lemma(new_node.lemma, new_node.morph)
            if lex_id is None:
                # no such lexeme exists
                self.data.append(new_node)
                if new_node.parent_id != '':
                    try:
                        self.data[new_node.parent_id] = self.data[-1]
                    except IndexError:
                        raise Exception("invalid parent id for new node {}: parent doesn't exist".format(new_node))
                self.index.setdefault(new_node.lemma, {})
                self.index[new_node.lemma][new_node.morph] = len(self.data)
            else:
                # there is such lexeme already
                

    def get_lexeme_by_id(self, lex_id):
        return self.data[lex_id]

    def get_parent_by_id(self, lex_id):
        parent_id = self.data[lex_id].parent_id
        if parent_id == '':
            return None
        return self.data[parent_id]

    def get_id_by_lemma(self, lemma, morph=None):
        if lemma not in self.index:
            # no such lemma in the net
            return None
        lemma_index = self.index.get(lemma, None)
        if len(lemma_index) == 1:
            # there's only one such lemma in the net
            return list(lemma_index.values())[0]
        # there's more than one such lemma in the net
        if morph is not None and morph in lemma_index:
            # morphological info specified is in the net
            return lemma_index[morph]
        # ambiguous lemma
        return None

    def get_children_by_id(self, lex_id):
        return self.data[lex_id].children

    def get_subtree_by_id(self, lex_id):
        lexeme = self.data[lex_id]
        return [lexeme, [self.get_subtree_by_id(child.id) for child in lexeme.children]]

    def print_subtree_by_id(self, lex_id, form1='', form2='  ', form3=''):
        lexeme = self.data[lex_id]
        print(form1 + form3, end='')
        print(*lexeme[:-1], sep='\t')
        if lexeme.children != []:
            for child in lexeme.children[:-1]:
                self.print_subtree_by_id(child.id, form1=form1+form2, form2='│ ', form3='└─')
            self.print_subtree_by_id(lexeme.children[-1].id, form1+form2, form2='  ', form3='└─')

if __name__ == "__main__":
    derinet = DeriNet()
    derinet.load('derinet-1-2.tsv')
    derinet.lex_sort()
    derinet.save('derinet-1-2-sorted.tsv')
