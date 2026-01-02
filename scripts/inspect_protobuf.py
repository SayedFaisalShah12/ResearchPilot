import google.protobuf as pb
p = pb.__file__
print("FILE:", p)
with open(p, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 200:
            break
        print(f"{i+1:03}: {line.rstrip()}")
