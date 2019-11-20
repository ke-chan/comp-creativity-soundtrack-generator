import text_to_emotion as utility
import TransProse

theText = utility.get_words_from_text("test.txt")

theTheme = TransProse.Theme()

theTheme.generate(theText)

theTheme.output()
