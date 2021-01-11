# with

# for message in inport:
#     try:
#         print(message)
#         if message.type == 'control_change':
#             if message.control == 106:
#                 if message.value == 127:
#                     send_lp_cc(106, 62)
#                     if current_instrument > 0:
#                         current_instrument = current_instrument - 1
#                     fluidsynth.set_instrument(1, current_instrument, current_bank)
#                     print('current_instrument ' + str(current_instrument))
#                 else:
#                     send_lp_cc(106, 0)

#             if message.control == 107:
#                 if message.value == 127:
#                     send_lp_cc(107, 62)
#                     if current_instrument < 128:  # TODO: check depend on bank....
#                         current_instrument = current_instrument + 1
#                     fluidsynth.set_instrument(1, current_instrument, current_bank)
#                     print('current_instrument ' + str(current_instrument))
#                 else:
#                     send_lp_cc(107, 0)

#             if message.control == 109 or message.control == 110:
#                 send_lp_cc(modes[MODE], 0)
#                 MODE = message.control - modes[0]
#                 current_bank = 0 if message.control == 109 else 128
#                 # TODO: set current instrument per bank...so you can remember selection when switch....
#                 current_instrument = 0
#                 fluidsynth.set_instrument(1, 0, current_bank)
#                 send_lp_cc(modes[MODE], 62)

#         if message.type == 'note_on':
#             k = message.note % 16
#             print("Received " + str(message.note) + ' - ' + str(k))

#             if (message.note >= 0 and message.note <= 7):
#                 print('change octave ' + str(k))
#                 send_lp_note(octave, 0)
#                 octave = k
#                 send_lp_note(octave, 60)

#             if (message.note >= note_min and message.note <= note_max and k >= 0 and k <= 6):
#                 n = Note(notes[k], octave)
#                 n.channel = 1
#                 n.velocity = 100

#                 if message.velocity == 127:
#                     print('Note ON - octave: ' + str(octave))
#                     fluidsynth.play_Note(n)
#                     send_lp_note(message.note, 63)

#                 else:
#                     print('Note OFF')
#                     fluidsynth.stop_Note(n, n.channel)
#                     send_lp_note(message.note, 62)

#     except Exception as e:
#         print("ERROR", e)
