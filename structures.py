
class Note:
    def __init__(self, key, sus):
        self.key = key
        self.sus = sus

class Span:
    def __init__(self, length, children):
        self.length = length
        self.children = children
    def __iter__(self):
        for child in self.children:
            if isinstance(child, Note):
                yield child
            else:
                yield from iter(child)

def compose(scale, min_meter_level):
    