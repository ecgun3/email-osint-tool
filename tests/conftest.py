#confest.py --> It adds the root directory so that tests can import modules in the project without any problems.

import sys
import os

# Projenin kök dizinini (email-osint-tool) sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
