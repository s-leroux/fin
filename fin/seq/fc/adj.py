from . import arit
from . import proj

def adj(serie, op, hi, lo, cl, adj_cl):
    return ( proj.thread(arit.mul, 4), op, hi, lo, cl, (arit.div, adj_cl, cl) )
