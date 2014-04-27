# This has Python look into every subdirectory of this directory when looking
# for packages and modules within this package.
import os
_my_dir = os.path.dirname(__file__)
__path__ += [os.path.join(_my_dir, i) for i in os.listdir(_my_dir)
    if os.path.isdir(os.path.join(_my_dir, i))]
