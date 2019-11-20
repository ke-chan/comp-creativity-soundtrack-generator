import numpy as np
import math
from numpy.random import choice
import pickle

PROB_MAP = [0.5, 0.15, 0.075, 0.025, 0.025, 0.075, 0.15]
PITCH_RANK = [1, 5, 3, 6, 2, 4, 7]
PITCH_MAP = ["C", "D", "E", "F", "G", "A", "B"]

JS_MAX = 1 # FIXME: this is not a good estimate
JS_MIN = 0 ## FIXME: SAME

MAX_OCTAVE = 6
MIN_OCTAVE = 4

MEASURE_CHUNKS = 4
PLOT_CHUNKS = 4

WORD_EMOTION_DICT = pickle.load(open('word_emotion_dict.pickle', 'rb'))

EMOTIONS = ["anticipation", "anger", "joy", "fear", "disgust", "sadness", "surprise", "trust", "overall", "positive", "negative"]

class Theme:
    def __init__(self):
        self.melodies = []
        self.key = ""
        self.tempo = 0

    def output(self):
        print("T" + str(round(self.tempo)) + " KC" + self.key + " ")
        for melody in self.melodies:
            melody.output()

    def setTempo(self, angerDensity, joyDensity, sadnessDensity, minTempo = 40, maxTempo = 180, minActive = -0.002, maxActive = 0.017):
        active = ((angerDensity + joyDensity) / 2)
        passive = sadnessDensity
        activityScore = active - passive
        self.tempo =  minTempo + (((activityScore - minActive) * (maxTempo - minTempo)) / (maxActive - minActive))
        return self.tempo

    def setKey(self, positiveCount, negativeCount):
        if positiveCount > negativeCount:
            self.key = "major"
        else:
            self.key = "minor"
        return self.key

    def calculateCounts(self, theText):
        counts = {emotion: 0 for emotion in EMOTIONS}
        totalWordCount = len(theText)

        for word in theText:
            if word not in WORD_EMOTION_DICT:
                continue
            loadEmotions = WORD_EMOTION_DICT[word]
            for anEmotion in loadEmotions:
                counts[anEmotion] += 1
                if anEmotion != "positive" and anEmotion != "negative":
                    counts["overall"] += 1
        return (counts, totalWordCount)

    def generate(self, theText, numMelodyLines = 3):

        print(WORD_EMOTION_DICT["chuckle"])

        (overallCounts, overallWordCount) = self.calculateCounts(theText)
        print(overallCounts)
        self.setTempo(overallCounts["anger"] / overallWordCount, overallCounts["joy"] / overallWordCount, overallCounts["sadness"] / overallWordCount)
        self.setKey(overallCounts["positive"], overallCounts["negative"])

        # Calculate melody tags (i.e. overall + 8 different emotions)
        sortedCounts = sorted(overallCounts.items(), key=lambda kv: kv[1])
        # Start with the overall melody (M_0)
        self.melodies.append(Melody())
        # Go through each of the keys
        for (key, value) in sortedCounts:
            if key == "positive" or key == "negative" or key == "overall":
                continue
            elif len(self.melodies) < numMelodyLines:
                self.melodies.append(Melody(key))

        JS = (overallCounts["joy"] - overallCounts["sadness"]) / overallWordCount
        M0 = 0
        # Now we set the octaves for each Melody
        for melody in self.melodies:
            if melody.tag == "overall":
                melody.octave = MIN_OCTAVE + round(((JS - JS_MIN)*(MAX_OCTAVE - MIN_OCTAVE)) / (JS_MAX - JS_MIN))
                M0 = melody.octave
            elif melody.tag == "joy" or melody.tag == "trust":
                melody.octave = M0 + 1
            elif melody.tag == "anger" or melody.tag == "fear" or melody.tag == "sadness" or melody.tag == "disgust":
                melody.octave = M0 - 1
            else:
                melody.octave = M0

        plotChunks = np.array_split(theText, PLOT_CHUNKS)
        plotChunkCounts = []
        for melodyChunk in plotChunks:
            plotChunkCounts.append(self.calculateCounts(melodyChunk))

        for melody in self.melodies:
            chunkDensities = []
            for chunkCount in plotChunkCounts:
                chunkDensities.append(chunkCount[0][melody.tag] / chunkCount[1])

            for plotChunk in plotChunks:
                for measureChunk in np.array_split(plotChunk, MEASURE_CHUNKS):
                    (counts, wordCount) = self.calculateCounts(measureChunk)
                    theMeasure = Measure(counts[melody.tag] / wordCount)
                    melody.measures.append(theMeasure)

            maxMeasureDensity = max([x.emotion_density for x in melody.measures])
            minMeasureDensity = min([x.emotion_density for x in melody.measures])

            for theMeasure in melody.measures:
                index = math.ceil(5 * ((counts[melody.tag] / wordCount) - minMeasureDensity) / (maxMeasureDensity - minMeasureDensity))
                pitchIndex = round(6 * ((counts[melody.tag] / wordCount) - minMeasureDensity) / (maxMeasureDensity - minMeasureDensity))
                #theMeasure = Measure((2**(index - 1)), counts[melody.tag] / wordCount)
                # print(index)
                # print(2**(index - 1))
                # print(PITCH_RANK)
                # print(theMeasure.num_notes)
                # print(PROB_MAP[pitchIndex:] + PROB_MAP[:pitchIndex])
                theMeasure.num_notes = (2**(index - 1))
                theMeasure.notes = choice(PITCH_RANK, theMeasure.num_notes, p=(PROB_MAP[pitchIndex:] + PROB_MAP[:pitchIndex]))

class Measure:
    def __init__(self, density):
        self.num_notes = 0
        self.emotion_density = density
        self.notes = []

    def output(self):
        print(self.notes)

class Melody:
    def __init__(self, tag="overall"):
        self.measures = []
        self.tag = tag
        self.octave = 0

    def output(self):
        for measure in self.measures:
            measure.output()
