from fin.model.solvers import ParticleSwarmSolver
solver = ParticleSwarmSolver()
score, result = solver.solve(domains, eqs)

print(f"Score {score}")
for param, value in zip(params, result):
    print(f"{param['description']:20s}: {value}")

