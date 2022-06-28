from functools import lru_cache
import timeit

@lru_cache(50000)
def simplical_number(n,x):
    if n < 0 and x < 0:
        return 0
    p = 1
    for it in range(n):
        p *= (x + it)/(it + 1)
    return p

@lru_cache(50000)
def pascal(row:int, col:int) -> int:
    if row<0:
        return 0
    if col>row:
        return 0
    if row==0 and col==0:
        return 1

    return pascal(row - 1, col) + pascal(row - 1, col - 1)

def dice_roll_probability_at_most_pascal(n: int, N: int, roll:int) -> float:
    roll = roll - n
    pos = roll // N # which stage of adding/substracting simplex volumes we've reached
                    # strictly speaking not necessary, we can simply define pascal/simplica_number
                    # as being 0 for negative/out of scope inputs, but this saves us from having to
                    # even call the function for those inputs/save them to the cache
    s = 0
    for it in range(pos + 1):
        s += ((-1)**it) * pascal(n,it) * pascal(roll + n - it*N , roll - it*N)
    return s/N**n

def dice_roll_probability_at_most_simplical(n: int, N: int, roll:int) -> float:
    roll = roll - n
    pos = roll // N
    s = 0
    for it in range(pos + 1):
        s += ((-1)**it)*simplical_number(n-it,it+1)*simplical_number(n,roll +1 - it*N)
    return s/N**n
if __name__ == "__main__":
    print('\n')
    simplical_time = timeit.timeit(
        stmt='[dice_roll_probability_at_most_simplical(100,100,it) for it in range(100,100*100+1)]',
        number = 1,
        setup = "from __main__ import dice_roll_probability_at_most_simplical"
    )

    pascal_time = timeit.timeit(
        stmt='[dice_roll_probability_at_most_pascal(100,100,it) for it in range(100,100*100+1)]',
        number = 1,
        setup = "from __main__ import dice_roll_probability_at_most_pascal"
    )

    print("using simplical numbers for all probabilities rolling 100d100:",
        f'{simplical_time*1000:.3f}',
        'ms'
    )

    print("using pascal for all probabilities rolling 100d100:",
        f'{pascal_time*1000:.3f}',
        'ms'
    )

    print('\n')

    pascal_values = [dice_roll_probability_at_most_pascal(5,6,it) for it in range(5,30 + 1)]
    simplical_values =  [dice_roll_probability_at_most_simplical(5,6,it) for it in range(5,30 + 1)]
    # values taken from the "at most" distribution for 5d6 on anydice
    anydice_values = [
        0.0128600823045,
        0.07716049382710001,
        0.2700617283951,
        0.7201646090531,
        1.6203703703701,
        3.2407407407401,
        5.8770576131701,
        9.7993827160501,
        15.2006172839501,
        22.1450617283901,
        30.5169753086401,
        39.9691358024701,
        49.9999999999701,
        60.0308641974701,
        69.4830246913001,
        77.8549382715501,
        84.79938271599009,
        90.2006172838901,
        94.12294238677009,
        96.75925925920009,
        98.37962962957009,
        99.27983539088709,
        99.72993827154508,
        99.92283950611308,
        99.98713991763567,
        99.99999999994017]
    print('roll\t\tpascal\t\tsimplex\t\tanydice')
    for it in range(5,31):
        print(f'{it}\t\t{pascal_values[it-5]:.5f}\t\t{simplical_values[it-5]:.5f}\t\t{anydice_values[it-5]/100:.5f}')



