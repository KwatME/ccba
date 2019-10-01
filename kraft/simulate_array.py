from numpy import arange, prod
from numpy.random import normal, randint, sample


def simulate_array(shape, how):

    if how == "uniform":

        array = sample(size=shape)

    elif how == "normal":

        array = normal(size=shape)

    elif how == "range":

        array = arange(prod(shape)).reshape(shape)

    else:

        array = randint(0, how, size=shape)

    return array