import text_to_emotion as utility
import TransProse
import pretty_midi

theText = utility.get_words_from_text("test.txt")

theTheme = TransProse.Theme()

theTheme.generate(theText)

theOutput = theTheme.output()
#print(theOutput["tempo"])
#print(theOutput["melodies"])





