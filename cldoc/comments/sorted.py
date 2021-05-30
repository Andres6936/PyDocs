# This module provides support for maintaining a list in sorted order without
# having to sort the list after each insertion. For long lists of items with
# expensive comparison operations, this can be an improvement over the more
# common approach. The module is called bisect because it uses a basic
# bisection algorithm to do its work. The source code may be most useful as
# a working example of the algorithm (the boundary conditions are already
# right!).
import bisect


class Sorted(list):
    def __init__(self, key=None):
        super().__init__()
        if key is None:
            key = lambda x: x

        self.keys = []
        self.key = key

    def insert_bisect(self, item, bi):
        k = self.key(item)
        idx = bi(self.keys, k)

        self.keys.insert(idx, k)
        return super(Sorted, self).insert(idx, item)

    def insert(self, item):
        return self.insert_bisect(item, bisect.bisect_left)

    insert_left = insert

    def insert_right(self, item):
        return self.insert_bisect(item, bisect.bisect_right)

    def bisect(self, item, bi):
        k = self.key(item)

        return bi(self.keys, k)

    def bisect_left(self, item):
        return self.bisect(item, bisect.bisect_left)

    def bisect_right(self, item):
        return self.bisect(item, bisect.bisect_right)

    def find(self, key):
        i = bisect.bisect_left(self.keys, key)

        if i != len(self.keys) and self.keys[i] == key:
            return self[i]
        else:
            return None
