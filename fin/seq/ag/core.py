from fin.seq import coltypes

class AggregateFunction:
    def type_for(self, column):
        return column.type

    def __call__(self, *cols):
        raise NotImplementedError()

class _First(AggregateFunction):
    def __call__(self, *cols):
        return [col[0] for col in cols]

first = _First()

class _Count(AggregateFunction):
    def type_for(self, column):
        return coltypes.Integer()

    def __call__(self, *cols):
        return [len(col) for col in cols]

count = _Count()

class _Avg(AggregateFunction):
    def type_for(self, column):
        return coltypes.Float()

    def __call__(self, *cols):
        return [sum(col)/len(col) for col in cols]

avg = _Avg()
