import numpy as np
from treeCl.alignment import Alignment
from treeCl.tree import Tree
from treeCl.utils.decorators import lazyprop
from treeCl.utils import flatten_list

__author__ = 'kgori'


class Concatenation(object):
    """docstring for Concatenation"""

    def __init__(self, collection, indices):
        super(Concatenation, self).__init__()
        if any((x > len(collection)) for x in indices):
            raise ValueError('Index out of bounds in {}'.format(indices))
        if any((x < 0) for x in indices) < 0:
            raise ValueError('Index out of bounds in {}'.format(indices))
        if any((not isinstance(x, int)) for x in indices):
            raise ValueError('Integers only in indices, please: {}'
                             .format(indices))
        self.collection = collection
        self.indices = sorted(indices)

    def __len__(self):
        return len(self.indices)

    @lazyprop
    def distances(self):
        return [self.collection.distances[i] for i in self.indices]

    @lazyprop
    def variances(self):
        return [self.collection.variances[i] for i in self.indices]

    @lazyprop
    def frequencies(self):
        return [self.collection.frequencies[i] for i in self.indices]

    @lazyprop
    def alphas(self):
        return [self.collection.alphas[i] for i in self.indices]

    @lazyprop
    def datatypes(self):
        return [self.collection.datatypes[i] for i in self.indices]

    @lazyprop
    def alignment(self):
        al = Alignment([self.collection[i] for i in self.indices])
        return al

    @lazyprop
    def names(self):
        return [self.collection.names[i] for i in self.indices]

    @lazyprop
    def lengths(self):
        return [self.collection.lengths[i] for i in self.indices]

    @lazyprop
    def headers(self):
        return [self.collection.headers[i] for i in self.indices]

    @lazyprop
    def coverage(self):
        total = float(self.collection.num_species())
        return [self.collection.lengths[i] / total for i in self.indices]

    @lazyprop
    def trees(self):
        return [self.collection.trees[i] for i in self.indices]

    @lazyprop
    def mrp_tree(self):
        trees = [tree.newick if hasattr('newick', tree) else tree for tree in self.trees]
        return Alignment().get_mrp_supertree(trees)

    def get_tree_collection_strings(self, scale=1, guide_tree=None):
        """ Function to get input strings for tree_collection
        tree_collection needs distvar, genome_map and labels -
        these are returned in the order above
        """
        return self.collection.get_tree_collection_strings(self.indices, scale, guide_tree)

    def qfile(self, models=None, default_dna='DNA', default_protein='LG', sep_codon_pos=False,
              ml_freqs=False, emp_freqs=False):
        from_ = 1
        to_ = 0
        qs = list()
        if models is None:
            if ml_freqs:
                default_dna += 'X'
                default_protein += 'X'
            if emp_freqs and not ml_freqs:
                default_protein += 'F'
            default_models = dict(dna=default_dna, protein=default_protein)
            models = [default_models[m] for m in self.datatypes]

        for (length, name, datatype, model) in zip(self.lengths, self.names,
                                                   self.datatypes, models):
            to_ += length
            if datatype == 'dna' and sep_codon_pos:
                qs.append('{}, {} = {}-{}/3'.format(model, name, from_,
                                                    to_))
                qs.append('{}, {} = {}-{}/3'.format(model, name, from_ + 1,
                                                    to_))
                qs.append('{}, {} = {}-{}/3'.format(model, name, from_ + 2,
                                                    to_))
            else:
                qs.append('{}, {} = {}-{}'.format(model, name, from_,
                                                  to_))
            from_ += length
        return '\n'.join(qs)

    def paml_partitions(self):
        return 'G {} {}'.format(len(self.lengths),
                                ' '.join(str(x) for x in self.lengths))
