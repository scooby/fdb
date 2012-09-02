        queue = coll.deque([op.abspath(top)])
        while queue:
            path = queue.popleft()
            if op.islink(path):
                continue
            elif op.isdir(path):
                try:
                    listing = [op.join(path, ent) for ent in os.listdir(path)]
                    listing.sort(key=lambda ent: op.join(ent, '') if op.isdir(ent) else ent)
                    listing.reverse()
                    queue.extendleft(listing)
                except IOError:
                    pass
            elif op.isfile(path):
                rs = os.stat(path)
