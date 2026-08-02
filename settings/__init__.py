import sys
import os

# Adiciona o diretório atual (a própria pasta features) ao sys.path 
# permitindo que os arquivos internos se encontrem sem alterar o código original
_features_dir = os.path.dirname(os.path.abspath(__file__))
if _features_dir not in sys.path:
    sys.path.insert(0, _features_dir)