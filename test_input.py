import sys, traceback
sys.path.insert(0, r'.')

modules = [
    'features.auto_attack',
    'features.template_matcher',
    'features.auto_skill',
    'features.auto_potion'
]

for m in modules:
    try:
        mod = __import__(m, fromlist=['*'])
        print(f'IMPORT OK: {m} ->', getattr(mod, '__file__', 'no __file__'))
    except Exception as e:
        print(f'IMPORT FAILED: {m} ->', type(e).__name__, e)
        traceback.print_exc()