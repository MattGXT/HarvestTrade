def read():
    dict = {}
    with open('./src/dict.txt', encoding='utf-8') as f:
        contents = f.readlines()
    for line in contents:
        if line != "\n":
            s = line.split(" ",1)
            key = s[0]
            value = s[1]
            dict[key] = value
    return dict