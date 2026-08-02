import marshal
import types
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# ===== SUBSTITUA POR ESTE BLOCO =====

if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.join(os.path.dirname(sys.executable), "_internal"))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pyc_path = os.path.join(BASE_DIR, "main.pyc")

with open(pyc_path, "rb") as f:
    f.read(16)
    code = marshal.load(f)

# ===== FIM DO BLOCO =====

globals_dict = {
    "__name__": "__main__",
    "__file__": pyc_path,
    "__package__": None,
    "__builtins__": __builtins__,
}

exec(code, globals_dict)