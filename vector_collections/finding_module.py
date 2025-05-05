import os 
import sys



current_dir = os.path.dirname(os.path.abspath(__file__))

print(current_dir)

parent_dir = os.path.join(current_dir, os.pardir)


grandparent_dir = os.path.join(parent_dir, os.pardir)

print(grandparent_dir)

if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)


current_dir = os.path.dirname(os.path.abspath(__file__))

print(current_dir)
