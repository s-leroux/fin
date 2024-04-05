# ======================================================================
# Constants
# ======================================================================
DEFAULT_DOMAIN = (0,100) # FIXME Replace with the full fp32/fp64 domain?

class DomainError(ValueError):
    pass

# ======================================================================
# Complex model
# ======================================================================
class ComplexModel:
    """ A complex model is an solver-agnostic representation of
        a model made of (possibly one or) several constraints.

        Constraints are given as "equilibrium functions" that evaluates to
        0 if the constraint is fully satisfied. The solver will try
        to minimize the absolute value of the set of equilibrium functions that
        defines the model.

        Equilibrium functions are associated at definition-time with a set of
        metadata to ease introspection.

        Currently, the metadata consists of a list of parameters in
        function argument's order as well as a description and a domain.

        The domain is either a signed value, or a [min; max] range.
        When the domain is a single value, the parameter is set to be bound.
        Solvers shouldn't modify bound parameters. On the other hand,
        solvers need to try to infer the range parameters in order to satisfy
        the best possible the set of constraints.
    """
    def __init__(self):
        self._eqs = [] # The list of equilibrium functions and param names order
        self._pdict = {} # Map between (eq, param_name) => param_data
        self._domains = {} # Map a param cluster to its domain

    def register(self, eq, *params):
        """ Register a new equilibrium function and associated metadata into the model.
        """
        self._eqs.append((eq, [param["name"] for param in params]))
        idx = 0
        for param in params:
            sig = (eq, param["name"])
            cluster = frozenset((sig,))
            self._pdict[sig] = dict(
                    position = idx,
                    description = param["description"],
                    cluster = cluster
                    )
            idx += 1
            self._domains[cluster] = DEFAULT_DOMAIN

    def bind(self, eq_A, param_name_A, eq_B, param_name_B):
        """ Bind two parameters.

            In practice this make both parameters to be part of the same cluster.
        """
        sig_A = (eq_A, param_name_A)
        sig_B = (eq_B, param_name_B)
        cluster_A = self._pdict[sig_A]["cluster"]
        cluster_B = self._pdict[sig_B]["cluster"]
        if cluster_A is cluster_B:
            # Already bound. Nothing to do.
            return

        # Unify both clusters
        cluster_C = cluster_A | cluster_B
        min_A, max_A = self._domains.pop(cluster_A)
        min_B, max_B = self._domains.pop(cluster_B)
        min_C = max(min_A, min_B)
        max_C = min(max_A, max_B)
        if min_C > max_C: # FIXME Or is NaN !
            raise DomainError(f"Unsolvable constraint for {cluster_C}: min is {min_C} max is {max_C}")
        
        # save the new cluster
        self._domains[cluster_C] = (min_C, max_C)
        # Update all parameters belonging to the same cluster
        for sig in cluster_C:
            self._pdict[sig]["cluster"] = cluster_C

    def get_domain_for(self, eq, param_name):
        """ Returns the domain for a parameter.

            EXPERIMENTAL. For debugging/testing purposes only.
        """
        cluster = self._pdict[eq, param_name]["cluster"]
        return self._domains[cluster]

    def domain(self, eq, param_name, min_value, max_value=None):
        if max_value is None:
            max_value = min_value

        sig = (eq, param_name)
        cluster = self._pdict[sig]["cluster"]
        curr_min, curr_max = self._domains[cluster]
        new_min = max(curr_min, min_value)
        new_max = min(curr_max, max_value)
        if new_min > new_max: # FIXME Or is NaN !
            raise DomainError(f"Unsolvable constraint for {cluster}: min is {new_min} max is {new_max}")

        self._domains[cluster] = (new_min, new_max)

    def export(self):
        """ Return the model as a list of parameters with their associated domain,
            and map between equilibrium functions and their parameter index in the list.

            This is the preferred format to interface with solvers.
        """

        clusters = tuple(self._domains.keys())
        # Above:
        # Iteration over a dict is in arbitrary order (and can vary from run to run),
        # but it should be consistent in the same run.
        # As I didn't find the confirmation in the docs, I map to a tuple for peace of
        # mind.
        cidx = { cluster: idx for idx, cluster in enumerate(clusters) }
        pidx = { sig: cidx[param["cluster"]] for sig, param in self._pdict.items() }

        domains = [ self._domains[cluster] for cluster in clusters ]
        eqs = [ (eq, [ pidx[eq, pname] for pname in pnames ]) for eq, pnames in self._eqs ]

        return domains, eqs

    def __repr__(self):
        return "ComplexModel(" \
                f"_eqs={self._eqs!r}," \
                f"_pdict={self._pdict!r}," \
                f"_domains={self._domains!r}," \
            ")"
