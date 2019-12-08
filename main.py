import text_to_emotion as utility
import TransProse
import pretty_midi
import generate_midi
import subprocess

#theText = utility.get_words_from_text("test.txt")
theText = utility.get_words_from_wikiurl("https://starwars.fandom.com/wiki/Darth_Sidious")

theTheme = TransProse.Theme()

theTheme.generate(theText)

theOutput = theTheme.output()
#print(theOutput["tempo"])
#print(theOutput["melodies"])

generate_midi.gen_midi(theOutput["melodies"],60)

#Magenta Generate
"""
subprocess.call(["melody_rnn_generate","--config=attention_rnn", "--bundle_file=./models/attention_rnn.mag", "--output_dir=./generated","--num_outputs=1","--num_steps=528","--primer_midi=generated_melody_primer.mid"])
subprocess.call(["performance_rnn_generate","--config=performance_with_dynamics", "--bundle_file=./models/performance_with_dynamics.mag", "--output_dir=./generated","--num_outputs=1","--num_steps=10000","--primer_midi=generated_melody_primer.mid"])
subprocess.call(["polyphony_rnn_generate","--bundle_file=./models/polyphony_rnn.mag", "--output_dir=./generated","--num_outputs=1","--num_steps=1000","--primer_midi=generated_melody_primer.mid","--condition_on_primer=true","--inject_primer_during_generation=false"])
"""
