import text_to_emotion as utility
import TransProse
import pretty_midi

theText = utility.get_words_from_text("test.txt")

theTheme = TransProse.Theme()

theTheme.generate(theText)

theOutput = theTheme.output()

print(theOutput)
#print(theOutput["tempo"])
#print(theOutput["melodies"])

def gen_midi(melodies, tempo):
    music_gen =  pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program("acoustic grand piano")
    piano = pretty_midi.Instrument(program=piano_program)
    #string_program = pretty_midi.instrument_name_to_program("string ensemble 1")
    #string_ens = pretty_midi.Instrument(program=string_program)
    for melody in melodies:
        runtime = 0
        for n in melody:
            # Retrieve the MIDI note number for this note name
            note_number = pretty_midi.note_name_to_number(n[0])
            length = (60/tempo)*n[1]
            # Create a Note instance, starting at 0s and ending at .5s
            note = pretty_midi.Note(velocity=100, pitch=note_number, start=runtime, end= runtime + length)
            # Add it to our piano instrument
            piano.notes.append(note)
            #string_ens.notes.append(note)
            runtime += length
    # Add the cello instrument to the PrettyMIDI object
    music_gen.instruments.append(piano)
    #music_gen.instruments.append(string_ens)
    # Write out the MIDI data
    music_gen.write('generated_melody_primer.mid')

gen_midi(theOutput["melodies"],60)
