import numpy as np
import math
from numpy.random import choice
import pickle

# Consonance Ranking
PITCH_RANK = [0, 4, 2, 5, 1, 3, 6]

# C Major
PITCH_MAP_MAJOR = ["C", "D", "E", "F", "G", "A", "B"]
# C Minor
PITCH_MAP_MINOR = ["C", "D", "Eb", "F", "G", "Ab", "Bb"]

# Arbitrary Constants from TransProse
JS_MAX = 1
JS_MIN = 0

# Hyperparameters that you should be able to change
MAX_OCTAVE = 6
MIN_OCTAVE = 4
MEASURE_CHUNKS = 4
PLOT_CHUNKS = 4

# Load in the NRC Emotion Pickled Dictionary
WORD_EMOTION_DICT = pickle.load(open('word_emotion_dict.pickle', 'rb'))

# NRC Emotions Listing
EMOTIONS = ["anticipation", "anger", "joy", "fear", "disgust", "sadness", "surprise", "trust", "overall", "positive", "negative"]

class Theme:
    """A Theme is the complete output of TransProse made up of constitunt melodies.

    The __init__ method may be documented in either the class level
    docstring, or as a docstring on the __init__ method itself.

    Either form is acceptable, but the two should not be mixed. Choose one
    convention to document the __init__ method and be consistent with it.

    Attributes:
        melodies (list): the list of Melodies .
        key (str): the key the melody follows.
        tempo (int): the tempo of the Theme

    """

    def __init__(self):
        self.melodies = []
        self.key = ""
        self.tempo = 0

    def output(self):
    """Method to output the Theme.

    Returns:
        A dictionary containing all of the relevant Theme data.

    """
        outputDictionary = {}
        outputDictionary["tempo"] = self.tempo
        outputDictionary["melodies"] = [melody.output() for melody in self.melodies]
        return outputDictionary

    def setTempo(self, angerDensity, joyDensity, sadnessDensity, minTempo = 40, maxTempo = 180, minActive = -0.002, maxActive = 0.017):
    """Calculate the tempo of the theme by using the active passive ratio """

        active = ((angerDensity + joyDensity) / 2)
        passive = sadnessDensity
        activityScore = active - passive

        self.tempo = ((active/(maxTempo - minTempo))*180)

        self.tempo =  minTempo + (((active - minActive) * (maxTempo - minTempo)) / (maxActive - minActive))
        return self.tempo

    def setKey(self, positiveCount, negativeCount):
        """Set the key of Theme based on the postive:negative ratio. """

        if positiveCount > negativeCount:
            self.key = "major"
        else:
            self.key = "minor"
        print(self.key)
        return self.key

    def calculateCounts(self, theText):
        """Scan through text and return NRC classified counts. """
        counts = {emotion: 0 for emotion in EMOTIONS}
        totalWordCount = len(theText)

        # Loop through each word and classify word by word
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
        """Main method to generate the Theme. """

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
        # Now we set the voicing octaves for each Melody
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

        # Split the input text into Plot chunks
        plotChunks = np.array_split(theText, PLOT_CHUNKS)
        plotChunkCounts = []
        for melodyChunk in plotChunks:
            plotChunkCounts.append(self.calculateCounts(melodyChunk))

        # For each melody, go through and generate
        for melody in self.melodies:

            # Find the min/max densities of chunks
            chunkDensities = []
            for chunkCount in plotChunkCounts:
                chunkDensities.append(chunkCount[0][melody.tag] / chunkCount[1])

            # Go through each plot chunk and measure and generate everything except Note selection
            for plotChunk in plotChunks:
                for measureChunk in np.array_split(plotChunk, MEASURE_CHUNKS):
                    (counts, wordCount) = self.calculateCounts(measureChunk)
                    theMeasure = Measure(counts[melody.tag] / wordCount, melody.octave, measureChunk)
                    melody.measures.append(theMeasure)

            # Find min and max densities for measure generation
            maxMeasureDensity = max([x.emotion_density for x in melody.measures])
            minMeasureDensity = min([x.emotion_density for x in melody.measures])

            # Find min and max densities for note generation
            tempList = []
            for theMeasure in melody.measures:
                index = math.ceil(4 * (theMeasure.emotion_density - minMeasureDensity) / (maxMeasureDensity - minMeasureDensity))
                theMeasure.num_notes = (2**(index))

                for aChunk in np.array_split(theMeasure.theText, theMeasure.num_notes):
                    (counts, wordCount) = self.calculateCounts(aChunk)
                    tempList.append(counts[melody.tag] / wordCount)

            # Generate notes
            for theMeasure in melody.measures:
                for aChunk in np.array_split(theMeasure.theText, theMeasure.num_notes):
                    (counts, wordCount) = self.calculateCounts(aChunk)

                    thePitch = math.floor(6 * ((counts[melody.tag] / wordCount) - min(tempList)) / (max(tempList) - min(tempList)))
                    theMeasure.notes.append(PITCH_RANK[thePitch])

class Measure:
    """Represents a single measure of a Melody.  """
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
    """Represents a single melody within the Theme.  """

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
