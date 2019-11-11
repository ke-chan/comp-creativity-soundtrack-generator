import pickle
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 

#open the word_emotion_dict from the pickle
with open('word_emotion_dict.pickle', 'rb') as handle:
    word_emotion_dict = pickle.load(handle)

def get_words(filename):
    #read in a text file and return a list of words from the text file with stopwords removed
    with open(filename, 'r') as file:
        data = file.read().replace('\n', ' ')
    stop_words = set(stopwords.words('english')) 
    word_tokens = word_tokenize(data) 
    #print(data)
    filtered_sentence = [w for w in word_tokens if not w in stop_words] 
    #print(filtered_sentence)
    return filtered_sentence

#get_words("test.txt")
    


