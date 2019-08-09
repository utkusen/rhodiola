#!/usr/bin/env python
# encoding: utf-8
import tweepy 
import csv
from textblob import TextBlob
import operator
from nltk.tag import pos_tag
from nltk.corpus import stopwords
import re, string
from collections import Counter
from textblob.wordnet import Synset
import sys
import wikipedia 
import re
import warnings
import exrex
import argparse
import os
from hurry.filesize import size
from hurry.filesize import alternative
from geotext import GeoText
from colorama import Fore, Back, Style
import requests
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""

print '''

            Utku Sen's
             _____  _               _ _       _                            
            |  __ \| |             | (_)     | |                            
            | |__) | |__   ___   __| |_  ___ | | __ _ 
            |  _  /| '_ \ / _ \ / _` | |/ _ \| |/ _` |                       
            | | \ \| | | | (_) | (_| | | (_) | | (_| |
            |_|  \_\_| |_|\___/ \__,_|_|\___/|_|\__,_|                           

Personalized wordlist generation with NLP, by analyzing tweets. (A.K.A crunch2049)                        

'''

with open("stopwords.txt") as f:
    content = f.readlines()
extra_stopwords = [x.strip() for x in content]

def get_all_tweets(screen_name):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    alltweets = []  
    new_tweets = api.user_timeline(screen_name = screen_name,count=200, include_rts=False,tweet_mode = 'extended')
    alltweets.extend(new_tweets)
    oldest = alltweets[-1].id - 1
    while len(new_tweets) > 0:
      new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest, include_rts=False,tweet_mode = 'extended')
      alltweets.extend(new_tweets)
      oldest = alltweets[-1].id - 1
      print "Downloaded %s tweets.." % (len(alltweets))
    outtweets = ""
    for tweet in alltweets:
        if tweet.full_text.encode("utf-8").startswith('@'):
            pass
        else:
            outtweets += (tweet.full_text.encode("utf-8").split('https://t.co')[0])
    return outtweets
            
def find_noun_phrases(string):
    noun_counts = {}
    try:
        blob = TextBlob(string.decode('utf-8'))
    except:
        print "Error occured"
        return None 
    if blob.detect_language() != "en":
        print "Tweets are not in English"
        sys.exit(1)
    else:   
        for noun in blob.noun_phrases:
            if noun in stopwords.words('english') or noun in extra_stopwords or noun == '' or len(noun) < 3:
                pass
            else:   
                noun_counts[noun.lower()] = blob.words.count(noun)
    sorted_noun_counts = sorted(noun_counts.items(), key=operator.itemgetter(1),reverse=True)
    return sorted_noun_counts[0:15]

def find_proper_nouns(string):
    pattern = re.compile('[\W_]+', re.UNICODE)
    tagged_sent = pos_tag(string.split())
    propernouns = [re.sub(r'\W+', '', word.lower()) for word,pos in tagged_sent if pos == 'NNP']
    last_propernouns = []
    for word in propernouns:
        if word in stopwords.words('english') or word in extra_stopwords or word == '' or len(word) < 3:
            pass
        else:
            last_propernouns.append(word)   
    propernouns_dict = dict(Counter(last_propernouns))
    sorted_propernouns_dict = sorted(propernouns_dict.items(), key=operator.itemgetter(1),reverse=True)
    return sorted_propernouns_dict[0:15]

def word_similarity(word1,word2):
    try:
        string1 = Synset(word1+'.n.01')
        string2 = Synset(word2+'.n.01')
        return string1.path_similarity(string2)
    except:
        return 0    

def mass_similarity_compare(wordlist):
    clean_wordlist = []
    out_wordlist = []
    for word in wordlist:
        clean_wordlist.append(word[0])
    for word in clean_wordlist:
        for word2 in clean_wordlist:
            similarity = word_similarity(word,word2)
            if similarity < 0.12:
                pass
            else:
                if word.lower() == word2.lower():
                    pass
                else:   
                    out_wordlist.append(word+word2)
    return out_wordlist         


def get_year(proper_noun):
    try:
        page = wikipedia.page(proper_noun)
        year = re.findall('[1-3][0-9]{3}',page.summary)
        return year[0]
    except:
        return None

def get_cities(proper_noun):
    page = wikipedia.page(proper_noun)
    geo = GeoText(page.summary)
    return list(set(geo.cities))
     

def regex_parser(regex):
    try:
        string_list = list(exrex.generate(regex))
        return string_list
    except:
        print "Incorrect regex syntax"
        sys.exit(1)

