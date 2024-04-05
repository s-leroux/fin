# cython: cdivision=True

from cpython cimport array
from fin cimport tuplex
from fin.mathx cimport balloc, aalloc, vrand
from fin.model.solvers.solver cimport Domain, Eq, Solver

# ======================================================================
# Particle Struct and Utilities
# ======================================================================
cdef struct Particle:
    double best_score
    double *position
    double *best_position
    double *velocity

cdef struct Model:
    unsigned    n
    unsigned    population_size
    Domain      *domains
    unsigned    k
    Eq          *eqs
    double      inertia
    double      cognitive_coef
    double      social_coef
    double      global_best_score
    double      *global_best_position

# ======================================================================
# Low-level functions
# ======================================================================
cdef void _init_particles(Model* model, Particle* particles, double* buffer):
    """ Initialize the particles state.

        Set best known score to +infinity, best known position to NaN,
        current position to U(0,1) and velocity to U(-1, 1) — where
        U(...) is the uniform probability distribution.
    """
    cdef float infinity = 1./0
    cdef float nan = 0./0
    cdef unsigned n = model.n
    cdef Particle*  particle = particles

    cdef unsigned i, j
    for i in range(model.population_size):
        particle.position = buffer
        buffer += n
        particle.best_position = buffer
        buffer += n
        particle.velocity = buffer
        buffer += n

        particle.best_score = infinity
        vrand(n, particle.position)
        vrand(n, particle.velocity)
        # XXX We might improve the two lines above by grouping position and velocity
        # Not sure if it worth the pain though.

        for j in range(n):
            particle.best_position[j] = nan
            particle.velocity[j] = particle.velocity[j]*2-1

            particle.position[j] *= model.domains[j]._max-model.domains[j]._min
            particle.velocity[j] *= model.domains[j]._max-model.domains[j]._min

        particle += 1

cdef int _evaluate(Model* model, Particle* particles) except -1:
    cdef Particle* particle = particles

    cdef unsigned i
    cdef unsigned j
    cdef unsigned h
    cdef double score, tmp
    cdef Eq*    eq
    cdef Particle* curr = particles

    for i in range(model.population_size):
        score = 0.0
        point = tuplex.from_doubles(model.n, curr.position)
        for j in range(model.k):
            eq = &model.eqs[j]
            # map params to a list
            # XXX We might use the PyTuple low-level API here
            params = [ point[eq.params[h]] for h in range(eq.count) ]
            tmp = (<object>eq.fct)(*params)
            score += tmp*tmp
        
        # Is this the local best?
        if score < curr.best_score:
            curr.best_score = score
            for j in range(model.n):
                curr.best_position[j] = curr.position[j]

        # Is this the global best?
        if score < model.global_best_score:
            model.global_best_score = score
            best_solution = particle
            for j in range(model.n):
                model.global_best_position[j] = curr.position[j]

        curr += 1

    print(model.global_best_score)
    for j in range(model.n):
        print(model.global_best_position[j])

    return 0

cdef void _update(Model* model, Particle* particles):
    cdef unsigned i,j
    cdef Particle* curr = particles

    cdef double[2]   rprg
    for i in range(model.population_size):
        for j in range(model.n):
            vrand(2, rprg)

            # Update velocity
            curr.velocity[j] = \
                curr.velocity[j]*model.inertia \
                + model.cognitive_coef*rprg[0]*(curr.best_position[j]-curr.position[j]) \
                + model.social_coef*rprg[1]*(model.global_best_position[j]-curr.position[j])

            # Update position
            curr.position[j] += curr.velocity[j]
            # Should we clip or rebound on the boundaries?
            # Apparently rebounding (invert velocity) give much much better results!
            if curr.position[j] > model.domains[j]._max:
                curr.position[j] = model.domains[j]._max
                curr.velocity[j] *= -1
            elif curr.position[j] < model.domains[j]._min:
                curr.position[j] = model.domains[j]._min
                curr.velocity[j] *= -1

        curr += 1

cdef _print(Model* model, Particle* particles):
    print("-----"*14)
    cdef unsigned i,j
    for i in range(model.population_size):
        print(f"{i} {particles.best_score}")
        for j in range(model.n):
            print(f"{particles.position[j]} {particles.best_position[j]} {particles.velocity[j]}")

        particles += 1

# ======================================================================
# Particle Swarm Solver
# ======================================================================
cdef class ParticleSwarmSolver(Solver):
    """ Model solver using particle swarm optimization.
        
        https://en.wikipedia.org/wiki/Particle_swarm_optimization
    """
    cdef unsigned _population_size
    cdef int _iterations
    cdef double _inertia
    cdef double _cognitive_coef
    cdef double _social_coef

    def __cinit__(self,
            population_size,
            iterations,
            inertia,
            cognitive_coef,
            social_coef,
            ):
        self._population_size = population_size
        self._iterations = iterations
        self._inertia = inertia
        self._cognitive_coef = cognitive_coef
        self._social_coef = social_coef

    cdef c_solve(self, const unsigned n, Domain* domains, unsigned k, Eq *eqs):
        """ Solver's entry point.

            In this method, like other methods of this file, '`n` is the
            number of dimensions of the search space.
        """
        # Create a buffer large enough to store `count` particles
        cdef array.array particles_array = balloc(self._population_size*sizeof(Particle))
        cdef Particle *particles = <Particle*>particles_array.data.as_chars

        # We need for *each* particle:
        # - n doubles for its position
        # - n doubles for its velocity
        # - n doubles for its best known position
        # To that, we add:
        # - n doubles for the global best position
        cdef array.array buffer_array = aalloc(3*n*self._population_size+n)
        cdef double *buffer = buffer_array.data.as_doubles
        
        # Initialize the Model structure to keep the model's parameters
        cdef Model   model
        model.n = n
        model.population_size = self._population_size
        model.domains = domains
        model.k = k
        model.eqs = eqs
        model.inertia = self._inertia
        model.cognitive_coef = self._cognitive_coef
        model.social_coef = self._social_coef
        model.global_best_score = 1./0
        model.global_best_position = buffer
        buffer += n

        _init_particles(&model, particles, buffer)

        cdef int remaining = self._iterations
        while True:
            _print(&model, particles)
            remaining -= 1
            _evaluate(&model, particles)
            if remaining < 1:
                break

            _update(&model, particles)

        return (
            model.global_best_score,
            tuplex.from_doubles(model.n, model.global_best_position)
        )

