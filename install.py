import os

print "Setup started"

os.system('pip install nltk textblob wikipedia hurry.filesize geotext gensim colorama tweepy exrex requests bs4')
os.system('python -m textblob.download_corpora')

import nltk

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

print "Setup finished!"