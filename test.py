uselast = True

def test():
    if uselast:
        print(uselast)
    uselast = False
    print(uselast)

test()