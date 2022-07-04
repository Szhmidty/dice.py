from functools import lru_cache, reduce
import operator as op
import timeit

@lru_cache(1000000)
def simplexVolume(dim: int, n: int):
    """
    simplexVolume(dim: int, n: int)

    Calculates the the nth simplical number of dimension dim 

    By analogy, this function returns the volume of a simplex of dimension dim
    made up of unit cubes
    """
    if dim < 1 or n < 1:
        return 0
    p = 1
    for it in range(dim):
        p *= (n + it)/(it + 1)
    return p

@lru_cache(1000000)
def truncatedSimplexVolume(constraints, n, dim = None):
    """
    truncatedSimplexVolume(constraints, n, dim = None)

    Calculates the volume of a truncated simplex of size n and dimension dim by
    truncating the simplex at the boundaries defined by the tuple constraints

    if dim is not set, it is assumed to be the length of the constraints iterable

    e.g. truncatedSimplexVolume([3,4,5], 10) will calculate a 3d simplex of size 10
    (i.e. it will call simplexVolume(3,10)) and then eliminate all volume that extends
    beyond X<=3, Y<=4, Z<=5 i.e. it will be truncated to fit within a rectangular prism
    of length 3, width 4, and height 5. 

    Note that constraints should be a tuple, this function is cached and all inputs
    must be hashable
    """
    if dim is None:
        dim = len(constraints)

    # start with the full volume for a simplex of dimension dim and size n
    volume = simplexVolume(dim, n)
    
    # for each constraint, subtract off the protrusion along a given dimension
    # eliminating a constraint at each step
    for it in range(len(constraints)):
        volume -= truncatedSimplexVolume(constraints[it+1:], n-constraints[it], dim)
    return volume

def symmetricalTruncatedSimplexVolume(numberOfConstraints, constraint, n, dim = None):
    """
    symmetricalTruncatedSimplexVolume(numberOfConstraints, constraint, n, dim = None)

    Calculates the volume of a truncated simplex of size n and dimension dim by
    truncating the simplex at the boundaries defined by the number of constraints
    and the constraint value

    This function behaves similarly to truncatedSimplexVolume, however this function
    assumes the constraint of each dimension is the same, and so instead takes the number
    of constrained dimensions and the size of the constraint

    This particular case can be heavily optimized, and so runs much quicker than the general
    case

    if dim is not set, it is assumed to be the same as numberOfConstraints

    e.g. symmetricalTruncatedSimplexVolume(3,5,10) will calculate a 3d simplex of size 10
    (i.e. it will call simplexVolume(3,10)) and then eliminate all volume that extends
    beyond X<=5, Y<=5, Z<=5 i.e. it will be truncated to fit within a cube of size 5
    """
    
    if dim is None:
        dim = numberOfConstraints
    pos = n // constraint
    s = 0
    for it in range(pos + 1):
        s += ((-1)**it)*simplexVolume(numberOfConstraints-it,it+1)*simplexVolume(dim,n - it*constraint)
    return s


def diceRollProbability(dice, roll, distribution = "exact roll"):
    """
    diceRollProbability(dice, roll, distribution = "exact roll")

    calculates the probability of a particular roll from a set of dice

    dice should be an iterable of integers, roll should be an iterable

    multiple distribution types are supported, namely the probablility of
    the "exact roll", "at most", "at least", "less than", or "more than"

    e.g. diceRollProbability([6,6,6], 17, distribution = "exact roll") will
    calculate the probability of getting a 17 from rolling 3 6-sided dice 
    numbered 1 to 6 (3 in 216)

    diceRollProbability([6,6,6], 17, distribution = "more than") will 
    calculate the probability of getting more than 17 from rolling 3 6-sided 
    dice numbered 1 to 6 (1 in 216) 
    """
    totalVolume = reduce(op.mul, dice)
    minimumRoll = numberOfDice = len(dice)
    maximumRoll = sum(dice)
    # adjusts the size and dimension of the required simplex based on the distribution;
    # the way the underlying functions are constructed, it's easiest to think of the values
    # as being in terms of the "at most" distribution; the "exact roll" distribution has the
    # same roll but lower dimension than "at most"; "less than" shifts the roll down by 1, etc
    match distribution:
        case "exact roll":
            dim = len(dice)-1
        case "at most":
            dim = len(dice)
        case "less than":
            dim = len(dice)
            roll = roll - 1
        case "more than":
            dim = len(dice)
            roll = maximumRoll + minimumRoll - roll - 1
        case "at least":
            dim = len(dice)
            roll = maximumRoll + minimumRoll - roll
        case _:
            raise ValueError('distribrution must be either "exact roll", "at most", "less than","more than", or "at least"')

    # checks if the dice are all the same size; this case is optimized to be much faster
    allSame = True
    for it in range(1,len(dice)):
        if dice[it] != dice[it-1]:
            allSame = False
            break
    
    if allSame:
        return symmetricalTruncatedSimplexVolume(numberOfDice, dice[0], roll - numberOfDice + 1, dim)/totalVolume
    else:
        return truncatedSimplexVolume(dice, roll - numberOfDice + 1, dim)/totalVolume

