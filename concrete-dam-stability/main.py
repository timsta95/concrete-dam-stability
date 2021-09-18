from segment import Segment
from pillar import Pillar
from dam import Dam
import load
from shapely.geometry import Polygon

from timeit import default_timer as timer

p1 = Polygon(((0,0), (5,5), (5,0)))
p2 = Polygon(((5,0), (5,5), (6,5), (10,0)))
seg1 = Segment(p1, 4, 20, 0, 'seg1')
seg2 = Segment(p2, 2, 20, 0, 'seg2')
seg3 = Segment(p1, 4, 20, 4, 'seg3')
seg4 = Segment(p2, 2, 20, 4, 'seg4')
pillar1 = Pillar([seg1, seg2], 0, 3, 1, 50, 'pl', 'pillar1')
pillar2 = Pillar([seg3, seg4], 0, 3, 1, 50, 'pl', 'pillar2')
dam = Dam([pillar1, pillar2])
start = timer()
for i in range(100):
    ld = load.Islast(dam, 6, 100)
    lds = ld.loads
    ctr = ld.centroids
end = timer()
print(round(end - start, 5))
print(lds)
print('finished')