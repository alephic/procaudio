import rtmidi
import play
import notes
import oscillators

def midi_play(base_osc, attack, decay):
    midi_in = rtmidi.MidiIn()
    ports = midi_in.get_ports()

    for i, port in enumerate(ports):
        if 'Through' not in port:
            print("Opening midi port:", port)
            midi_in.open_port(i)

    gen = notes.NoteGen(base_osc, attack, decay)

    def callback(evt, data):
        print(evt)
        if evt[0][0] == 144:
            gen.play_note(evt[0][1])
        elif evt[0][0] == 128:
            gen.kill_note(evt[0][1])

    midi_in.set_callback(callback)
    play.play_unbuffered(gen)
    midi_in.close_port()
    del midi_in

if __name__ == "__main__":
    midi_play(oscillators.Scaled(0.5, oscillators.Sine(440)), 0.01, 0.1)