from fin.model.complexmodel import ComplexModel

model = ComplexModel()
eq1 = model.register(
        lambda duration, buyprice : 800*1.04**duration-buyprice,
        dict(name="duration", description="Placement duration in years"),
        dict(name="buyprice", description="Good's buy price"),
    )
eq2 = model.register(
        lambda duration, buyprice : 1000*1.02**duration-buyprice,
        dict(name="duration", description="Placement duration in years"),
        dict(name="buyprice", description="Good's buy price"),
    )

