import util
import re

def canonicalizations(text):
    text = text.lower()
    yield text
    yield re.sub('[^a-z]', '', text)

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
    for t in canonicalizations(text):
        for n in nn:
            for i in range(len(t)-n+1):
                token = t[i:i+n]
                for s in substitutions(token):
                    ngrams[s] += 1
    return ngrams

if __name__ == '__main__':
    print ngen("It 'ate' 237 apples.")
