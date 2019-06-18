
class Note:
    def __init__(self, key, time):
        self.key = key
        self.time = time

class HeldNote(Note):
    def __init__(self, key, time, length):
        super().__init__(key, time)
        self.length = length

def note_times(notes):
    for note in notes:
        yield note.time

# composition procedure:
# start with a base position (time 0, metric level 0)