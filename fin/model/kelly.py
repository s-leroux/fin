import fin.model

import math
import fin.math

from fin.model.kellyx import kelly_criterion

# ======================================================================
# Kelly Criterion
# ======================================================================
KellyCriterion = fin.model.Model(
    kelly_criterion, 
    p=dict(
        value=(0.0, 1.0),
    )
)
