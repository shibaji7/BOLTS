# Adding an element

```python
# src/bolts/elements/my_shunt.py
from ..mna.stamp import Stamper
from .base import Element


class MyShunt(Element):
    def __init__(self, name, node, g_S):
        self.name, self.node, self.g = name, node, g_S

    @property
    def nodes(self):
        return (self.node,)

    def stamp(self, st: Stamper) -> None:
        st.add_conductance(self.node, None, self.g)      # None is the sea (ground)
```

Register it (`register_element("my_shunt", MyShunt)` in `elements/__init__.py`, or an entry point in your own package), add
`tests/test_my_shunt.py`, and, if the physics has a closed form, a case in `src/bolts/validation/`. Nonlinear elements will implement a
companion model for the Newton solver (v0.2). Put new parameters in `config/defaults/*.toml` with unit, status and source.
