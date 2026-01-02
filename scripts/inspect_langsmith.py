p = r"C:\Users\webco\AppData\Local\Programs\Python\Python312\Lib\site-packages\langsmith\env\_runtime_env.py"
print('FILE:', p)
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        if i<200:
            print(f"{i+1:03}: {line.rstrip()}")
        else:
            break
