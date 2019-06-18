from collections import deque

def transpose_iter(it):
    it = iter(it)
    try:
        init_tuple = next(it)
    except StopIteration:
        return tuple()
    ds = tuple(deque([x]) for x in init_tuple)
    def _itrans_sub(d):
        while True:
            if len(d) > 0:
                yield d.popleft()
            else:
                try:
                    t = next(it)
                except StopIteration:
                    return
                for d2, x in zip(ds, t):
                    d2.append(x)
    return tuple(map(_itrans_sub, ds))

def clone_iter(it, n):
    it = iter(it)
    ds = tuple(deque() for _ in range(n))
    def _irepl_sub(d):
        while True:
            if len(d) > 0:
                yield d.popleft()
            else:
                try:
                    x = next(it)
                except StopIteration:
                    return
                for d2 in ds:
                    d2.append(x)
    return tuple(map(_irepl_sub, ds))