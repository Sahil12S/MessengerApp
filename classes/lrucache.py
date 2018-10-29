import collections
import time

class Cache:
    def __init__ (self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    # set key-value pair.
    def set (self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last = False)
        self.cache[key] = value


    # display all entries in cache.
    def display(self):
        messages = list(self.cache.values())
        return messages


    def deleteOlder(self, life):
        pop_count = 0
        
        i = 0
        while i < len(self.cache):
            keys = list(self.cache.keys())
            if (time.time() - keys[i]) >= life:
                self.cache.popitem(last = False)
                pop_count += 1
            else:
                break

        return pop_count
