from fin.seq.fc cimport funcx

# ======================================================================
# Functor test functions
# ======================================================================
cdef class Functor1Example(funcx.Functor1):
    def __cinit__(self):
        self.src1_tc = b'd'
        self.dst1_tc = b'd'

    cdef void eval(
            self,
            unsigned n,
            funcx.param_t* dst1,
            const funcx.param_t* src1,
            ):
        cdef unsigned i
        for i in range(n):
            # Simple copy
            dst1.as_doubles[i] = src1.as_doubles[i]

cdef class Functor2Example(funcx.Functor2):
    def __cinit__(self):
        self.src1_tc = b'd'
        self.src2_tc = b'd'
        self.dst1_tc = b'd'

    cdef void eval(
            self,
            unsigned n,
            funcx.param_t* dst1,
            const funcx.param_t* src1,
            const funcx.param_t* src2,
            ):
        cdef unsigned i
        for i in range(n):
            # Sum
            dst1.as_doubles[i] = src1.as_doubles[i] + src2.as_doubles[i]

cdef class Functor3Example(funcx.Functor3):
    def __cinit__(self):
        self.src1_tc = b'd'
        self.src2_tc = b'd'
        self.src3_tc = b'd'
        self.dst1_tc = b'd'

    cdef void eval(
            self,
            unsigned n,
            funcx.param_t* dst1,
            const funcx.param_t* src1,
            const funcx.param_t* src2,
            const funcx.param_t* src3,
            ):
        cdef unsigned i
        for i in range(n):
            # Sum
            dst1.as_doubles[i] = src1.as_doubles[i] + src2.as_doubles[i] + src3.as_doubles[i]

cdef class Functor1_3Example(funcx.Functor1_3):
    def __cinit__(self):
        self.src1_tc = b'd'
        self.dst1_tc = b'd'
        self.dst2_tc = b'd'
        self.dst3_tc = b'd'

    cdef void eval(
            self,
            unsigned n,
            funcx.param_t* dst1,
            funcx.param_t* dst2,
            funcx.param_t* dst3,
            const funcx.param_t* src1,
            ):
        cdef unsigned i
        for i in range(n):
            # Sum
            dst1.as_doubles[i] = dst2.as_doubles[i] = dst3.as_doubles[i] = src1.as_doubles[i]

cdef class Functor2_3Example(funcx.Functor2_3):
    def __cinit__(self):
        self.src1_tc = b'd'
        self.src2_tc = b'd'
        self.dst1_tc = b'd'
        self.dst2_tc = b'd'
        self.dst3_tc = b'd'

    cdef void eval(
            self,
            unsigned n,
            funcx.param_t* dst1,
            funcx.param_t* dst2,
            funcx.param_t* dst3,
            const funcx.param_t* src1,
            const funcx.param_t* src2,
            ):
        cdef unsigned i
        for i in range(n):
            # Sum
            dst1.as_doubles[i] = dst2.as_doubles[i] = dst3.as_doubles[i] = src1.as_doubles[i] + src2.as_doubles[i]
