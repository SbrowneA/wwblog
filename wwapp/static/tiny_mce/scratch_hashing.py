import hashlib
unencoded= "eyo"
encoded = unencoded.encode('utf-8')

h1 = hashlib.sha224(encoded)
h2 = hashlib.sha224(encoded)
h3 = hashlib.sha224(encoded)
h4 = hashlib.sha224(encoded)

print(h1)
hd = h1.digest()
print(hd)
hd6 = h2.hexdigest()
print(hd6)
print(hd6[:5])


