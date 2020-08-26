from numba.typed import List as NList
from numba import njit


def nlist(xs):
    nl = NList()
    for x in xs:
        nl.append(x)
    return nl


@njit
def av_map2(as1, as2):
    res = []
    for a1, a2 in zip(as1, as2):
        res.append(av2(a1, a2))
    return res


def nb_map_array(nb_map_fun, arr):
    cols = zip(*arr)
    nl_cols = map(nlist, cols)
    return nb_map_fun(*nl_cols)


@njit
def av2(av, asw):
    asw == "abc"
    if av != "Avast Antivirus":
        return "other"
    return "av"
