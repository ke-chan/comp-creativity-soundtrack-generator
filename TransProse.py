import numpy as np
import math
from numpy.random import choice
import pickle

PROB_MAP = [0.5, 0.15, 0.075, 0.025, 0.025, 0.075, 0.15]
PITCH_RANK = [0, 4, 2, 5, 1, 3, 6]
PITCH_MAP_MAJOR = ["C", "D", "E", "F", "G", "A", "B"]
PITCH_MAP_MINOR = ["C", "D", "Eb", "F", "G", "Ab", "Bb"]
#PITCH_MAP_MINOR = ["A", "B", "C", "D", "E", "F", "G"]

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
        outputDictionary = {}
        outputDictionary["tempo"] = self.tempo
        outputDictionary["melodies"] = [melody.output() for melody in self.melodies]
        return outputDictionary

    def setTempo(self, angerDensity, joyDensity, sadnessDensity, minTempo = 40, maxTempo = 180, minActive = -0.002, maxActive = 0.017):
        active = ((angerDensity + joyDensity) / 2)
        passive = sadnessDensity
        activityScore = active - passive

        self.tempo = ((active/(maxTempo - minTempo))*180)

        self.tempo =  minTempo + (((active - minActive) * (maxTempo - minTempo)) / (maxActive - minActive))
        return self.tempo

    def setKey(self, positiveCount, negativeCount):
        if positiveCount > negativeCount:
            self.key = "major"
        else:
            self.key = "minor"
        print(self.key)
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
        (overallCounts, overallWordCount) = self.calculateCounts(theText)
        self.setTempo(overallCounts["anger"] / overallWordCount, overallCounts["joy"] / overallWordCount, overallCounts["sadness"] / overallWordCount)
        self.setKey(overallCounts["positive"], overallCounts["negative"])

        # Calculate melody tags (i.e. overall + 8 different emotions)
        sortedCounts = sorted(overallCounts.items(), key=lambda kv: kv[1])
        # Start with the overall melody (M_0)
        self.melodies.append(Melody(self.key))
        # Go through each of the keys
        for (key, value) in sortedCounts:
            if key == "positive" or key == "negative" or key == "overall":
                continue
            elif len(self.melodies) < numMelodyLines:
                self.melodies.append(Melody(self.key, key))

        JS = (overallCounts["joy"] - overallCounts["sadness"]) / overallWordCount
        M0 = 0
        # Now we set the octaves for each Melody
        for melody in self.melodies:
            if melody.tag == "overall":
                melody.octave = MIN_OCTAVE + round(((JS - -0.1)*(MAX_OCTAVE - MIN_OCTAVE)) / (0.3 - -0.1))
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
                    theMeasure = Measure(counts[melody.tag] / wordCount, melody.octave, measureChunk)
                    melody.measures.append(theMeasure)

            maxMeasureDensity = max([x.emotion_density for x in melody.measures])
            minMeasureDensity = min([x.emotion_density for x in melody.measures])

            #print(minMeasureDensity)
            #print(maxMeasureDensity)

            for theMeasure in melody.measures:
                index = math.ceil(4 * (theMeasure.emotion_density - minMeasureDensity) / (maxMeasureDensity - minMeasureDensity))
                #theMeasure = Measure((2**(index - 1)), counts[melody.tag] / wordCount)
                # print(index)
                # print(2**(index - 1))
                # print(PITCH_RANK)
                # print(theMeasure.num_notes)
                # print(PROB_MAP[pitchIndex:] + PROB_MAP[:pitchIndex])
                theMeasure.num_notes = (2**(index))

                tempList = []
                for aChunk in np.array_split(theMeasure.theText, theMeasure.num_notes):
                    (counts, wordCount) = self.calculateCounts(aChunk)
                    thePitch = round(6 * ((counts[melody.tag] / wordCount) - minMeasureDensity) / (maxMeasureDensity - minMeasureDensity))
                    theMeasure.notes.append(PITCH_RANK[thePitch])

                print(theMeasure.notes)

                #theMeasure.notes = choice(PITCH_RANK, theMeasure.num_notes, p=(PROB_MAP[pitchIndex:] + PROB_MAP[:pitchIndex]))

class Measure:
    def __init__(self, density, octave, someText):
        self.num_notes = 0
        self.octave = octave
        self.emotion_density = density
        self.notes = []
        self.theText = someText

    def output(self, key):
        if key == "major":
            return [(PITCH_MAP_MAJOR[note] + str(self.octave), 4 / self.num_notes) for note in self.notes]
        else:
            return [(PITCH_MAP_MINOR[note] + str(self.octave), 4 / self.num_notes) for note in self.notes]

class Melody:
    def __init__(self, theKey, tag="overall"):
        self.measures = []
        self.tag = tag
        self.octave = 0
        self.key = theKey

    def output(self):
        # Build a list of lists using Measure's output function
        output = [measure.output(self.key) for measure in self.measures]
        # Flatten list and return value
        return [val for sublist in output for val in sublist]


        #print([note for measure in output for note in measure.notes])
