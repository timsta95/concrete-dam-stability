import segment, pillar, dam

from shapely.geometry import Polygon

"""
This script is used to define the dam construction.
The script expects a list of pillars to be passed to a Dam instance and a list
of water levels (HRV, DFV, MFV). See pillar.py for definition of pillars.
"""

axis = 5 #axis length [m]
concrete = 23.54 #specific weight concrete [kn/m3]
width_pilar = 2. #pillar width [m]
phi = 50 #friction angle [deg]
width_cr = 0.5 #width of dam crest [m]

#example dam geometries
plate_poly = Polygon(((0, 0), (5, 5), (5, 5.8), (5.5, 5.8), (5.5, 5.5),(5.2, 5.5), (5.2, 4.8), (1, 0)))
pilar_poly = Polygon(((1, 0), (5.2, 4.8), (5.2, 5.5), (5.5, 5.5), (5.5, 4.5), (8, 0)))

#example contact points dam - rock (left = upstream, right =  downstream)
left = (0.2, 0.25)
right = (1, 1.5)

#dam type (gravity dam/ buttress dam)
dam_type = 'Platedam'
#create volumes of first dam section
plate1 = segment.Segment(plate_poly, axis, concrete, 0, 'Plate1')
pilar1 = segment.Segment(pilar_poly, width_pilar, concrete, 0, 'Pilar1')
section1 = pillar.Pillar([plate1, pilar1], left[0], right[0], width_cr, phi, dam_type, 'Section 1')
#create volumes of second dam section
plate2 = segment.Segment(plate_poly, axis, concrete, 5, 'Plate2')
pilar2 = segment.Segment(pilar_poly, width_pilar, concrete, 5, 'Pilar2')
section2 = pillar.Pillar([plate2, pilar2], left[1], right[1], width_cr, phi, dam_type, 'Section 2')
#build dam from sections
dam_construction = dam.Dam([section1, section2])

#define water levels
levels = [4, 5, 6]