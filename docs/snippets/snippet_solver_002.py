model.bind(eq1, "duration", eq2, "duration")
model.bind(eq1, "buyprice", eq2, "buyprice")
model.domain(eq1, "duration", 1, 100)
model.domain(eq1, "buyprice", 1, 10000)
