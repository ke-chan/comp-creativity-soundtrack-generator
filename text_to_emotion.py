import pickle
#open the word_emotion_dict from the pickle
with open('word_emotion_dict.pickle', 'rb') as handle:
    word_emotion_dict = pickle.load(handle)

