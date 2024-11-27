

from collections import namedtuple


Shape = namedtuple('Shape', ['class_name', 'xmin', 'ymin', 'xmax', 'ymax', 'difficult', 'feature'])
Shape.__new__.__defaults__ = (0, 0)
# class Shape(shape_tuple):
#     __slots__ = ()
#     def __new__(cls, *args, difficult=0, feature=0):
#         return super().__new__(cls, *args, difficult, feature)

# a = Shape(0,1,2,5,2, feature=2)
# print(a.class_name)