size = 100
dice_list = tuple(range(1,size+1))

if __name__ == "__main__":

    time = timeit.timeit(
        stmt='[diceRollProbability(dice_list,it) for it in range(size, size*(size+1)//2)]',
        number = 1,
        setup = "from __main__ import diceRollProbability, dice_list, size"
    )
    # timing a single iteration is generally bad practice, but with a cached function it's necessary:
    # the later iterations have the benefit of the cache so it doesn't reflect how long it takes
    # fo run the code from "cold"

    print("using simplical numbers for all probabilities rolling 1d1 + 1d2 + 1d3+...+1d100:",
        f'{time*1000:.3f}',
        'ms'
    )

    time = timeit.timeit(
        stmt='[diceRollProbability([size]*size,it) for it in range(size, size*size+1)]',
        number = 1,
        setup = "from __main__ import diceRollProbability, dice_list, size"
    )

    print("using simplical numbers for all probabilities rolling 100d100:",
        f'{time*1000:.3f}',
        'ms'
    )


    values_atMost = [diceRollProbability((2,4,6,7,9),it, "at most") for it in range(5,30 + 1)]
    values_Exact = [diceRollProbability((2,4,6,7,9),it, "exact roll") for it in range(5,30 + 1)]
    values_lessThan = [diceRollProbability((2,4,6,7,9),it, "less than") for it in range(5,30 + 1)]
    values_moreThan = [diceRollProbability((2,4,6,7,9),it, "more than") for it in range(5,30 + 1)]
    values_atLeast = [diceRollProbability((2,4,6,7,9),it, "at least") for it in range(5,30 + 1)]
    # values taken from the "normal" (exact roll), "at most", and "at least", distributions for 1d2 + 1d4 + 1d6 + 1d7 + 1d9 on anydice

    anydice_values = [
        # exact         at least        at most
        [0,             100,            0],
        [0.033068783,	100,	        0.033068783],
        [0.165343915,	99.96693122,	0.198412698],
        [0.462962963,	99.8015873,	    0.661375661],
        [0.992063492,	99.33862434,	1.653439153],
        [1.785714286,	98.34656085,	3.439153439],
        [2.843915344,	96.56084656,	6.283068783],
        [4.133597884,	93.71693122,	10.41666667],
        [5.555555556,	89.58333333,	15.97222222],
        [6.977513228,	84.02777778,	22.94973545],
        [8.234126984,	77.05026455,	31.18386243],
        [9.16005291,	68.81613757,	40.34391534],
        [9.656084656,	59.65608466,	50],
        [9.656084656,	50,	            59.65608466],
        [9.16005291,	40.34391534,	68.81613757],
        [8.234126984,	31.18386243,	77.05026455],
        [6.977513228,	22.94973545,	84.02777778],
        [5.555555556,	15.97222222,	89.58333333],
        [4.133597884,	10.41666667,	93.71693122],
        [2.843915344,	6.283068783,	96.56084656],
        [1.785714286,	3.439153439,	98.34656085],
        [0.992063492,	1.653439153,	99.33862434],
        [0.462962963,	0.661375661,	99.8015873],
        [0.165343915,	0.198412698,	99.96693122],
        [0.033068783,	0.033068783,	100],
        [0,             0,              100]
        ]
    print('\nLooking at every possibility for 1d2 + 1d4 + 1d6 + 1d7 + 1d9  for multiple distributions:\n')
    print('\t(EXACT ROLL)\t\t\t(AT LEAST)\t\t\t(AT MOST)\t\t\t(MORE THAN)\t\t\t(LESS THAN)')
    print('roll\tsimplex\t\tanydice','\tsimplex\t\tanydice','\tsimplex\t\tanydice','\tsimplex\t\tanydice','\tsimplex\t\tanydice' )
    for it in range(5,29):
        print(f"{it}\t",
        f"{values_Exact[it-5]:.5f}\t",f"{anydice_values[it-4][0]/100:.5f}\t",       # exact columns
        f"{values_atLeast[it-5]:.5f}\t",f"{anydice_values[it-4][1]/100:.5f}\t",     # at least columns
        f"{values_atMost[it-5]:.5f}\t",f"{anydice_values[it-4][2]/100:.5f}\t",      # at most columns
        f"{values_moreThan[it-5]:.5f}\t",f"{anydice_values[it-3][1]/100:.5f}\t",    # more than columns
        f"{values_lessThan[it-5]:.5f}\t",f"{anydice_values[it-5][2]/100:.5f}\t")    # less than columns
