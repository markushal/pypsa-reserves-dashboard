### Methodology:
We follow the approach that has been presented by Andreas Hösl et al here: https://www.youtube.com/watch?v=fmwDxNpSMM4&t=8043s

The basic idea is that each generator needs to provide reserve capacity **symmetrically**. That means that it needs to be able to increase and decrease its output by the same amount in order to contribute to satisfy reserve requirements. This ensures that generators need to operate at partial load in order to provide reserve capacity. 

It involves defining a new variable and some new constraints:
- a new variable $p_{\text{reserve}}(g,t)$ that represents the reserve power provided by generator $g$ in time step $t$. 

- One new constraint that ensures that for each time step $t$, the sum of all reserve power provided is greater or equal the required reserves: 
$$
\forall t: \sum_{g} p_{\text{reserve}}(g,t) \geq \text{reserve\_requirement}
$$

- One constraint to ensure that the reserve power a generator provides must be less or equal than the difference between its output $p$ and its nominal capacity $p_\text{nom}$, , multiplied with a scalar coefficient ``a``. This coefficient can have any value between 0 and 1 and represents the technical availability of a generator to provide balancing power. 
$$
\forall g, t: p_\text{reserve}(g, t) \leq a(g) p_\text{nom}(g) - p(g,t)
$$

- One constraint  to ensure that the balancing power a generator provides must be less or equal than its actual output ``p``, multiplied with a scalar coefficient ``b``. This coefficient can have any value between 0 and 1 and represents the technical availability of a generator to provide balancing power. 

$$
\forall g, t: p_\text{reserve}(g, t) \leq b(g) p(g,t)
$$
