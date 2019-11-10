import pandas as pd 
import pickle
words = pd.read_csv("NRC-Emotion-Lexicon-Wordlevel-v0.92.txt", sep='\t')
#print(words.shape)
#read in the tab separated file

word_emotions = {}
#for each item, add it to the dictionary with the word as the key and the list of emotions as the value
for index, row in words.iterrows():
    if row[0] in word_emotions.keys():
        if row[2] == 1:
            word_emotions[row[0]].append(row[1])
    else:
        word_emotions[row[0]] = []
        if row[2] == 1:
            word_emotions[row[0]].append(row[1])

#save the dict in a pickle       
with open('word_emotion_dict.pickle', 'wb') as handle:
    pickle.dump(word_emotions, handle, protocol=pickle.HIGHEST_PROTOCOL)
#print(word_emotions)
    



