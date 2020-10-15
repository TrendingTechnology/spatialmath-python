# Created by: Aditya Dua, 2017
# Peter Corke, 2020
# 13 June, 2017

import numpy as np
from collections import UserList
import copy
from spatialmath.base import argcheck
from spatialmath import base as tr
from spatialmath.smuserlist import SMUserList
from spatialmath.base import symbolic as sym

_eps = np.finfo(np.float64).eps

# colored printing of matrices to the terminal
#   colored package has much finer control than colorama, but the latter is available by default with anaconda
try:
    from colored import fg, bg, attr
    _color = True
    # print('using colored output')
except ImportError:
    # print('colored not found')
    _color = False

# try:
#     import colorama
#     colorama.init()
#     print('using colored output')
#     from colorama import Fore, Back, Style

# except:
#     class color:
#         def __init__(self):
#             self.RED = ''
#             self.BLUE = ''
#             self.BLACK = ''
#             self.DIM = ''

# print(Fore.RED + '1.00 2.00 ' + Fore.BLUE + '3.00')
# print(Fore.RED + '1.00 2.00 ' + Fore.BLUE + '3.00')
# print(Fore.BLACK + Style.DIM + '0 0 1')


class SMPose(SMUserList):
    """
    Superclass for SO(N) and SE(N) objects

    Subclasses are:

    - ``SO2`` representing elements of SO(2) which describe rotations in 2D
    - ``SE2`` representing elements of SE(2) which describe rigid-body motion in 2D
    - ``SO3`` representing elements of SO(3) which describe rotations in 3D
    - ``SE3`` representing elements of SE(3) which describe rigid-body motion in 3D

    Arithmetic operators are overloaded but the operation they perform depend
    on the types of the operands.  For example:

    - ``*`` will compose two instances of the same subclass, and the result will
      be an instance of the same subclass, since this is a group operator.
    - ``+`` will add two instances of the same subclass, and the result will be
      a matrix, not an instance of the same subclass, since addition is not a group operator.

    These classes all inherit from ``UserList`` which enables them to 
    represent a sequence of values, ie. an ``SE3`` instance can contain
    a sequence of SE(3) values.  Most of the Python ``list`` operators
    are applicable::

        >>> x = SE3()  # new instance with identity matrix value
        >>> len(x)     # it is a sequence of one value
        1
        >>> x.append(x)  # append to itself
        >>> len(x)       # it is a sequence of two values
        2
        >>> x[1]         # the element has a 4x4 matrix value
        SE3([
        array([[1., 0., 0., 0.],
               [0., 1., 0., 0.],
               [0., 0., 1., 0.],
            [0., 0., 0., 1.]]) ])
        >>> x[1] = SE3.Rx(0.3)  # set an elements of the sequence
        >>> x.reverse()         # reverse the elements in the sequence
        >>> del x[1]            # delete an element

    """

    def __new__(cls, *args, **kwargs):
        """
        Create the subclass instance (superclass method)

        Create a new instance and call the superclass initializer to enable the 
        ``UserList`` capabilities.
        """

        pose = super(SMPose, cls).__new__(cls)  # create a new instance
        super().__init__(pose)  # initialize UserList
        return pose

# ------------------------------------------------------------------------ #

    @property
    def about(self):
        """
        Succinct summary of object type and length (superclass property)

        :return: succinct summary
        :rtype: str

        Displays the type and the number of elements in compact form, for 
        example::

            >>> x = SE3([SE3() for i in range(20)])
            >>> len(x)
            20
            >>> print(x.about)
            SE3[20]
        """
        return "{:s}[{:d}]".format(type(self).__name__, len(self))

    @property
    def N(self):
        """
        Dimension of the object's group (superclass property)

        :return: dimension
        :rtype: int

        Dimension of the group is 2 for ``SO2`` or ``SE2``, and 3 for ``SO3`` or ``SE3``.
        This corresponds to the dimension of the space, 2D or 3D, to which these
        rotations or rigid-body motions apply.

        Example::

            >>> SE3().N
            3
            >>> SE2().N
            2
        """
        if type(self).__name__ == 'SO2' or type(self).__name__ == 'SE2':
            return 2
        else:
            return 3

    #----------------------- tests
    @property
    def isSO(self):
        """
        Test if object belongs to SO(n) group (superclass property)

        :param self: object to test
        :type self: SO2, SE2, SO3, SE3 instance
        :return: ``True`` if object is instance of SO2 or SO3
        :rtype: bool
        """
        return type(self).__name__ == 'SO2' or type(self).__name__ == 'SO3'

    @property
    def isSE(self):
        """
        Test if object belongs to SE(n) group (superclass property)

        :param self: object to test
        :type self: SO2, SE2, SO3, SE3 instance
        :return: ``True`` if object is instance of SE2 or SE3
        :rtype: bool
        """
        return type(self).__name__ == 'SE2' or type(self).__name__ == 'SE3'


# ------------------------------------------------------------------------ #