def mask_parser(mask,word):
    mask_items = mask.split('?')
    mask_length = len(mask_items)
    word_chars = list(word)
    i = 0
    for mask in mask_items[1:]:
        if len(word_chars) < i+1:
            break
        else:    
            if mask == 'l':
                word_chars[i] = word_chars[i].lower()
            elif mask == 'u':
                word_chars[i] = word_chars[i].capitalize()
            i += 1
    final_word = ''.join(word_chars)        
    return final_word             

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def action(twitter_username,word_type='all',regex_place='suffix',regex=None,mask=None,filename=None,urlfile=None):
    final_wordlist = []
    year_list = []
    city_list = []
    noun_phrases_display = []
    proper_nouns_display = []
    text = ''
    if twitter_username is not "none":
        try:
            print "Downloading tweets from: " + twitter_username
            text = get_all_tweets(twitter_username)
        except:
            print "Couldn't download tweets. Your credentials maybe wrong or you rate limited."
            sys.exit(1)
        print "Analyzing tweets, this will take a while.."
        print ""
    else:
        if filename is None and urlfile is None:
            print "No input source is specified"
            sys.exit(0)
        elif filename is not None and urlfile is None:
            print "Analyzing the text file.."
            print ""    
            with open(filename, 'r') as textfile:
                text = textfile.read().replace('\n', '')
        elif filename is None and urlfile is not None:
            print "Analyzing the given URLs.."
            print ""    
            with open(urlfile, 'r') as textfile:
                urls = textfile.read().splitlines()
                for url in urls:
                    print "Connecting to: " + url
                    try:
                        r = requests.get(url,timeout=20)
                    except:
                        print "Connection failed"
                        continue    
                    soup = BeautifulSoup(r.text)
                    for script in soup(["script", "style"]):
                        script.decompose()
                    clean_text = soup.get_text()
                    lines = (line.strip() for line in clean_text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    clean_text = '\n'.join(chunk for chunk in chunks if chunk)
                    text += clean_text 
    text = ''.join(i for i in text if ord(i)<128)
    noun_phrases = find_noun_phrases(text)
    proper_nouns = find_proper_nouns(text)        
    paired_nouns = mass_similarity_compare(noun_phrases)
    paired_propers = mass_similarity_compare(proper_nouns)
    for i in range(len(noun_phrases)):
        noun_phrases_display.append(str(noun_phrases[i][0])+":"+str(noun_phrases[i][1]))

    print(Fore.GREEN + 'Most used nouns: ' + Style.RESET_ALL + ", ".join(noun_phrases_display))  
    for i in range(len(proper_nouns)):
        proper_nouns_display.append(str(proper_nouns[i][0])+":"+str(proper_nouns[i][1]))
    print(Fore.GREEN + 'Most used proper nouns: ' + Style.RESET_ALL + ", ".join(proper_nouns_display))
    print ""
    print "Gathering related locations and years.."
    print ""
    for noun in proper_nouns:
        print "Getting info for: " + str(noun)
        try:
            temp_city_list = get_cities(noun[0])[0:3]
        except:
            continue    
        for city in temp_city_list:
            city_list.append(city.replace(" ", "").lower())
    if city_list:
        city_list = list(set(city_list))
        for city in city_list:
            city_tuple = (city,0)
            proper_nouns.append(city_tuple) 
    for word in noun_phrases:
        if mask is None:
            final_wordlist.append(word[0])
        else:
            final_wordlist.append(mask_parser(mask,word[0]))    
    for word in proper_nouns:
        if mask is None:
            final_wordlist.append(word[0])
        else:
            final_wordlist.append(mask_parser(mask,word[0]))
        if word_type != 'base':
            try:
                year = get_year(word[0])
                if year != None:
                    if year not in year_list:
                        year_list.append(year)
            except:
                pass
    for word in paired_nouns:
        if mask is None:
            final_wordlist.append(word)
        else:
            final_wordlist.append(mask_parser(mask,word))
    for word in paired_propers:
        if mask is None:
            final_wordlist.append(word)
        else:
            final_wordlist.append(mask_parser(mask,word)) 
    if regex_place is not None or regex is not None:
        new_items = regex_parser(regex)
        for item in new_items:
            for word in final_wordlist:
                with open("regex_words.txt","a+") as regex_words:
                    if regex_place == 'prefix':
                        regex_words.write(item+word+'\n')
                    else:
                        regex_words.write(word+item+'\n')     
    with open(twitter_username+"_wordlist.txt",'w+') as wordlist:
        for word in final_wordlist:
            wordlist.write(word+'\n')
        if word_type != 'base':    
            for word in final_wordlist: 
                for year in list(set(year_list)):
                    wordlist.write(word+year+'\n')
    if regex is not None:                
        os.system('cat regex_words.txt >> ' +twitter_username+"_wordlist.txt")                
        os.remove('regex_words.txt')
    raster_size = os.path.getsize(twitter_username+"_wordlist.txt")
    print "Wordlist is written to: " + twitter_username+"_wordlist.txt"
    print "Size of the wordlist: " + size(raster_size, system=alternative)
    print "Number of lines in wordlist: " + str(file_len(twitter_username+"_wordlist.txt"))         


parser = argparse.ArgumentParser()
parser.add_argument('--username', action='store', dest='username', help='Twitter username', required=False,default="none")
parser.add_argument('--regex_place', action='store', dest='regex_place', help='Regex place: prefix or suffix', required=False)
parser.add_argument('--regex', action='store', dest='regex', help='Regex syntax', required=False)
parser.add_argument('--mask', action='store', dest='mask', help='Mask structure of wordlist', required=False)
parser.add_argument('--filename', action='store', dest='filename', help='Arbitrary textfile to analyze', required=False)
parser.add_argument('--urlfile', action='store', dest='urlfile', help='File which contains URLs to analyze', required=False)
argv = parser.parse_args()

action(twitter_username=argv.username,regex_place=argv.regex_place,regex=argv.regex,mask=argv.mask,filename=argv.filename,urlfile=argv.urlfile)



