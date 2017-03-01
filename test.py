import math
import play

def a(t):
  return math.sin(t*440*2*math.pi)*0.5

if __name__ == '__main__':
  play.play(a)