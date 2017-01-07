import sys
import os

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)

# That was all required to make this line work.
# Since we are inside the actual uBlog folder, we can't refer to it by uBlog, unless we add it to the path.
# ...Something about python being elegant until its not...

from uBlog import manager

# This is run when the module is ran with "python -m uBlog"

manager.run()
