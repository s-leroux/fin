import sys

from fin.utils.log import console
from fin.utils import formatters
from fin import datetime

from fin.mathx cimport isnan

cdef object IGNORE = object()

# ======================================================================
# Type string parsing
# ======================================================================
cdef parse_type_char(Py_UCS4 c):
    #
    # Generic types
    #
    if c==u'-': # IGNORE
        return None
    elif c==u'o':
        return Object()
    #
    # Numeric types
    #
    elif c==u'n': # NUMERIC
#            f = float
        return Float()
    elif c==u'i': # INTEGER
#            f = int
        return Integer()
    #
    # Logical types
    #
    elif c==u't': # TERNARY
        return Ternary()
    #
    # Date/Time types
    #
    elif c==u'd': # ISO DATE
#            f = datetime.parseisodate
        return Date()
    elif c==u's': # SECONDS SINCE UNIX EPOCH
#            f = datetime.parsetimestamp
        return DateTime()
    elif c==u'm': # MILLISECONDS SINCE UNIX EPOCH
#            f = datetime.parsetimestamp_ms
        return DateTimeMicro()
    #
    # Otherwise...
    #
    else:
        raise ValueError(f"Invalid column type specifier {c!r}")

cdef parse_type_atom(object tpe):
    if not isinstance(tpe, str):
        return tpe

    cdef str fstring = <str>tpe
    cdef Py_UCS4 c = fstring[0]
    if len(fstring) > 1:
        raise ValueError(f"Invalid column type specifier {fstring!r}")

    return parse_type_char(c)

cdef parse_type_string(object types):
    if not isinstance(types, str):
        return types

    cdef str fstring = <str>types
    types = []

    for fchar in fstring:
        types.append(parse_type_char(fchar))

    return types

# ======================================================================
# Types
# ======================================================================
class ColType:
    """ The new column type implementation.

        The type is responsible converting columns from and to
        strings. The conversion of the individual cells to string
        with extended alignment information if forwarded to a formatter
        object.
    """
    def __init__(self, **kwargs):
        self._options = kwargs
        self._formatter = None

    def set_option(self, name, value):
        self._options[name] = value

    def format(self, context, column):
        formatter = self._formatter
        if formatter is None:
            formatter = self._formatter = self.create_formatter()

        cdef list result = []
        for cell in column:
            result.append(formatter(context, cell))

        return result

    def create_formatter(self):
        """ Return a Formatter object suitable for data of this type.

            The default implementation return a StringFormatter.
        """
        return formatters.StringLeftFormatter()

    def parse_sequence(self, sequence):
        """ Convert from a sequence of Python objects to a tuple of the receiver's type instances.

            Some types may collect statistics about the cell's current
            representation in order to convert the values back to string at a
            later time. Typically, a float formatter may gather data to
            infer the precision used for float to string conversion.

            The default implementation trivially convert the sequence to a tuple.
        """
        return tuple(sequence)

class Float(ColType):
    """ The type for a column containing floating-point numbers.

        This type support the following options:
        - precision:
            The number of digits after the decimal separator when converting
            to a string.
    """
    def parse_sequence(self, sequence):
        cdef list result = []
        cdef unsigned precision = 2
        cdef int tmp

        for item in sequence:
            try:
                value = float(item)
            except:
                value = None # XXX Log warning here
            else:
                if isnan(value):
                    value = None
                elif type(item) is str:
                    tmp = item.rfind(".")
                    if tmp > -1:
                        tmp = len(item)-tmp-1
                        if tmp > precision:
                            precision = tmp

            result.append(value)

        self._options["precision.inferred"] = precision
        return result

    def create_formatter(self):
        precision = self._options.get("precision")
        if precision is None:
            precision = self._options.get("precision.inferred")
        if precision is None:
            precision = 2

        return formatters.FloatFormatter(precision=precision)

