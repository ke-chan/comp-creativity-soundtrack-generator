import pickle
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer

def get_words_from_text(filename):
    #read in a text file and return a list of words from the text file with stopwords removed
    with open(filename, 'r',encoding='utf-8') as file:
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
    paragraphs = list(str(soup.find_all("p")))
    paragraphs = "".join(paragraphs)
    soup = BeautifulSoup(paragraphs, "html.parser")
    data = soup.get_text()
    stop_words = set(stopwords.words('english'))
    data = data.lower()
    tokenizer = RegexpTokenizer(r'\w+')
    word_tokens = tokenizer.tokenize(data)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return filtered_sentence

#get_words_from_wikiurl("https://starwars.fandom.com/wiki/Luke_Skywalker")
#print(get_words_from_text("test.txt"))
