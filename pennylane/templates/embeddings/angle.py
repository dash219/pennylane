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
r"""
Contains the ``AngleEmbedding`` template.
"""
# pylint: disable-msg=too-many-branches,too-many-arguments,protected-access
from pennylane.templates.decorator import template
from pennylane.ops import RX, RY, RZ
from pennylane.templates import broadcast
from pennylane.templates.utils import (
    check_shape,
    check_is_in_options,
    check_type,
    get_shape,
)
from pennylane.wires import Wires


@template
def AngleEmbedding(features, wires, rotation="X"):
    r"""
    Encodes :math:`N` features into the rotation angles of :math:`n` qubits, where :math:`N \leq n`.

    The rotations can be chosen as either :class:`~pennylane.ops.RX`, :class:`~pennylane.ops.RY`
    or :class:`~pennylane.ops.RZ` gates, as defined by the ``rotation`` parameter:

    * ``rotation='X'`` uses the features as angles of RX rotations

    * ``rotation='Y'`` uses the features as angles of RY rotations

    * ``rotation='Z'`` uses the features as angles of RZ rotations

    The length of ``features`` has to be smaller or equal to the number of qubits. If there are fewer entries in
    ``features`` than rotations, the circuit does not apply the remaining rotation gates.

    Args:
        features (array): input array of shape ``(N,)``, where N is the number of input features to embed,
            with :math:`N\leq n`
        wires (Iterable or Wires): Wires that the template acts on. Accepts an iterable of numbers or strings, or
            a Wires object.
        rotation (str): Type of rotations used

    Raises:
        ValueError: if inputs do not have the correct format
    """

    #############
    # Input checks

    wires = Wires(wires)

    check_shape(
        features,
        (len(wires),),
        bound="max",
        msg="'features' must be of shape {} or smaller; "
        "got {}.".format((len(wires),), get_shape(features)),
    )
    check_type(rotation, [str], msg="'rotation' must be a string; got {}".format(rotation))

    check_is_in_options(
        rotation,
        ["X", "Y", "Z"],
        msg="did not recognize option {} for 'rotation'.".format(rotation),
    )

    ###############

    if rotation == "X":
        _broadcast_no_shape_check(unitary=RX, pattern="single", wires=wires, parameters=features)

    elif rotation == "Y":
        _broadcast_no_shape_check(unitary=RY, pattern="single", wires=wires, parameters=features)

    elif rotation == "Z":
        _broadcast_no_shape_check(unitary=RZ, pattern="single", wires=wires, parameters=features)

def _broadcast_no_shape_check(unitary, pattern, wires, parameters):
    """This is a temporary auxiliary function that turns off the internal shape
    check of the ``broadcast`` function used by AngleEmbedding to allow for
    fewer number of features as qubits.

    This behaviour will be revisited after tape mode has been introduced for
    templates.
    """
    try:
        broadcast(unitary=unitary, pattern=pattern, wires=wires, parameters=parameters)
    except ValueError as e:
        msg = "must contain entries for {} unitaries".format(len(wires))

        # Re-raise the error if it did not occur when the error message refers
        # to a mismatch of the parameters for unitaries
        if msg not in str(e):
            raise e
