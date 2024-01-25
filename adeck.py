import gzip

with gzip.open(r"C:\Users\deela\Downloads\aal102023.dat.gz", mode="rt") as f:
    file_content = f.read()
    print(file_content)

    f2 = open(r"C:\Users\deela\Downloads\Idalia2023ADeck.txt", 'w')
    f2.write(file_content)
