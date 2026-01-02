import google.protobuf as pb
p = pb.__file__
print("FILE:", p)
with open(p, 'r', encoding='utf-8') as f:
    print(f.read())
