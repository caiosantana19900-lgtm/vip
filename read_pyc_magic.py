import os, sys
p = r"features\auto_attack.pyc"
if not os.path.exists(p):
    print("Ficheiro não encontrado:", p)
    sys.exit(1)
with open(p,"rb") as f:
    magic = f.read(4)
print("magic bytes hex:", magic.hex())
