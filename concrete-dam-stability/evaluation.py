import os
from dataclasses import dataclass
from functools import cached_property
import pandas as pd
import stability as stb
from dam import Dam

HEADER = ['Sikkerhet mot','Lasttilfelle', 'Damseksjon', 
          'Sikkherhetsfaktor', 'Sikkerhetskrav', 'Stabilitet']

BUTTRESS = 'Platedam'
GRAVITY = 'Gravitasjonsdam'

GL = 'Glidning'
VE = 'Velting'

LEVELS = ('HRV + is', 'DFV', 'MFV')

OK = 'ok'
NOT_OK = 'ikke ok'

ICE_LOAD = 100

GL_DICT = {GRAVITY: (1.5, 1.5, 1.1), BUTTRESS: (1.4, 1.4, 1.1)}
VE_DICT = {GRAVITY: (1/12, 1/12, 1/6), BUTTRESS: (1.4, 1.4, 1.3)}

class SortedLevels:

    ice_loads = (ICE_LOAD, 0, 0)
    
    @property
    def sorted_levels(self):
        return sorted(self.levels)

    @staticmethod
    def compare(value, threshold1, threshold2 = None):
        if threshold2:
            if value >= threshold1 and value <= threshold2:
                return OK
            else:
                return NOT_OK
        else:
            if value >= threshold1:
                return OK
            else:
                return NOT_OK

@dataclass
class Evaluation(SortedLevels):
    dam: Dam
    levels: list

    @cached_property
    def stability(self):
        return [stb.Stability(self.dam, level, ice) for level, ice in zip(
            self.sorted_levels, self.ice_loads)]

    @property
    def glidning(self):
        gl_list = [i.glidning for i in self.stability]
        results = []
        for idx, (gl, name) in enumerate(zip(gl_list, LEVELS)):
            for gl_i, p in zip(gl, self.dam.pillars):
                safety = GL_DICT[p.dam_type][idx]
                result = self.compare(gl_i, safety)
                results.append([
                    GL, name, p.name, round(gl_i, 2), safety, result])
        return results

    @property
    def velting(self):
        vm_list, vr_list = zip(
            *[(i.velting_moment, i.velting_resultant) for i in self.stability])
        results = []
        for idx, (vm, vr, name) in enumerate(zip(vm_list, vr_list, LEVELS)):
            for vm_i, vr_i, p in zip(vm, vr, self.dam.pillars):
                safety = VE_DICT[p.dam_type][idx]
                if p.dam_type == GRAVITY:
                    v_i = vr_i
                    dist = p.right_contact.x - p.left_contact.x
                    min_dist = dist * safety
                    max_dist = dist - min_dist
                    result = self.compare(v_i, min_dist, max_dist)
                elif p.dam_type == BUTTRESS:
                    v_i = vm_i
                    result = self.compare(v_i, safety)
                results.append([
                    VE, name, p.name, round(v_i, 2), safety, result])
        return results     