# this file should never import anything from discoship
import os

DEFAULT_PROVIDER = "usps"
DEFAULT_SERVICE = "fcpis"

with open(os.path.sep.join([os.path.dirname(__file__), 'VERSION']), 'r') as fh:
    VERSION = fh.read().strip()

