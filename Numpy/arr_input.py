import numpy as np
def arr_input():
    dim=input().strip().split()
    n=int(dim[0])
    if len(dim)==2:
        m=int(dim[1])
    else:
        m=0

    inpt=[]
    for i in range(n):
        inp=input().strip().split()
        inp=[int(z) for z in inp]
        print(inp)
        if len(inp) == m:
            inpt.append(inp)
    arr=np.array(inpt)
    return arr
