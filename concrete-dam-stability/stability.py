import math
from dataclasses import dataclass
from functools import cached_property
from load import Islast, Vanntrykk, Vannvekt, Overtopping, Opptrykk, Egenvekt
from dam import Dam

@dataclass
class Stability:
    dam: Dam
    level: float
    ice: float = 100

    @cached_property
    def basic(self):
        ice = Islast(self.dam, self.level, self.ice)
        vt = Vanntrykk(self.dam, self.level)
        vv = Vannvekt(self.dam, self.level)
        ov = Overtopping(self.dam, self.level)
        op = Opptrykk(self.dam, self.level)
        ev = Egenvekt(self.dam)
        return [ice, vt, vv, ov, op, ev]

    @cached_property
    def basic_segments(self):
        return [i.segments for i in self.basic]

    @property
    def segments(self): #formally draw()
        ice, vt, vv, ov, op, ev = self.basic_segments
        loads = [ice, vt, vv, ov] + op + ev
        return [s for l in loads for s in l]

    @property
    def segments_per_pillar(self): #formally draw_per_pillar()
        zipped = zip(self.basic_segments)
        return [[ice, vt, vv, ov] + op + ev for ice, vt, vv, ov, op, ev in zipped]

    @cached_property
    def loads(self):
        return [i.loads for i in self.basic]

    @property
    def horizontal_loads(self):
        ice, vt, _, _, _, _ = self.loads
        return [a + b for a, b in zip(ice, vt)]

    @property
    def vertical_loads(self):
        _, _, vv, ov, op, ev = self.loads
        return [a + b + c + d for a, b, c, d in zip(vv, ov, op, ev)]

    @cached_property
    def moment(self):
        pass

    @property
    def glidning(self):
        pass

    @property
    def velting_resultant(self):
        pass

    @property
    def velting_moment(self):
        pass



    


