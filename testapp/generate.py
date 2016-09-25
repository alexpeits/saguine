import os
import sys
sys.path.append('./')
sys.path.append('../')

from saguine.engine import init_site, create_base, generate

HERE = os.path.abspath(os.path.dirname(__file__))

init_site(HERE)
create_base(HERE)
generate(HERE)
