import os
import sys
sys.path.append('./')
sys.path.append('../')

from saguine.engine import generate

HERE = os.path.abspath(os.path.dirname(__file__))

generate(HERE)
