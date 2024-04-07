import unittest

from fin.model import solvers

SOLVERS=(
    ( solvers.ParticleSwarmSolver, 1e-6, 1e-6, 10, 100, 0.5, 1.5, 1.5 ),
    ( solvers.RandomSolver, 2.5e-1, 1e-1, 500000 ),
        )

# ======================================================================
# Common tests for various solvers
# ======================================================================
class TestSolvers(unittest.TestCase):
    def test_solvers(self):
        testcases = {
                "desc": "Use case #1",
                "domains": [
                    (1,100),
                    (2,40),
                    ],
                "eqs": [
                    (lambda x : x*x - 12*x + 32, [1]),
                    (lambda a, b : (a-10)*(a-10)+(b-2)*(b-2)-8, [1, 0]),
                    ],
                "solution": (4, 8),
                },{
                "desc": "Use case #2",
                "domains": [
                    (1,100),
                    (2,40),
                    ],
                "eqs": [
                    (lambda x, y : (x-2)+(y-3), [0, 1]),
                    (lambda x, y : 2*(x-2)+(y-3), [0, 1]),
                    (lambda x, y : (x-2)+2*(y-3), [0, 1]),
                    ],
                "solution": (2, 3),
                },{
                "desc": "Use case #3 (unsolvable)",
                "domains": [
                    (10,100),
                    (20,40),
                    ],
                "eqs": [
                    (lambda x, y : x, [0, 1]),
                    (lambda x, y : y, [0, 1]),
                    ],
                "solution": (10, 20),
                "score": 505,
                }
        for testcase in testcases:
            desc = testcase["desc"]
            domains = testcase["domains"]
            eqs = testcase["eqs"]
            solution = testcase["solution"]

            for Solver, score_limit, precision, *args in SOLVERS:
                with(self.subTest(desc=desc, solver=Solver)):
                    solver = Solver(*args)
                    score, result = solver.solve(domains, eqs)
                    print(Solver, desc, score, result)

                    self.assertLess(score, testcase.get("score", score_limit))
                    self.assertEqual(len(result), len(solution))
                    for a, b in zip(result, solution):
                        self.assertAlmostEqual(a, b, delta=testcase.get("precision", precision))
