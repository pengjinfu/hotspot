import hotspot.get_hotspot


builders = [i for i in dir(hotspot.get_hotspot) if i.endswith('Builder') and i != 'Builder']


# Using this way to auto injection task.
for item in builders:
    cls = getattr(hotspot.get_hotspot, item)
    cls.register()
