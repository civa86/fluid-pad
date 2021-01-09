import sys
import mido
import mingus.core.notes as notes
from mingus.midi import fluidsynth
from mingus.containers import Note

DEVICE = "Launchpad"
SF2 = "sf2/VintageDreamsWaves-v2.sf2"

inport = mido.open_input(DEVICE)
outport = mido.open_output(DEVICE)

if not fluidsynth.init(SF2):
    print("Couldn't load soundfont", SF2)
    sys.exit(1)

fluidsynth.set_instrument(0, 127, 0)

with mido.open_output('Launchpad') as outport:
    outport.send(mido.Message('control_change', control=0, value=1))

    with mido.open_input() as inport:
        for message in inport:
            try:
                print(message)
                nn = message.note
                if message.velocity == 127:
                    fluidsynth.play_Note(nn, 0, 100)
                else:
                    fluidsynth.stop_Note(nn, 0)

            except Exception as e:
                print(e)


outport.close()
