import pickle
import requests
import string
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer

def get_words_from_text(filename):
    #read in a text file and return a list of words from the text file with stopwords removed
    with open(filename, 'r') as file:
        data = file.read().replace('\n', ' ')
    stop_words = set(stopwords.words('english'))
    data = data.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    word_tokens = tokenizer.tokenize(data)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    #print(filtered_sentence)
    return filtered_sentence

#get_words_from_text("test.txt")

def get_words_from_wikiurl(url):
    res = requests.get(url)
    html_page = res.text
    soup = BeautifulSoup(html_page, "html.parser")
    #print(soup.prettify().encode("utf-8"))
    print()
