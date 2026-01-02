import sys, os
pattern = 'from google.protobuf import runtime_version'
for p in sys.path:
    if p and os.path.isdir(p):
        for root, dirs, files in os.walk(p):
            for fn in files:
                if fn.endswith('.py'):
                    fp = os.path.join(root, fn)
                    try:
                        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                            txt = f.read()
                            if pattern in txt:
                                print(fp)
                    except Exception:
                        pass
