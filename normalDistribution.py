import random
import math

uselast = True
next_gaussian = 0.0

def boxMullerHelper():
    global uselast
    global next_gaussian
    if uselast==True:
        uselast = False
        return next_gaussian
    else:
        while(True):
            v1 = 2.0 * random.uniform(0.0, 1.0) - 1.0
            v2 = 2.0 * random.uniform(0.0, 1.0) - 1.0
            s = v1*v1 + v2*v2
            if  (s>=1.0 or s==0):
                continue
            else:
                break
        
        s = math.sqrt(s/(math.log(s)*-2.0))
        next_gaussian = v2*s
        uselast = True
        return v1*s
def boxMuller(mean, standard_deviation):
    return mean + boxMullerHelper()*standard_deviation

def normalNumber(min, max):
    deviations = 0.3
    while (True):
        mn = min + (max - min) / 2.0
        sd = (max - min) / (2.0 * deviations)
        r = int(boxMuller(mean=mn, standard_deviation=sd))
        if (r>max or r<min):
            continue
        else:
            break
    return r
if __name__ == '__main__':

    for i in range(0,10):
        x = normalNumber(2,4)
        print(x)