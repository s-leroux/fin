from fin.seq.column import Column

class ColumnFactory:
    @staticmethod
    def column_from_ternary(*values, name="X"):
        """ Return a column created with `from_ternary_mv`.
        """
        master = Column.from_sequence(values, name=name)
        return Column.from_ternary_mv(master.t_values, name=name, type="t")

    @staticmethod
    def column_from_float(*values, name="X"):
        """ Return a column created with `from_float_mv`.
        """
        master = Column.from_sequence(values, name=name)
        return Column.from_float_mv(master.f_values, name=name, type="n")

    @staticmethod
    def column_from_sequence(*values, name="X"):
        """ Return a column created with `from_sequence`.
        """
        return Column.from_sequence(values, name=name)
