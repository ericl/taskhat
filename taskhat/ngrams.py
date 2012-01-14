import util
import re

def substitutions(token):
    yield token
    variation = re.sub('[0-9]', 'N', token)
    if variation != token:
        yield variation

def ngen(text, nn=[1,2,3,4]):
    """
    Returns a dictionary of ngram counts for a string.
    """
    ngrams = util.Counter()
    nn.sort()
    text = text.lower()
    for n in nn:
        for i in range(len(text)-n+1):
            token = text[i:i+n]
            for s in substitutions(token):
                ngrams[s] += 1
    ngrams[int(len(text)**0.5)] = 1
    return ngrams

if __name__ == '__main__':
    print ngen("It 'ate' 237 apples.")
