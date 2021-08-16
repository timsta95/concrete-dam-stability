#--- TO DO ---
#- inheritance: parent class Load
#-------------

from shapely.geometry import (
    Polygon, Point, MultiPoint, LineString, MultiLineString
    )
from shapely.ops import unary_union

from segment import Segment

class Vannvekt:
    """
    Vannvekt: The polygon is created by cutting a larger polygon ('box') with
    the pillar geometry; if the water level is above the crest, an additional
    polygon is added (unary union)
    
    """
    
    def __init__(self, dam, level, g_water = 9.81):
        """
        Parameters
        ----------
        dam : instance of class dam
            
        level : float
            water level,
            unit: masl
        g_water : positive float, optional
            specific weight of water; the default is 9.81,
            unit: kN/m3

        Returns
        -------
        None.

        """
        self.dam = dam
        self.level = level
        self.g_water = g_water
        
    def draw(self):
        """
        Returns
        -------
        vv_list : list
            list of instances of class Segment

        """
        vv_list = []
        for p in self.dam.pillars:
            height = min(p.highest_point().y, self.level)
            box = Polygon([(p.left_contact().x, height),
                           (p.righternmost_x() + 1, height),
                           (p.righternmost_x() + 1, p.left_contact().y),
                           p.left_contact()])
            try:
                poly = box.difference(p.get_union())[0]
            except:
                poly = Polygon(
                    [(p.left_contact().x - 1, p.left_contact().y),
                    p.left_contact(),
                    (p.left_contact().x + 1, p.left_contact().y)]
                    )
            
            if self.level > p.highest_point().y and poly.area > 0:
                poly2 = Polygon([(p.left_contact().x, p.highest_point().y),
                                 (p.left_contact().x, self.level),
                                 (p.highest_point().x, self.level),
                                 p.highest_point()])
                poly = unary_union([poly, poly2])
                
            vv_list.append(
                Segment(
                    poly, p.max_depth(), self.g_water, p.axis(), 'Vannvekt'
                    )
                )
            
        return vv_list
    
    def calc_centroid(self):
        """
        Returns
        -------
        list
            list of centroids/ load-carrying points of instances of class
            Segment,
            length units: m

        """
        return [i.centroid() for i in self.draw()]
    
    def calc_load(self):
        """
        Returns
        -------
        list
            list of loads of instances of class Segment,
            unit: kN/m3

        """
        return [i.load() for i in self.draw()]

class Vanntrykk:
    
    def __init__(self, dam, level, g_water = 9.81): 
        self.dam = dam
        self.level = level
        self.g_water = g_water
        
    def draw(self):
        vt_list = []
        for p in self.dam.pillars:
            left_pt = Point(
                p.left_contact().x - (self.level - p.left_contact().y),
                p.left_contact().y
                )
            poly = Polygon([(p.left_contact().x, self.level),
                            p.left_contact(),
                            left_pt])
            
            if self.level > p.highest_point().y:
                box = Polygon([(left_pt.x, self.level),
                               (p.highest_point().x, self.level),
                               p.highest_point(),
                               (left_pt.x, p.highest_point().y)])
                poly = poly.difference(box)
                
            vt_list.append(
                Segment(
                    poly, p.max_depth(), self.g_water, p.axis(), 'Vanntrykk'
                    )
                )
            
        return vt_list
    
    def calc_centroid(self):
        return [i.centroid() for i in self.draw()]
    
    def calc_load(self):
        return [- i.load() for i in self.draw()]
    
