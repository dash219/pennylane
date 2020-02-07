# Copyright 2018-2020 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Contains the sum function, for summing QNode collections.
"""
# pylint: disable=too-many-arguments,import-outside-toplevel

from .apply import apply


def _get_sum_func(interface):
    """Helper function for :func:`~.sum` to determine
    the correct sum function depending on the QNodeCollection
    interface.

    Args:
        interface (str): the interface to get the sum function for

    Returns:
        callable: the required sum function
    """
    if interface == "tf":
        import tensorflow as tf

        return tf.reduce_sum

    if interface == "torch":
        import torch

        return torch.sum

    if interface in ("autograd", "numpy"):
        from autograd import numpy as np

        return np.sum

    if interface is None:
        import numpy as np

        return np.sum

    raise ValueError("Unknown interface {}".format(interface))


def sum(x):
    """Lazily sum the constituent QNodes of a :class:`QNodeCollection`.

    Args:
        x (QNodeCollection): a QNode collection of independent QNodes.

    .. seealso:: :func:`~.apply`, :func:`~.dot`

    **Example:**

    We can create a QNodeCollection using :func:`~.map`:

    >>> dev = qml.device("default.qubit", wires=2)
    >>> obs_list = [qml.PauliX(0) @ qml.PauliZ(1), qml.PauliZ(0) @ qml.PauliZ(1)]
    >>> qnodes = qml.map(qml.templates.StronglyEntanglingLayers, obs_list, dev, interface="torch")

    For the cost function, we now sum the results of all QNodes in the collection:

    >>> cost = qml.sum(qnodes)

    This is a lazy summation --- no QNode evaluation has yet occured. Evaluation
    only occurs when the returned function ``cost`` is evaluated:

    >>> x = qml.init.strong_ent_layers_normal(3, 2)
    >>> cost(x)
    tensor(0.9092, dtype=torch.float64, grad_fn=<SumBackward0>)
    """
    interface = getattr(x, "interface", None)
    sum_fn = _get_sum_func(x.interface)
    return apply(sum_fn, x)