# ------------------------------------------------------------------------ #

    # --------- compatibility methods


    def isrot(self):
        """
        Test if object belongs to SO(3) group (superclass method)

        :return: ``True`` if object is instance of SO3
        :rtype: bool

        For compatibility with Spatial Math Toolbox for MATLAB.
        In Python use ``isinstance(x, SO3)``.

        Example::

            >>> x = SO3()
            >>> x.isrot()
            True
            >>> x = SE3()
            >>> x.isrot()
            False
        """
        return type(self).__name__ == 'SO3'

    def isrot2(self):
        """
        Test if object belongs to SO(2) group (superclass method)

        :return: ``True`` if object is instance of SO2
        :rtype: bool

        For compatibility with Spatial Math Toolbox for MATLAB.
        In Python use ``isinstance(x, SO2)``.

        Example::

            >>> x = SO2()
            >>> x.isrot()
            True
            >>> x = SE2()
            >>> x.isrot()
            False
        """
        return type(self).__name__ == 'SO2'

    def ishom(self):
        """
        Test if object belongs to SE(3) group (superclass method)

        :return: ``True`` if object is instance of SE3
        :rtype: bool

        For compatibility with Spatial Math Toolbox for MATLAB.
        In Python use ``isinstance(x, SE3)``.

        Example::

            >>> x = SO3()
            >>> x.isrot()
            False
            >>> x = SE3()
            >>> x.isrot()
            True
        """
        return type(self).__name__ == 'SE3'

    def ishom2(self):
        """
        Test if object belongs to SE(2) group (superclass method)

        :return: ``True`` if object is instance of SE2
        :rtype: bool

        For compatibility with Spatial Math Toolbox for MATLAB.
        In Python use ``isinstance(x, SE2)``.

        Example::

            >>> x = SO2()
            >>> x.isrot()
            False
            >>> x = SE2()
            >>> x.isrot()
            True
        """
        return type(self).__name__ == 'SE2'

     #----------------------- functions

    def det(self):
        """
        Determinant of rotational component (superclass method)

        :return: Determinant of rotational component
        :rtype: float or NumPy array

        ``x.det()`` is the determinant of the rotation component of the values
        of ``x``.  

        Example::

            >>> x=SE3.Rand()
            >>> x.det()
            1.0000000000000004
            >>> x=SE3.Rand(N=2)
            >>> x.det()
            [0.9999999999999997, 1.0000000000000002]

        :SymPy: not supported
        """
        if type(self).__name__ in ('SO3', 'SE3'):
            if len(self) == 1:
                return np.linalg.det(self.A[:3,:3])
            else:
                return [np.linalg.det(T[:3,:3]) for T in self.data]
        elif type(self).__name__ in ('SO2', 'SE2'):
            if len(self) == 1:
                return np.linalg.det(self.A[:2,:2])
            else:
                return [np.linalg.det(T[:2,:2]) for T in self.data]


    def log(self, twist=False):
        """
        Logarithm of pose (superclass method)

        :return: logarithm :rtype: numpy.ndarray :raises: ValueError

        An efficient closed-form solution of the matrix logarithm.

        =====  ======  ===============================
        Input         Output
        -----  ---------------------------------------
        Pose   Shape   Structure
        =====  ======  ===============================
        SO2    (2,2)   skew-symmetric SE2    (3,3)   augmented skew-symmetric
        SO3    (3,3)   skew-symmetric SE3    (4,4)   augmented skew-symmetric
        =====  ======  ===============================

        Example::

            >>> x = SE3.Rx(0.3)
            >>> y = x.log()
            >>> y
            array([[ 0. , -0. ,  0. ,  0. ],
                   [ 0. ,  0. , -0.3,  0. ],
                   [-0. ,  0.3,  0. ,  0. ],
                   [ 0. ,  0. ,  0. ,  0. ]])


        :seealso: :func:`~spatialmath.base.transforms2d.trlog2`,
        :func:`~spatialmath.base.transforms3d.trlog`

        :SymPy: not supported
        """
        if self.N == 2:
            log = [tr.trlog2(x, twist=twist) for x in self.data]
        else:
            log = [tr.trlog(x, twist=twist) for x in self.data]
        if len(log) == 1:
            return log[0]
        else:
            return log

    def interp(self, s=None, start=None):
        """
        Interpolate pose (superclass method)

        :param start: initial pose
        :type start: same as ``self``
        :param s: interpolation coefficient, range 0 to 1
        :type s: float or array_like
        :return: interpolated pose
        :rtype: SO2, SE2, SO3, SE3 instance

        - ``X.interp(s)`` interpolates the pose X between identity when s=0
          and X when s=1.

         ======  ======  ===========  ===============================
         len(X)  len(s)  len(result)  Result
         ======  ======  ===========  ===============================
         1       1       1            Y = interp(identity, X, s)
         M       1       M            Y[i] = interp(T0, X[i], s)
         1       M       M            Y[i] = interp(T0, X, s[i])
         ======  ======  ===========  ===============================

        Example::

            >>> x = SE3.Rx(0.3)
            >>> print(x.interp(0))
            SE3(array([[1., 0., 0., 0.],
                       [0., 1., 0., 0.],
                       [0., 0., 1., 0.],
                       [0., 0., 0., 1.]]))
            >>> print(x.interp(1))
            SE3(array([[ 1.        ,  0.        ,  0.        ,  0.        ],
                       [ 0.        ,  0.95533649, -0.29552021,  0.        ],
                       [ 0.        ,  0.29552021,  0.95533649,  0.        ],
                       [ 0.        ,  0.        ,  0.        ,  1.        ]]))
            >>> y = x.interp(x, np.linspace(0, 1, 10))
            >>> len(y)
            10
            >>> y[5]
            SE3(array([[ 1.        ,  0.        ,  0.        ,  0.        ],
                       [ 0.        ,  0.98614323, -0.16589613,  0.        ],
                       [ 0.        ,  0.16589613,  0.98614323,  0.        ],
                       [ 0.        ,  0.        ,  0.        ,  1.        ]]))

        Notes:

        #. For SO3 and SE3 rotation is interpolated using quaternion spherical linear interpolation (slerp).

        :seealso: :func:`~spatialmath.base.transforms3d.trinterp`, :func:`~spatialmath.base.quaternions.slerp`, :func:`~spatialmath.base.transforms2d.trinterp2`

        :SymPy: not supported
        """
        s = argcheck.getvector(s)
        if start is not None:
            assert len(start) == 1, 'len(start) must == 1'
            start = start.A

        if self.N == 2:
            # SO(2) or SE(2)
            if len(s) > 1:
                assert len(self) == 1, 'if len(s) > 1, len(X) must == 1'
                return self.__class__([tr.trinterp2(start, self.A, s=_s) for _s in s])
            else:
                return self.__class__([tr.trinterp2(start, x, s=s[0]) for x in self.data])
        elif self.N == 3:
            # SO(3) or SE(3)
            if len(s) > 1:
                assert len(self) == 1, 'if len(s) > 1, len(X) must == 1'
                return self.__class__([tr.trinterp(start, self.A, s=_s) for _s in s])
            else:
                return self.__class__([tr.trinterp(start, x, s=s[0]) for x in self.data])

    def norm(self):
        """
        Normalize pose (superclass method)

        :return: pose
        :rtype: SO2, SE2, SO3, SE3 instance

        - ``X.norm()`` is an equivalent pose object but the rotational matrix 
          part of all values has been adjusted to ensure it is a proper orthogonal
          matrix rotation.

        Example::

            >>> x = SE3()
            >>> y = x.norm()
            >>> y
            SE3(array([[1., 0., 0., 0.],
                       [0., 1., 0., 0.],
                       [0., 0., 1., 0.],
                       [0., 0., 0., 1.]]))

        Notes:

        #. Only the direction of A vector (the z-axis) is unchanged.
        #. Used to prevent finite word length arithmetic causing transforms to 
           become 'unnormalized'.

        :seealso: :func:`~spatialmath.base.transforms3d.trnorm`, :func:`~spatialmath.base.transforms2d.trnorm2`
        """
        if self.N == 2:
            return self.__class__([tr.trnorm2(x) for x in self.data])
        else:
            return self.__class__([tr.trnorm(x) for x in self.data])

    def simplify(self):
        """
        Symbolically simplify matrix values (superclass method)

        :return: pose with symbolic elements
        :rtype: pose instance

        Apply symbolic simplification to every element of every value in the
        pose instane. 

        Example::

            >>> a = SE3.Rx(sympy.symbols('theta')
            >>> b = a * a
            >>> b
            SE3(array([[1, 0, 0, 0.0],
            [0, -sin(theta)**2 + cos(theta)**2, -2*sin(theta)*cos(theta), 0],
            [0, 2*sin(theta)*cos(theta), -sin(theta)**2 + cos(theta)**2, 0],
            [0.0, 0, 0, 1.0]], dtype=object)
            >>> b.simplify()
            SE3(array([[1, 0, 0, 0],
            [0, cos(2*theta), -sin(2*theta), 0],
            [0, sin(2*theta), cos(2*theta), 0],
            [0, 0, 0, 1.00000000000000]], dtype=object))

        .. todo:: No need to simplify the constants in bottom row

        :SymPy: supported
        """
        vf = np.vectorize(sym.simplify)
        return self.__class__([vf(x) for x in self.data], check=False)

    # ----------------------- i/o stuff

    def printline(self, **kwargs):
        """
        Stringify pose as a single line (superclass method)

        :param label: text label to put at start of line
        :type label: str
        :param fmt: conversion format for each number as used by ``format()``
        :type fmt: str
        :param label: text label to put at start of line
        :type label: str
        :param orient: 3-angle convention to use, optional, ``SO3`` and ``SE3``
                       only
        :type orient: str
        :param unit: angular units: 'rad' [default], or 'deg'
        :type unit: str
        :param file: file to write formatted string to. [default, stdout]
        :type file: 
        :return: formatted string
        :rtype: str

        - ``X.printline()`` print ``X`` in single-line format
        - ``X.printline(file=None)`` is a string representing the pose ``X`` in single-line format

        If ``X`` has multiple values, print one per line.

        Example::

            >>> x=SE3.Rx(0.3)
            >>> x.printline()
            t =        0,        0,        0; rpy/zyx =       17°,        0°,        0°
            >>> x = SE3.Rx([0.2, 0.3])
            >>> x.printline()
            t =        0,        0,        0; rpy/zyx =       11°,        0°,        0°
            t =        0,        0,        0; rpy/zyx =       17°,        0°,        0°
        >> x = SE2(1, 2, 0.3)
            >>> x.printline()
            t =        1,        2;       17 deg
        
        .. note:: The formatted string is always returned.

        """
        s = []
        if self.N == 2:
            for x in self.data:
                s.append(tr.trprint2(x, **kwargs))
        else:
            for x in self.data:
                s.append(tr.trprint(x, **kwargs))

        return '\n'.join(s)

    def __repr__(self):
        """
        Readable representation of pose (superclass method)

        :return: readable representation of the pose as a list of arrays
        :rtype: str

        Example::

            >>> x = SE3.Rx(0.3)
            >>> x
            SE3(array([[ 1.        ,  0.        ,  0.        ,  0.        ],
                       [ 0.        ,  0.95533649, -0.29552021,  0.        ],
                       [ 0.        ,  0.29552021,  0.95533649,  0.        ],
                       [ 0.        ,  0.        ,  0.        ,  1.        ]]))

        """

        # TODO: really should iterate over all the elements, can have a symb
        #       element and ~eps values
        def trim(x):
            if x.dtype == 'O':
                return x
            else:
                return tr.removesmall(x)

        name = type(self).__name__
        if len(self) == 0:
            return name + '([])'
        elif len(self) == 1:
            # need to indent subsequent lines of the native repr string by 4 spaces
            return name + '(' + trim(self.A).__repr__().replace('\n', '\n    ') + ')'
        else:
            # format this as a list of ndarrays
            return name + '([\n' + ',\n'.join([trim(v).__repr__() for v in self.data]) + ' ])'

    def _repr_pretty_(self, p, cycle):
        """
        Pretty string for IPython (superclass method)

        :param p: pretty printer handle (ignored)
        :param cycle: pretty printer flag (ignored)

        Print colorized output when variable is displayed in IPython, ie. on a line by
        itself.

        Example::

            In [1]: x

        """
        # see https://ipython.org/ipython-doc/stable/api/generated/IPython.lib.pretty.html
        s = str(self).split('\n')
        p.begin_group(4, self.__class__.__name__ + ':' +  s[0])
        p.break_()
        for i, s in enumerate(s[1:]):
            p.text(s)
            if i < len(s) - 2:
                p.break_()
        p.end_group(4, '')

    def __str__(self):
        """
        Pretty string representation of pose (superclass method)

        :return: readable representation of the pose
        :rtype: str

        Convert the pose's matrix value to a simple grid of numbers.

        Example::

            >>> x = SE3.Rx(0.3)
            >>> print(x)
               1           0           0           0            
               0           0.955336   -0.29552     0            
               0           0.29552     0.955336    0            
               0           0           0           1 

        Notes:

            - By default, the output is colorised for an ANSI terminal console:

                * red: rotational elements
                * blue: translational elements
                * white: constant elements

        """
        return self._string(color=True)

    def _string(self, color=False, tol=500):
        """
        Pretty print the matrix value

        :param color: colorise the output, defaults to False
        :type color: bool, optional
        :param tol: zero values smaller than tol*eps, defaults to 10
        :type tol: float, optional
        :return: multiline matrix representation
        :rtype: str

        Convert a matrix to a simple grid of numbers with optional
        colorization for an ANSI terminal console:

                * red: rotational elements
                * blue: translational elements
                * white: constant elements

        Example::

            >>> x = SE3.Rx(0.3)
            >>> print(str(x))
               1           0           0           0            
               0           0.955336   -0.29552     0            
               0           0.29552     0.955336    0            
               0           0           0           1 

        """
        #print('in __str__', _color)
        
        if _color:
            # bgcol = bg('grey_93')
            bgcol = ''
            trcol = fg('blue')
            rotcol = fg('red')
            constcol = fg('grey_50')
            reset = attr(0)
            indexcol = bg('yellow_2')
        else:
            bgcol = ''
            trcol = ''
            rotcol = ''
            constcol = ''
            reset = ''

        def mformat(self, X):
            # X is an ndarray value to be display
            # self provides set type for formatting
            out = ''
            n = self.N  # dimension of rotation submatrix
            for rownum, row in enumerate(X):
                rowstr = '  '
                # format the columns
                for colnum, element in enumerate(row):
                    if sym.issymbol(element):
                        s = '{:<12s}'.format(str(element))
                    else:
                        if tol > 0 and abs(element) < tol * _eps:
                            element = 0
                        s = '{:< 12g}'.format(element)

                    if rownum < n:
                        if colnum < n:
                            # rotation part
                            s = rotcol + bgcol + s + reset
                        else:
                            # translation part
                            s = trcol + bgcol + s + reset
                    else:
                        # bottom row
                        s = constcol + bgcol + s + reset
                    rowstr += s
                out += rowstr + bgcol + '  ' + reset + '\n'
            return out

        output_str = ''

        if len(self.data) == 0:
            output_str = '[]'
        elif len(self.data) == 1:
            # single matrix case
            output_str = mformat(self, self.A)
        else:
            # sequence case
            for count, X in enumerate(self.data):
                # add separator lines and the index
                output_str += indexcol + '[{:d}] ='.format(count) + reset \
                    + '\n' + mformat(self, X)

        return output_str

    # ----------------------- graphics

    def plot(self, *args, **kwargs):
        """
        Plot pose object as a coordinate frame (superclass method)

        :param `**kwargs`: plotting options

        - ``X.plot()`` displays the pose ``X`` as a coordinate frame in either
          2D or 3D.  There are many options, see the links below.

        Example::

            >>> X = SE3.Rx(0.3)
            >>> X.plot(frame='A', color='green')

        :seealso: :func:`~spatialmath.base.transforms3d.trplot`, :func:`~spatialmath.base.transforms2d.trplot2`
        """
        if self.N == 2:
            tr.trplot2(self.A, *args, **kwargs)
        else:
            tr.trplot(self.A, *args, **kwargs)

    def animate(self, *args, start=None, **kwargs):
        """
        Plot pose object as an animated coordinate frame (superclass method)

        :param start: initial pose, defaults to null/identity
        :type start: same as ``self``
        :param `**kwargs`: plotting options

        - ``X.animate()`` displays the pose ``X`` as a coordinate frame moving
          from the origin in either 2D or 3D.  There are many options, see the 
          links below.
        - ``X.animate(*args, start=X1)`` displays the pose ``X`` as a coordinate
          frame moving from pose ``X1``, in either 2D or 3D.  There are 
          many options, see the links below.

        Example::

            >>> X = SE3.Rx(0.3)
            >>> X.animate(frame='A', color='green')
            >>> X.animate(start=SE3.Ry(0.2))

        :seealso: :func:`~spatialmath.base.transforms3d.tranimate`, :func:`~spatialmath.base.transforms2d.tranimate2`
        """
        if start is not None:
            start = start.A
        if self.N == 2:
            tr.tranimate2(self.A, start=start, *args, **kwargs)
        else:
            tr.tranimate(self.A, start=start, *args, **kwargs)