class Opptrykk:
    """
    This class creates a list of instances of the class Segment by incremently
    advancing along the dam sole and measuring the width of the increment
    
    """
    
    def __init__(self, dam, level, g_water = 9.81):
        self.dam = dam
        self.level = level
        self.g_water = g_water
        
    def draw(self):
        increment = 0.05
        op_list = []
        for p in self.dam.pillars:
            left_contact, right_contact = p.left_contact(), p.right_contact()
            y = min(left_contact.y, right_contact.y)
            p0 = (left_contact.x, y - (self.level - left_contact.y))
            segments = []
            surface = p.cutting_surface()
            minx, miny, maxx, maxy = surface.bounds
            line = LineString([(minx, miny), (maxx, miny)])
            count = 0
            new_axis = p.axis() - (maxy - miny) / 2 + increment / 2
            while line.intersects(surface):
                count += 1
                intersec = line.intersection(surface)
                if type(intersec) == LineString:
                    intersec = MultiLineString([intersec])
                if type(intersec) not in (Point, MultiPoint):
                    intersec = intersec[0]
                    p1, p2 = intersec.coords
                    p1_x, p2_x = p1[0], p2[0]
                    p1, p2 = (p1_x, y), (p2_x, y)
                    poly = Polygon([p0, p1, p2])
                    segments.append(
                        Segment(
                            poly, increment, self.g_water, new_axis, 'Opptrykk'
                            )
                        )
                new_y = miny + count * increment
                line = LineString([(minx, new_y), (maxx, new_y)])
                new_axis += increment
            op_list.append(segments)
        return op_list
    
    def calc_centroid(self):
        op_list = self.draw()
        centr_list = []
        for op, pillar in zip(op_list, self.dam.pillars):
            left_y = pillar.left_contact().y
            area_i = [i.area() for i in op]
            x_i = [i.centroid().x for i in op]
            xs = sum([a * b for a, b in zip(area_i, x_i)]) / sum(area_i)
            centr_list.append(Point(xs, left_y))
        return centr_list
    
    def calc_load(self):
        op_list = self.draw()
        load_list = []
        for op in op_list:
            load_list.append(- sum([i.load() for i in op]))
        return load_list
    
class Overtopping:
    
    def __init__(self, dam, level, g_water = 9.81):
        self.dam = dam
        self.level = level
        self.g_water = g_water
        
    def draw(self):
        ov_list = []
        for p in self.dam.pillars:
            highest_point = p.highest_point()
            if self.level > highest_point.y:
                poly = Polygon(
                    [highest_point,
                     (highest_point.x, self.level),
                     (highest_point.x + p.crest_width, highest_point.y)])       
            else:
                poly = Polygon(
                    [highest_point,
                     (highest_point.x + p.crest_width / 2, highest_point.y),
                     (highest_point.x + p.crest_width, highest_point.y)])
            ov_list.append(
                    Segment(
                        poly, p.max_depth(), self.g_water,
                        p.axis(), 'Overtopping'
                        )
                    )
        return ov_list
    
    def calc_centroid(self):
        return [i.centroid() for i in self.draw()]
    
    def calc_load(self):
        return [i.load() for i in self.draw()]
        
class Egenvekt:
    
    def __init__(self, dam):
        self.dam = dam
        
    def draw(self):
        return [p.segments_above() for p in self.dam.pillars]
    
    def calc_centroid(self):
        seg_list = self.draw()
        centr_list = []
        for segs in seg_list:
            load_i = [seg.load() for seg in segs]
            x_i = [seg.centroid().x for seg in segs]
            y_i = [seg.centroid().y for seg in segs]
            xs = sum([l * x for l, x in zip(load_i, x_i)]) / sum(load_i)
            ys = sum([l * y for l, y in zip(load_i, y_i)]) / sum(load_i)
            centr_list.append(
                Point(xs, ys))
        return centr_list
    
    def calc_load(self):
        seg_list = self.draw()
        load_list = []
        for segs in seg_list:
            load_list.append(sum([seg.load() for seg in segs]))
        return load_list
    
class Islast:
    
    def __init__(self, dam, level, ice_load):
        self.dam = dam
        self.level = level
        self.ice_load = ice_load
        
    def draw(self):
        ice_list = []
        for p in self.dam.pillars:
            y = max(p.lowest_point().y, self.level - 0.25)
            x_min = p.left_contact().x
            poly = Polygon(
                [(x_min, y + 0.25),
                 (x_min, y - 0.25),
                 (x_min - 2, y - 0.25),
                 (x_min - 2, y + 0.25)]
                )
            ice_list.append(
                Segment(
                    poly, p.max_depth(), self.ice_load, p.axis(), 'Islast'
                    )
                )
        return ice_list
    
    def calc_centroid(self):
        return [i.centroid() for i in self.draw()]
    
    def calc_load(self):
        return [- i.load() for i in self.draw()]