### Stemming
# similar words in different variants
# ex: imaging, images
# use Natural Language Toolkit (NLTK)
# link with vectorizer

import nltk.stem
from sklearn.feature_extraction.text import CountVectorizer
import os
import sys
import scipy as sp
from sklearn.feature_extraction.text import TfidfVectorizer


DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")    
TOY_DIR = os.path.join(DATA_DIR, "toy")

posts = [open(os.path.join(TOY_DIR, f)).read() for f in os.listdir(TOY_DIR)]



s= nltk.stem.SnowballStemmer('english')
s.stem("graphics")
# u'graphic'
s.stem("kissing")
# u'kiss'
s.stem("imaging")
s.stem("image")
# u'imag'
s.stem("imagination")
s.stem("imagine")
# u'imagin

### Extend vectorizer with NLTK stemmer

english_stemmer = nltk.stem.SnowballStemmer('english')

class StemmedCountVectorizer(CountVectorizer):
    def build_analyzer(self):
        analyzer = super(StemmedCountVectorizer, self).build_analyzer()
        return lambda doc : (english_stemmer.stem(w) for w in analyzer(doc))
        
vectorizer = StemmedCountVectorizer(min_df=1, stop_words='english')

# fit
X_train = vectorizer.fit_transform(posts)

# size
num_samples, num_features = X_train.shape

# reword
#print("#samples: %d" % num_samples)
#print("#features: %d" % num_features)
#print(vectorizer.get_feature_names())
'''
[u'actual', u'capabl', u'contain', u'data', u'databas', u'imag',
u'interest', u'learn', u'machin', u'perman', u'post', u'provid',
u'safe', u'storag', u'store', u'stuff', u'toy']
'''
# new post
new_post = "imaging databases"
new_post_vec = vectorizer.transform([new_post])

# best_post
def best_post(dist_f):
    best_doc = None
    best_dist = sys.maxint
    best_i = None
    for i in range(0, num_samples):
        post = posts[i]    
        if post == new_post:
            continue    
        post_vec = X_train.getrow(i)
        d = dist_f(post_vec, new_post_vec)
        print "=== Post %i with dist=%.2f: %s"%(i, d, post)
        if d < best_dist:
            best_dist = d
            best_i = i
            
    print("Best post is %i with dist=%.2f"%(best_i, best_dist))
    
### need to normalize the word count vectors
def dist_norm(v1, v2):
    v1_normalized = v1 / sp.linalg.norm(v1.toarray())
    v2_normalized = v2 / sp.linalg.norm(v2.toarray())
    delta = v1_normalized - v2_normalized
    return sp.linalg.norm(delta.toarray())

# get beest post using normalized euclidean dist
#best_post(dist_norm)

'''
=== Post 0 with dist=1.41: This is a toy post about machine learning.
Actually, it contains not much interesting stuff.
=== Post 1 with dist=0.86: Imaging databases provide storage
capabilities.
=== Post 2 with dist=0.63: Most imaging databases safe images
permanently.
=== Post 3 with dist=0.77: Imaging databases store data.
=== Post 4 with dist=0.77: Imaging databases store data. Imaging
databases store data. Imaging databases store data.
Best post is 2 with dist=0.63
'''


### TF - IDF
### Term Frequency - Inverse Document Frequency

# some words occur many times but only withing certain posts
# they are important to those posts

# count term frequency for every post
# discount those that appear in many posts

# we want a high value for a given term in a given value if that term occurs often in that particular post 
# and very rarely anywhere else

# TF = counting part
# IDF = discounting part


def tfidf(term, doc, Docset):
    nCountTermInDoc = doc.count(term)
    uniqueWordsInDoc = set(doc)
    nCountAllTermsInDoc = sum (doc.count(w) for w in uniqueWordsInDoc)
    tf = float(nCountTermInDoc) / nCountAllTermsInDoc
    
    nDocsWithTerm = len( [document for document in Docset if term in document])
    nDocs = len(Docset)
    idf = sp.log( float(nDocs) / nDocsWithTerm ) 
    
    return tf * idf
    
'''
def tfidf(t, d, D):
    tf = float(d.count(t)) / sum(d.count(w) for w in set(d))
    idf = sp.log(float(len(D)) / (len([doc for doc in D if t in doc])))
    return tf * idf
'''
 
a, abb, abc = ['a'], ['a', 'b', 'b'], ['a', 'b', 'c']

D = [a, abb, abc]

print(tfidf('a', a, D))
# 1 / 1 * log(3 / 3) = 1 * 0 = 0
# a appears in all documents so it is useless

print(tfidf('b', abb, D))
# 2 / 3 * ln(3 / 2) = 0.27031007207
# 0.27031007207

print(tfidf('a', abb, D))
# 0 

print(tfidf('b', abc, D))
# 0.135

print(tfidf('c', abc, D))
# 0.366

# c in abc is more meaningfull than b in abc
# b in abb is more meaningfull than b in abc


### Use NTLK TfidfVectorizer and the previous stemmer
class StemmedTfidfVectorizer(TfidfVectorizer):
    def build_analyzer(self):
        analyzer = super(TfidfVectorizer, self).build_analyzer()
        
        return lambda doc: (
            english_stemmer.stem(w) for w in analyzer(doc))

vectorized = vectorizer.fit_transform(posts)
num_samples, num_features = vectorized.shape
print("#samples: %d, #features: %d" % (num_samples, num_features))
print(vectorizer.get_feature_names())

# samples: 3529, #features: 4712

# the resulting vectors will not contain counts
# they will contain individual TF-IDF values


### So far
# 1 Tokenize the text
# 2 Throw away words that appear too ofter
# 3 Throw away words that appear too seldom
# 4 Count remaining words
# 5 Calculate TF-IDF from counts, considering the whoel corpus
# 
# overall: noisy words => feature values
# 6 next efficiently build cluster from the features

# Problems 

# does not cover word relations
# crocodile eats ana === ana eats crocodile

# does not capture negations
# he does not walk
# can fix this by considering BIGRAMs or TRIGRAMS (3 words in a row)

# misspelled words are a problem
