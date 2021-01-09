import sys
import mido
import mingus.core.notes as notes
from mingus.midi import fluidsynth
from mingus.containers import Note

DEVICE = "Launchpad"
SF2 = "sf2/VintageDreamsWaves-v2.sf2"

inport = mido.open_input(DEVICE)
outport = mido.open_output(DEVICE)

octave = 2
note_min = 112
note_max = 118
notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

modes = [109, 110]
current_mode = 0
current_instrument = 0

if not fluidsynth.init(SF2):
    print("Couldn't load soundfont", SF2)
    sys.exit(1)

fluidsynth.set_instrument(1, current_instrument, 0)

with mido.open_output() as outport:
    # RESET LP
    outport.send(mido.Message('control_change', control=0, value=0))
    # SET LED of OCTAVE
    outport.send(mido.Message('note_on', note=octave, velocity=60))

    # CURRENT MODE
    outport.send(mido.Message('control_change', control=modes[current_mode], value=62))

    # SET LED of NOTES
    for x in range(note_min, note_max + 1):
        outport.send(mido.Message('note_on', note=x, velocity=62))

    with mido.open_input() as inport:
        for message in inport:
            try:
                print(message)
                if message.type == 'control_change':
                    if message.control == 106:
                        if message.value == 127:
                            outport.send(mido.Message('control_change', control=106, value=62))
                            if current_instrument > 0:
                                current_instrument = current_instrument - 1
                            fluidsynth.set_instrument(1, current_instrument, 0)
                            print('current_instrument ' + str(current_instrument))
                        else:
                            outport.send(mido.Message('control_change', control=106, value=0))

                    if message.control == 107:
                        if message.value == 127:
                            outport.send(mido.Message('control_change', control=107, value=62))
                            if current_instrument < 128:
                                current_instrument = current_instrument + 1
                            fluidsynth.set_instrument(1, current_instrument, 0)
                            print('current_instrument ' + str(current_instrument))
                        else:
                            print('reset 107')
                            outport.send(mido.Message('control_change', control=107, value=0))

                    if message.control == 109 or message.control == 110:
                        outport.send(mido.Message('control_change', control=modes[current_mode], value=0))
                        current_mode = message.control - modes[0]
                        outport.send(mido.Message('control_change', control=modes[current_mode], value=62))

                if message.type == 'note_on':
                    k = message.note % 16
                    print("Received " + str(message.note) + ' - ' + str(k))

                    if (message.note >= 0 and message.note <= 7):
                        print('change octave ' + str(k))
                        outport.send(mido.Message('note_on', note=octave, velocity=0))
                        octave = k
                        outport.send(mido.Message('note_on', note=octave, velocity=60))

                    if (message.note >= note_min and message.note <= note_max and k >= 0 and k <= 6):
                        n = Note(notes[k], octave)
                        n.channel = 1
                        n.velocity = 100

                        if message.velocity == 127:
                            print('Note ON - octave: ' + str(octave))
                            fluidsynth.play_Note(n)
                            outport.send(mido.Message('note_on', note=message.note, velocity=63))

                        else:
                            print('Note OFF')
                            fluidsynth.stop_Note(n, n.channel)
                            outport.send(mido.Message('note_on', note=message.note, velocity=62))

            except Exception as e:
                print(e)


outport.close()
