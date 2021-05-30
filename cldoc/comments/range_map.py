import bisect

from util.Struct import Struct
from comments.sorted import Sorted


class RangeMap(Sorted):
    Item = Struct.define('Item', obj=None, start=0, end=0)

    def __init__(self):
        super(RangeMap, self).__init__(key=lambda x: x.start)

        self.stack = []

    def push(self, obj, start):
        self.stack.append(RangeMap.Item(obj=obj, start=start, end=start))

    def pop(self, end):
        item = self.stack.pop()
        item.end = end

        self.insert(item)

    def insert(self, item, start=None, end=None):
        if not isinstance(item, RangeMap.Item):
            item = RangeMap.Item(obj=item, start=start, end=end)

        self.insert_right(item)

    def find(self, i):
        # Finds object for which i falls in the range of that object
        idx = bisect.bisect_right(self.keys, i)

        # Go back up until falls within end
        while idx > 0:
            idx -= 1

            o = self[idx]

            if i <= o.end:
                return o.obj

        return None
