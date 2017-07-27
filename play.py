#!/usr/bin/env python3
import argparse
import queue
import sys
import threading
import sounddevice as sd
import numpy as np
import traceback as tb

def block(gen, blocksize, t0, samplerate):
  ar = np.zeros((blocksize,1))
  for i in range(blocksize):
    ar[i, 0] = gen.amp((i+t0) / samplerate)
  return ar

def play(gen, buffersize=20, blocksize=2048, samplerate=44100):

  q = queue.Queue(maxsize=buffersize)
  event = threading.Event()

  def callback(outdata, frames, time, status):
    assert frames == blocksize
    if status.output_underflow:
      print('Output underflow: increase blocksize?', file=sys.stderr)
      raise sd.CallbackAbort
    assert not status
    try:
      data = q.get_nowait()
    except queue.Empty:
      print('Buffer is empty: increase buffersize?', file=sys.stderr)
      raise sd.CallbackAbort
    if len(data) < len(outdata):
      outdata[:len(data)] = data
      outdata[len(data):] = 0
      raise sd.CallbackStop
    else:
      outdata[:] = data

  try:
    t = 0
    for _ in range(buffersize):
      q.put_nowait(block(gen, blocksize, t, samplerate))  # Pre-fill queue
      t += blocksize
    
    stream = sd.OutputStream(
        samplerate=samplerate, blocksize=blocksize,
        device=sd.default.device, channels=1, dtype='float32',
        callback=callback, finished_callback=event.set)

    with stream:
      timeout = blocksize * buffersize / samplerate
      while True:
        q.put(block(gen, blocksize, t, samplerate), timeout=timeout)
        t += blocksize
      event.wait()  # Wait until playback is finished
  except KeyboardInterrupt:
      print('\nInterrupted by user', file=sys.stderr)
  except queue.Full:
      # A timeout occured, i.e. there was an error in the callback
      print('Queue timeout (error in OutputStream callback)', file=sys.stderr)
  except Exception as e:
      tb.print_exc()

def play_unbuffered(gen, blocksize=1024, samplerate=44100):
  t = 0
  def callback(outdata, frames, time, status):
    nonlocal t
    nonlocal gen
    if status:
      print(status)
    for i in range(blocksize):
      outdata[i, 0] = gen.amp((t+i)/samplerate)
    t += blocksize
  try:
    stream = sd.OutputStream(
      samplerate=samplerate, blocksize=blocksize,
      device=sd.default.device, channels=1, dtype='float32',
      callback=callback
    )
    with stream:
      threading.Event().wait()
  except KeyboardInterrupt:
    return
  except Exception as e:
    tb.print_exc()