# ------------------------------------------------------------------------ #
    def prod(self):
        r"""
        Product of elements (superclass method)

        :return: Product of elements
        :rtype: pose instance

        ``x.prod()`` is the product of the values held by ``x``, ie.
        :math:`\prod_i^N T_i`.

        Example::

            >>> x = SE3.Rx([0, 0.1, 0.2, 0.3])
            >>> x.prod()
            SE3(array([[ 1.        ,  0.        ,  0.        ,  0.        ],
                       [ 0.        ,  0.82533561, -0.56464247,  0.        ],
                       [ 0.        ,  0.56464247,  0.82533561,  0.        ],
                       [ 0.        ,  0.        ,  0.        ,  1.        ]]))
        """
        Tprod = self.__class__._identity()  # identity value
        for T in self.data:
            Tprod = Tprod @ T
        return self.__class__(Tprod)

    def __pow__(self, n):
        """
        Overloaded ``**`` operator (superclass method)

        :param n: exponent
        :type n: int
        :return: pose to the power ``n``
        :rtype: pose instance

        ``X**n`` raise all values held in `X` to the specified power using repeated
        multiplication.  If ``n`` < 0 then the result is inverted.

        Example::

            >>> SE3.Rx(0.1) ** 2
            SE3(array([[ 1.        ,  0.        ,  0.        ,  0.        ],
                       [ 0.        ,  0.98006658, -0.19866933,  0.        ],
                       [ 0.        ,  0.19866933,  0.98006658,  0.        ],
                       [ 0.        ,  0.        ,  0.        ,  1.        ]]))
            >>> SE3.Rx([0, 0.1]) ** 2
            SE3([
            array([[1., 0., 0., 0.],
                   [0., 1., 0., 0.],
                   [0., 0., 1., 0.],
                   [0., 0., 0., 1.]]),
            array([[ 1.        ,  0.        ,  0.        ,  0.        ],
                   [ 0.        ,  0.98006658, -0.19866933,  0.        ],
                   [ 0.        ,  0.19866933,  0.98006658,  0.        ],
                   [ 0.        ,  0.        ,  0.        ,  1.        ]]) ])

        """

        assert type(n) is int, 'exponent must be an int'
        return self.__class__([np.linalg.matrix_power(x, n) for x in self.data], check=False)
    #----------------------- arithmetic


    def __mul__(left, right):  # pylint: disable=no-self-argument
        """
        Overloaded ``*`` operator (superclass method)

        :return: Product of two operands
        :rtype: pose instance
        :raises NotImplemented: for incompatible arguments

        Pose composition, scaling or vector transformation:

        - ``X * Y`` compounds the poses ``X`` and ``Y``
        - ``X * s`` performs element-wise multiplication of the elements of ``X`` by ``s``
        - ``s * X`` performs element-wise multiplication of the elements of ``X`` by ``s``
        - ``X * v`` linear transformation of the vector ``v`` where ``v`` is array-like

        ==============   ==============   ===========  ======================
                   Multiplicands                   Product
        -------------------------------   -----------------------------------
            left             right            type           operation
        ==============   ==============   ===========  ======================
        Pose             Pose             Pose         matrix product
        Pose             scalar           NxN matrix   element-wise product
        scalar           Pose             NxN matrix   element-wise product
        Pose             N-vector         N-vector     vector transform
        Pose             NxM matrix       NxM matrix   transform each column
        ==============   ==============   ===========  ======================

        .. note::

            #. Pose is an ``SO2``, ``SE2``, ``SO3`` or ``SE3`` instance
            #. N is 2 for ``SO2``, ``SE2``; 3 for ``SO3`` or ``SE3``
            #. Scalar x Pose is handled by __rmul__`
            #. Scalar multiplication is commutative but the result is not a group
               operation so the result will be a matrix
            #. Any other input combinations result in a ValueError.

        For pose composition either or both operands may hold more than one value which
        results in the composition holding more than one value according to:

        =========   ==========   ====  ================================
        len(left)   len(right)   len     operation
        =========   ==========   ====  ================================
         1          1             1    ``prod = left * right``
         1          M             M    ``prod[i] = left * right[i]``
         N          1             M    ``prod[i] = left[i] * right``
         M          M             M    ``prod[i] = left[i] * right[i]``
        =========   ==========   ====  ================================

        Example::

            >>> SE3.Rx(pi/2) * SE3.Ry(pi/2)
            SE3(array([[0., 0., 1., 0.],
                    [1., 0., 0., 0.],
                    [0., 1., 0., 0.],
                    [0., 0., 0., 1.]]))
            >>> SE3.Rx(pi/2) * 2
            array([[ 2.0000000e+00,  0.0000000e+00,  0.0000000e+00,  0.0000000e+00],
                   [ 0.0000000e+00,  1.2246468e-16, -2.0000000e+00,  0.0000000e+00],
                   [ 0.0000000e+00,  2.0000000e+00,  1.2246468e-16,  0.0000000e+00],
                   [ 0.0000000e+00,  0.0000000e+00,  0.0000000e+00,  2.0000000e+00]])

        For vector transformation there are three cases:

        =========  ===========  =====  ==========================
              Multiplicands             Product
        ----------------------  ---------------------------------
        len(left)  right.shape  shape  operation
        =========  ===========  =====  ==========================
        1          (N,)         (N,)   vector transformation
        M          (N,)         (N,M)  vector transformations
        1          (N,M)        (N,M)  column transformation
        =========  ===========  =====  ==========================

        .. note:: For the ``SE2`` and ``SE3`` case the vectors are converted to homogeneous
                  form, transformed, then converted back to Euclidean form.

        Example:: 

            >>> SE3.Rx(pi/2) * [0, 1, 0]
            array([0.000000e+00, 6.123234e-17, 1.000000e+00])
            >>> SE3.Rx(pi/2) * np.r_[0, 0, 1]
            array([ 0.000000e+00, -1.000000e+00,  6.123234e-17])
        """
        if isinstance(left, right.__class__):
            #print('*: pose x pose')
            return left.__class__(left._op2(right, lambda x, y: x @ y), check=False)

        elif isinstance(right, (list, tuple, np.ndarray)):
            #print('*: pose x array')
            if len(left) == 1 and argcheck.isvector(right, left.N):
                # pose x vector
                #print('*: pose x vector')
                v = argcheck.getvector(right, out='col')
                if left.isSE:
                    # SE(n) x vector
                    return tr.h2e(left.A @ tr.e2h(v))
                else:
                    # SO(n) x vector
                    return left.A @ v

            elif len(left) > 1 and argcheck.isvector(right, left.N):
                # pose array x vector
                #print('*: pose array x vector')
                v = argcheck.getvector(right)
                if left.isSE:
                    # SE(n) x vector
                    v = tr.e2h(v)
                    return np.array([tr.h2e(x @ v).flatten() for x in left.A]).T
                else:
                    # SO(n) x vector
                    return np.array([(x @ v).flatten() for x in left.A]).T

            elif len(left) == 1 and isinstance(right, np.ndarray) and left.isSO and right.shape[0] == left.N:
                # SO(n) x matrix
                return left.A @ right
            elif len(left) == 1 and isinstance(right, np.ndarray) and left.isSE and right.shape[0] == left.N:
                # SE(n) x matrix
                return tr.h2e(left.A @ tr.e2h(right))
            elif isinstance(right, np.ndarray) and left.isSO and right.shape[0] == left.N and len(left) == right.shape[1]:
                # SO(n) x matrix
                return np.c_[[x.A @ y for x, y in zip(right, left.T)]].T
            elif isinstance(right, np.ndarray) and left.isSE and right.shape[0] == left.N and len(left) == right.shape[1]:
                # SE(n) x matrix
                return np.c_[[tr.h2e(x.A @ tr.e2h(y)) for x, y in zip(right, left.T)]].T
            else:
                raise ValueError('bad operands')
        elif argcheck.isscalar(right):
            return left._op2(right, lambda x, y: x * y)
        else:
            return NotImplemented

    def __rmul__(right, left):  # pylint: disable=no-self-argument
        """
        Overloaded ``*`` operator (superclass method)

        :return: Product of two operands
        :rtype: pose instance
        :raises NotImplemented: for incompatible arguments

        Left-multiplication by a scalar

        - ``s * X`` performs elementwise multiplication of the elements of ``X`` by ``s``

        Notes:

        #. For other left-operands return ``NotImplemented``.  Other classes
          such as ``Plucker`` and ``Twist`` implement left-multiplication by
          an ``SE3`` using their own ``__rmul__`` methods.

        """
        if argcheck.isscalar(left):
            return right.__mul__(left)
        else:
            return NotImplemented


    def __truediv__(left, right):  # pylint: disable=no-self-argument
        """
        Overloaded ``/`` operator (superclass method)

        :return: Product of right operand and inverse of left operand
        :rtype: pose instance or NumPy array
        :raises ValueError: for incompatible arguments

        Pose composition or scaling:

        - ``X / Y`` compounds the poses ``X`` and ``Y.inv()``
        - ``X / s`` performs elementwise multiplication of the elements of ``X`` by ``s``

        ==============   ==============   ===========  =========================
                   Multiplicands                   Quotient
        -------------------------------   --------------------------------------
            left             right            type           operation
        ==============   ==============   ===========  =========================
        Pose             Pose             Pose         matrix product by inverse
        Pose             scalar           NxN matrix   element-wise division
        ==============   ==============   ===========  =========================

        .. notes::

            #. Pose is ``SO2``, ``SE2``, ``SO3`` or ``SE3`` instance
            #. N is 2 for ``SO2``, ``SE2``; 3 for ``SO3`` or ``SE3``
            #. Scalar multiplication is not a group operation so the result will 
               be a matrix
            #. Any other input combinations result in a ValueError.

        For pose composition either or both operands may hold more than one value which
        results in the composition holding more than one value according to:

        =========   ==========   ====  ================================
        len(left)   len(right)   len     operation
        =========   ==========   ====  ================================
         1          1             1    ``quo = left * right.inv()``
         1          M             M    ``quo[i] = left * right[i].inv()``
         N          1             M    ``quo[i] = left[i] * right.inv()``
         M          M             M    ``quo[i] = left[i] * right[i].inv()``
        =========   ==========   ====  ================================

        """
        if isinstance(left, right.__class__):
            return left.__class__(left._op2(right.inv(), lambda x, y: x @ y), check=False)
        elif argcheck.isscalar(right):
            return left._op2(right, lambda x, y: x / y)
        else:
            raise ValueError('bad operands')

    def __add__(left, right):  # pylint: disable=no-self-argument
        """
        Overloaded ``+`` operator (superclass method)

        :return: Sum of two operands
        :rtype: NumPy ndarray, shape=(N,N)
        :raises ValueError: for incompatible arguments


        Add the elements of two poses.  This is not a group operation so the
        result is a matrix not a pose class.

        - ``X + Y`` is the element-wise sum of the matrix value of ``X`` and ``Y``
        - ``X + s`` is the element-wise sum of the matrix value of ``X`` and scalar ``s``
        - ``s + X`` is the element-wise sum of the scalar ``s`` and the matrix value of ``X``

        ==============   ==============   ===========  ========================
                   Operands                   Sum
        -------------------------------   -------------------------------------
            left             right            type           operation
        ==============   ==============   ===========  ========================
        Pose             Pose             NxN matrix   element-wise matrix sum
        Pose             scalar           NxN matrix   element-wise sum
        scalar           Pose             NxN matrix   element-wise sum
        ==============   ==============   ===========  ========================

        .. note::

            #. Pose is an ``SO2``, ``SE2``, ``SO3`` or ``SE3`` instance
            #. N is 2 for ``SO2``, ``SE2``; 3 for ``SO3`` or ``SE3``
            #. scalar + Pose is handled by :meth:`__radd__`
            #. Addition is commutative
            #. Any other input combinations result in a ``ValueError``.

        For pose addition either or both operands may hold more than one value which
        results in the sum holding more than one value according to:

        =========   ==========   ====  ================================
        len(left)   len(right)   len     operation
        =========   ==========   ====  ================================
         1          1             1    ``sum = left + right``
         1          M             M    ``sum[i] = left + right[i]``
         N          1             M    ``sum[i] = left[i] + right``
         M          M             M    ``sum[i] = left[i] + right[i]``
        =========   ==========   ====  ================================

        """
        # results is not in the group, return an array, not a class
        return left._op2(right, lambda x, y: x + y)

    def __radd__(left, right):  # pylint: disable=no-self-argument
        """
        Overloaded ``+`` operator (superclass method)

        :return: Sum of two operands
        :raises ValueError: for incompatible arguments

        Left-addition by a scalar

        - ``s + X`` performs elementwise addition of the elements of ``X`` and ``s``

        :seealso: :meth:`__add__`
        """
        return left.__add__(right)

    # def __iadd__(left, right):
    #     return left.__add__(right)

    def __sub__(left, right):  # pylint: disable=no-self-argument
        """
        Overloaded ``-`` operator (superclass method)

        :return: Difference of two operands
        :return: matrix
        :rtype: numpy ndarray, shape=(N,N)
        :raises ValueError: for incompatible arguments


        Subtract elements of two poses.  This is not a group operation so the
        result is a matrix not a pose class.

        - ``X - Y`` is the element-wise difference of the matrix value of ``X`` and ``Y``
        - ``X - s`` is the element-wise difference of the matrix value of ``X`` and the scalar ``s``
        - ``s - X`` is the element-wise difference of the scalar ``s`` and the matrix value of ``X``

        ==============   ==============   ===========  ==============================
                   Operands                   Sum
        -------------------------------   -------------------------------------------
            left             right            type           operation
        ==============   ==============   ===========  ==============================
        Pose             Pose             NxN matrix   element-wise matrix difference
        Pose             scalar           NxN matrix   element-wise sum
        scalar           Pose             NxN matrix   element-wise sum
        ==============   ==============   ===========  ==============================

        .. note::

            #. Pose is ``SO2``, ``SE2``, ``SO3`` or ``SE3`` instance
            #. N is 2 for ``SO2``, ``SE2``; 3 for ``SO3`` or ``SE3``
            #. scalar - Pose is handled by :meth:`__rsub__`
            #. Any other input combinations result in a ``ValueError``.

        For pose subtraction either or both operands may hold more than one value which
        results in the difference holding more than one value according to:

        =========   ==========   ====  ================================
        len(left)   len(right)   len     operation
        =========   ==========   ====  ================================
         1          1             1    ``diff = left - right``
         1          M             M    ``diff[i] = left - right[i]``
         N          1             M    ``diff[i] = left[i] - right``
         M          M             M    ``diff[i] = left[i]  right[i]``
        =========   ==========   ====  ================================
        """

        # results is not in the group, return an array, not a class
        # TODO allow class +/- a conformant array
        return left._op2(right, lambda x, y: x - y)

    def __rsub__(left, right):  # pylint: disable=no-self-argument
        """
        Overloaded ``-`` operator (superclass method)

        :return: Difference of two operands
        :raises ValueError: for incompatible arguments

        Left-addition by a scalar

        - ``s - X`` performs elementwise addition of the elements of ``X`` and ``s``

    :seealso: :meth:`__sub__`
        """
        return -left.__sub__(right)

    # def __isub__(left, right):
    #     return left.__sub__(right)

    def __eq__(left, right):  # pylint: disable=no-self-argument
        """
        Overloaded ``==`` operator (superclass method)

        :return: Equality of two operands
        :rtype: bool or list of bool

        Test two poses for equality

        ``X == Y`` is true of the poses are of the same type and numerically
        equal.

        If either or both operands may hold more than one value which
        results in the equality test holding more than one value according to:

        =========   ==========   ====  ================================
        len(left)   len(right)   len     operation
        =========   ==========   ====  ================================
         1          1             1    ``eq = left == right``
         1          M             M    ``eq[i] = left == right[i]``
         N          1             M    ``eq[i] = left[i] == right``
         M          M             M    ``eq[i] = left[i] == right[i]``
        =========   ==========   ====  ================================

        """
        assert type(left) == type(right), 'operands to == are of different types'
        return left._op2(right, lambda x, y: np.allclose(x, y))

    def __ne__(left, right):  # pylint: disable=no-self-argument
        """
        Overloaded ``!=`` operator (superclass method)

        :return: Inequality of two operands
        :rtype: bool or list of bool

        Test two poses for inequality

        - ``X != Y`` is true of the poses are of the same type but not numerically
          equal.

        If either or both operands may hold more than one value which
        results in the inequality test holding more than one value according to:

        =========   ==========   ====  ================================
        len(left)   len(right)   len     operation
        =========   ==========   ====  ================================
         1          1             1    ``ne = left != right``
         1          M             M    ``ne[i] = left != right[i]``
         N          1             M    ``ne[i] = left[i] != right``
         M          M             M    ``ne[i] = left[i] != right[i]``
        =========   ==========   ====  ================================

        """
        return [not x for x in left == right]

    def _op2(left, right, op):  # pylint: disable=no-self-argument
        """
        Perform binary operation

        :param left: left side of comparison
        :type self: SO2, SE2, SO3, SE3
        :param right: right side of comparison
        :type self: SO2, SE2, SO3, SE3
        :param op: binary operation
        :type op: callable
        :raises ValueError: arguments are not compatible
        :return: list of matrices
        :rtype: list

        Peform a binary operation on a pair of operands.  If either operand
        contains a sequence the results is a sequence accordinging to this
        truth table.

        =========   ==========   ====  ================================
        len(left)   len(right)   len     operation
        =========   ==========   ====  ================================
         1          1             1    ``ret = op(left, right)``
         1          M             M    ``ret[i] = op(left, right[i])``
         N          1             M    ``ret[i] = op(left[i], right)``
         M          M             M    ``ret[i] = op(left[i], right[i])``
        =========   ==========   ====  ================================

        """

        if isinstance(right, left.__class__):
            # class by class
            if len(left) == 1:
                if len(right) == 1:
                    #print('== 1x1')
                    return op(left.A, right.A)
                else:
                    #print('== 1xN')
                    return [op(left.A, x) for x in right.A]
            else:
                if len(right) == 1:
                    #print('== Nx1')
                    return [op(x, right.A) for x in left.A]
                elif len(left) == len(right):
                    #print('== NxN')
                    return [op(x, y) for (x, y) in zip(left.A, right.A)]
                else:
                    raise ValueError('length of lists to == must be same length')
        elif argcheck.isscalar(right) or (isinstance(right, np.ndarray) and right.shape == left.shape):
            # class by matrix
            if len(left) == 1:
                return op(left.A, right)
            else:
                return [op(x, right) for x in left.A]

if __name__ == "__main__":
    from spatialmath import SE3
    x = SE3.Rand(N=6)

    print(x)