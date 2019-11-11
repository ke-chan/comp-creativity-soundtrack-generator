import numpy as np
import math

JS_MAX = 1 # FIXME: this is not a good estimate
JS_MIN = 0 ## FIXME: SAME

MAX_OCTAVE = 6
MIN_OCTAVE = 4

MEASURE_CHUNKS = 4
PLOT_CHUNKS = 4

EMOTIONS = ["anticipation", "anger", "joy", "fear", "disgust", "sadness", "surprise", "trust", "overall", "positive", "negative"]

class Theme:
    def __init__(self):
        self.melodies = []
        self.key = ""
        self.tempo = 0

    def setTempo(angerDensity, joyDensity, sadnessDensity, minTempo = 40, maxTempo = 180, minActive = -0.002, maxActive = 0.017):
        active = ((angerDensity + joyDensity) / 2)
        passive = sadnessDensity
        activityScore = active - passive
        self.tempo =  minTempo + (((active - minActive) * (maxTempo - minTempo)) / (maxActive - minActive))
        return self.tempo

    def setKey(positiveCount, negativeCount):
        if positiveCount > negativeCount:
            self.key = "major"
        else:
            self.key = "minor"
        return self.key

    def calculateCounts(theText):

        counts = {emotion: 0 for emotion in EMOTIONS}
        totalWordCount = len(theText)

        for word in theText:
            loadEmotions = MAGIC_DICTIONARY[word]
            for anEmotion in loadEmotions:
                counts[anEmotion] += 1
                if anEmotion != "positive" and anEmotion != "negative":
                    counts["overall"] += 1

        return (counts, totalWordCount)

    def generate(theText, numMelodyLines = 3):

        (overallCounts, overallWordCount) = calculateCounts(theText)
        setTempo(overallCounts["anger"] / overallWordCount, overallCounts["joy"] / overallWordCount, overallCounts["sadness"] / overallWordCount)
        setKey(overallCounts["positive"], overallCounts["negative"])

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

        JS = (overallCounts["joy"] - overallCounts["sadness"] / overallWordCount)
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
            plotChunkCounts.append(calculateCounts(melodyChunk))

        for melody in self.melodies:
            chunkDensities = []
            for chunkCount in plotChunkCounts:
                chunkDensities.append(chunkCount[0][melody.tag] / chunkCount[1])
            maxChunkDensity = max(chunkDensities)
            minChunkDensity = min(chunkDensities)
            for plotChunk in plotChunks:
                for measureChunk in np.array_split(plotChunk, MEASURE_CHUNKS):
                    (counts, wordCount) = calculateCounts(measureChunk)
                    index = math.ceiling(5 * ((counts[melody.tag] / wordCount) - minChunkDensity) / (maxChunkDensity - minChunkDensity))
                    melody.measures.append(Measure(2**(index - 1)), counts[melody.tag] / wordCount)

                    ## TODO: Need to fill in the pitch selection


class Measure:
    def __init__(self, num_notes, density):
        self.num_notes = num_notes
        self.emotion_density = density

class Melody:
    def __init__(self, tag="overall"):
        self.measures = []
        self.tag = tag
        self.octave = 0
