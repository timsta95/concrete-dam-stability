import load

import math

class Stability:
    """
    Calculate stability coefficients that will be
    evaluated at a following stage (see Evaluation);
    the examined failure modes are sliding and overturning
    """
    def __init__(self, dam, level, ice = 100):
        self.dam = dam
        self.level = level
        self.ice = ice
        
    def basic(self):
        #return list of load instances
        ice = load.Islast(self.dam, self.level, self.ice)
        vt = load.Vanntrykk(self.dam, self.level)
        vv = load.Vannvekt(self.dam, self.level)
        ov = load.Overtopping(self.dam, self.level)    
        op = load.Opptrykk(self.dam, self.level)
        ev = load.Egenvekt(self.dam)
        return [ice, vt, vv, ov, op, ev]
        
    def draw(self):
        #returns a flat list of all segments, information on which pillar each
        #segment belongs to is *NOT* preserved  
        ice, vt, vv, ov, op, ev = [i.draw() for i in self.basic()]
        loads = [ice, vt, vv, ov] + op + ev
        
        seg_list = []
        for l in loads:
            [seg_list.append(s) for s in l]
        return seg_list
    
    def draw_per_pillar(self):
        #returns a nested list of segments, structured by which pillar the
        #segments belong to
        ice, vt, vv, ov, op, ev = [i.draw() for i in self.basic()]
        
        rearranged = []
        for ice_i, vt_i, vv_i, ov_i, op_i, ev_i in zip(
                ice, vt, vv, ov, op, ev
                ):
            rearranged.append([ice_i, vt_i, vv_i, ov_i] + op_i + ev_i)
        return rearranged
    
    def loads(self):
        return [i.calc_load() for i in self.basic()]
    
    def horizontal_loads(self):
        ice_load, vt_load, vv_load, ov_load, op_load, ev_load = self.loads()     
        return [ice + vt for ice, vt in zip(ice_load, vt_load)]
    
    def vertical_loads(self):
        ice_load, vt_load, vv_load, ov_load, op_load, ev_load = self.loads()     
        return [vv + ov + op + ev for vv, ov, op, ev in zip(
            vv_load, ov_load, op_load, ev_load
            )]
    
    def moment(self):
        pt_list = [p.right_contact() for p in self.dam.pillars]
        
        ice_load, vt_load, vv_load, ov_load, op_load, ev_load = self.loads()
        
        ice_c, vt_c, vv_c, ov_c, op_c, ev_c = [i.calc_centroid() for i in self.basic()]
        
        m_lists = []
        for idx, pt in enumerate(pt_list):
            ice_m = ice_load[idx] * (ice_c[idx].y - pt.y)
            vt_m = vt_load[idx] * (vt_c[idx].y - pt.y)
            vv_m = vv_load[idx] * (pt.x - vv_c[idx].x)
            ov_m = ov_load[idx] * (pt.x - ov_c[idx].x)
            op_m = op_load[idx] * (pt.x - op_c[idx].x)
            ev_m = ev_load[idx] * (pt.x - ev_c[idx].x)
            
            m_lists.append([ice_m, vt_m, vv_m, ov_m, op_m, ev_m])
        return m_lists
    
    def glidning(self):
        alpha_list = [p.bottom_angle() for p in self.dam.pillars]
        phi_list = [p.phi for p in self.dam.pillars]

        ice_load, vt_load, vv_load, ov_load, op_load, ev_load = self.loads()
        
        glidning_list = []
        for (alpha, phi, ice, vt, vv, ov, op, ev) in zip(
                alpha_list, phi_list, ice_load, vt_load,
                vv_load, ov_load, op_load, ev_load
                ):
            fh = ice + vt
            fv = vv + ov + op + ev
            glidning_list.append(
                abs((fv * math.tan(math.radians(phi + alpha))) / fh)
                )
        return glidning_list
    
    def velting_resultant(self):
        m_lists = self.moment()
        fh_list = self.horizontal_loads()
        fv_list = self.vertical_loads()
        return [sum(m) / math.sqrt(fh**2 + fv**2) for m, fh, fv in zip(
            m_lists, fh_list, fv_list
            )]
    
    def velting_moment(self):
        m_lists = self.moment()
        s_list = []
        for m_list in m_lists:
            m_pos = sum([m for m in m_list if m >= 0])
            m_neg = sum([m for m in m_list if m < 0])
            s_list.append(abs(m_pos / m_neg)) 
        return s_list      