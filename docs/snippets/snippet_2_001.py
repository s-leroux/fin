from fin.seq import serie
from fin.seq import fc

s1 = serie.Serie.create(
        (fc.named("X"), fc.sequence((1,2,3,4))),
        (fc.named("Y"), fc.mul, "X", fc.constant(10)),
    )

print()
print("s1 is:")
print(s1)

s2 = serie.Serie.create(
        (fc.named("X"), fc.sequence((1,4,5))),
        (fc.named("Z"), fc.mul, "X", fc.constant(100)),
    )

print()
print("s2 is:")
print(s2)

print()
print("s1 & s2 is:")
print(s1 & s2)
