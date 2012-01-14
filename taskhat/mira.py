# simple online MIRA classifier

import time
import util
import gobject
from collections import defaultdict
from pickle import loads, dumps
from ngrams import ngen

def benchmark(f):
    def g(*args):
        start = time.time()
        ans = f(*args)
        print 1000*(time.time() - start), "ms for", str(f).split()[1] + "()"
        return ans
    return g

class MiraClassifier(object):
    def __init__(self, labels=[], path=None):
        self.weights = defaultdict(util.Counter)
        for l in labels:
            self.weights[l]
        self.path = path
        if path:
            try:
               with open(path, 'r') as f:
                  self.weights.update(loads(f.read()))
               print 'Loaded MIRA weights'
            except IOError, e:
               print e

    @benchmark
    def update(self, correct_label, datum):
        C = 0.003
        chosen_label = self.classify(datum)
        if chosen_label != correct_label:
            tau = min(C,
              ((self.weights[chosen_label] - self.weights[correct_label])
                * datum + 1.0) / (2*(datum*datum)))
            scaled_datum = datum.copy()
            scaled_datum.divideAll(1.0/tau)
            if chosen_label != None:
                self.weights[chosen_label] -= scaled_datum
            self.weights[correct_label] += scaled_datum
        self.prune()

    @benchmark
    def classify(self, datum):
        vectors = util.Counter()
        for l in self.weights.keys():
            vectors[l] = self.weights[l] * datum
        return vectors.argMax()

    def prune(self):
        # TODO reduce dimensionality of weight vectors
        pass

    def save(self):
        def callback():
            if self.path:
                with open(self.path, 'w') as f:
                    f.write(dumps(self.weights))
                print 'Saved MIRA weights'
            return False
        gobject.idle_add(callback)

    def report(self):
        print "num labels", len(self.weights)
        print "dimensions", map(len, self.weights.values())

if __name__ == '__main__':
    classifier = MiraClassifier()
    while True:
        print "Enter a training line:",
        try:
            line = raw_input()
        except EOFError:
            break
        ngrams = ngen(line)
        label = classifier.classify(ngrams)
        print "Enter the right label [guessed %s]:" % label,
        line = raw_input()
        if line:
            classifier.update(line, ngrams)
        else:
            classifier.update(label, ngrams)
        classifier.report()
    print
    for k, weights in classifier.weights.items():
        if k is None:
            continue
        print
        print k, '-', '.'.join(map(
            lambda (k,v): k
            , sorted(weights.items(), key=lambda x: -x[1])[:15]))

# vim: et sw=4