class Integer(ColType):
    """ The type for a column containing integer numbers.
    """
    def parse_sequence(self, sequence):
        cdef list result = []
        for item in sequence:
            try:
                value = int(item)
            except:
                value = None # XXX Log warning here

            result.append(value)

        return result

    def create_formatter(self):
        return formatters.IntegerFormatter()

class Ternary(ColType):
    """ The type for a column containing standard ternary logic values.
        
        This type support the following options:
        - true:
            The set of string considered as valid representations
            for the True value
        - false:
            The set of string considered as valid representations
            for the False value
        - none:
            The set of string considered as valid representations
            for the None value
    """
    def __init__(self, **kwargs):
        if "true" not in kwargs:
            kwargs["true"] = ("True", "T", "Yes")
        if "false" not in kwargs:
            kwargs["false"] = ("False", "F", "No")
        if "none" not in kwargs:
            kwargs["none"] = ("None", "N", "")

        ColType.__init__(self, **kwargs)

    def parse_sequence(self, sequence):
        true = self._options.get("true")
        false = self._options.get("false")
        none = self._options.get("none")

        cdef list result = []
        for item in sequence:
            if item is True or item in true:
                result.append(True)
            elif item is False or item in false:
                result.append(False)
            elif item is None or item in none:
                result.append(None)
            else:
                raise ValueError(f"Unexpected value {item}")

        return result

    def create_formatter(self):
        return formatters.TernaryFormatter(
                true=self._options["true"][0],
                false=self._options["false"][0],
                none=self._options["none"][0],
            )

class Object(ColType):
    """ The type for a column containing arbitrary PYthon objects.

        This is the default type if none is specified.
    """
    def parse_sequence(self, sequence):
        return sequence

class Other(ColType):
    """ User-defined type.

        This type support the following options:
        - from_object:
            A function to convert from a Python object to the most meaningful format for
            this type of data.
    """
    def parse_sequence(self, sequence):
        try:
            parser = self._options["from_object"]
        except KeyError:
            return super().parse_sequence(sequence)

        cdef list result = []
        for item in sequence:
            result.append(parser(item))

        return result

class DateTimeBase(ColType):
    """ The type for a column containing datetime values.

        This type support the following options:
        - format:
            The strftime format string used when converting to string.
    """
    def create_formatter(self):
        format = self._options.get("format")

        return formatters.DateTimeFormatter(format=format)

    def parse_sequence(self, sequence):
        raise NotImplementedError(f"Sub-classes should call _parse_sequence_to() with the proper arguments")

    def parse_sequence_to(self, sequence, datetime_cls, datetime_from_str):
        cdef list result = []
        from_ts = datetime_cls.fromtimestamp

        for item in sequence:
            # We recognize the following convestions:
            # - None -> None
            # - DateTime -> DateTime: identity
            # - number/obj.timetamp -> convert from timestamp
            # - str -> DateTime: parse using a format string
            if item is None:
                result.append(item)
                continue

            t = type(item)
            if t is datetime_cls:
                result.append(item)
                continue

            # Possible timestamp:
            try:
                item = item.timestamp
            except AttributeError:
                pass

            try:
                item = float(item)
            except:
                pass
            else:
                result.append(from_ts(item))
                continue

            # Time string
            if isinstance(item, str):
                result.append(datetime_from_str(item))
                continue

            raise ValueError(f"Can't convert {item} or type {t} to a CalendarDateTime")

        return result

class Date(DateTimeBase):
    def parse_sequence(self, sequence):
        return self.parse_sequence_to(
                sequence, datetime.CalendarDate,
                datetime.parseisodate,
            )

class DateTime(DateTimeBase):
    def parse_sequence(self, sequence):
        return self.parse_sequence_to(sequence,
                datetime.CalendarDateTime,
                datetime.parseisodatetime,
            )

class DateTimeMicro(DateTimeBase):
    def parse_sequence(self, sequence):
        return self.parse_sequence_to(
                sequence,
                datetime.CalendarDateTimeMicro,
                datetime.parseisodatetime_ms,
            )

