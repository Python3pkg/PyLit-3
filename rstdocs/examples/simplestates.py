#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# simplestates.py
# ***************
# Generic state machine class using iterators
# +++++++++++++++++++++++++++++++++++++++++++
#
# :Version:   0.3
# :Date:      2006-12-01
# :Copyright: 2006 Guenter Milde.
#             Released under the terms of the GNU General Public License
#             (v. 2 or later)
#
# Doctest string::

"""Simple generic state machine class using iterators

Usage
=====

Example: A two-state machine sorting numbers in the categories
         "< 3" and ">= 3".

Preparation
-----------

Import the basic class::

>>> from simplestates import SimpleStates

Subclass and add state handlers:

>>> class StateExample(SimpleStates):
...    def high_handler_generator(self):
...        result = []
...        for token in self.data_iterator:
...            if token <= 3:
...                self.state = "low"
...                yield result
...                result = []
...            else:
...                result.append(token)
...        yield result
...    def low_handler_generator(self):
...        result = []
...        for token in self.data_iterator:
...            if token > 3:
...                self.state = "high"
...                yield result
...                result = []
...            else:
...                result.append(token)
...        yield result


Set up an instance of the StateExample machine with some test data::

>>> testdata = [1, 2, 3, 4, 5, 4, 3, 2, 1]
>>> testmachine = StateExample(testdata, state="low")

>>> print( [name for name in dir(testmachine) if name.endswith("generator")] )
['high_handler_generator', 'low_handler_generator']


Running
-------

Iterating over the state machine yields the results of state processing::

>>> for result in testmachine:
...     print( result, end=',' )
...
[1, 2, 3],[5, 4],[2, 1],

For a correct working sort algorithm, we would expect::

  [1, 2, 3] [4, 5, 4] [3, 2, 1]

However, to achieve this a backtracking algorithm is needed. See iterqueue.py
and simplestates-test.py for an example.


The `__call__` method returns a list of results. It is used if you call
an instance of the class::

>>> testmachine()
[[1, 2, 3], [5, 4], [2, 1]]

"""

# Detailed documentation of this class and the design rationales (including
# tested variants) is available in the file simplestates-test.py.txt
#
# This has been revised for Python3.
#
# Abstract State Machine Class
# ============================
#
# ::

class SimpleStates:
    """generic state machine acting on iterable data

    Class attributes:

      state -- name of the current state (next state_handler method called)
      state_handler_generator_suffix -- common suffix of generator functions
                                        returning a state-handler iterator
    """
    state = 'start'
    state_handler_generator_suffix = "_handler_generator"

# Initialisation
# --------------
#
# * sets the data object to the `data` argument.
#
# * remaining keyword arguments are stored as class attributes (or methods, if
#   they are function objects) overwriting class defaults (a neat little trick
#   I found somewhere on the net)
#
#   ..note: This is the same as `self.__dict__.update(keyw)`. However,
#           the "Tutorial" advises to confine the direct use of `__dict__`
#           to post-mortem analysis or the like...
#
# ::

    def __init__(self, data, **keyw):
        """data   --  iterable data object
                      (list, file, generator, string, ...)
           **keyw --  all remaining keyword arguments are
                      stored as class attributes
        """
        self.data = data
        for (key, value) in list(keyw.items()):
            setattr(self, key, value)





# Iteration over class instances
# ------------------------------
#
# The special `__iter__` method returns an iterator. This allows to use
# a  class instance directly in an iteration loop.  We define it as is a
# generator method that sets the initial state and then iterates over the
# data calling the state methods::

    def __iter__(self):
        """Generate and return an iterator

        * ensure `data` is an iterator
        * convert the state generators into iterators
        * (re) set the state attribute to the initial state
        * pass control to the active states state_handler
          which should call and process next(self.data_iterator)
        """
        self.data_iterator = iter(self.data)
        self._initialize_state_generators()
        # now start the iteration
        while True:
            yield getattr(self, self.state)()

# a helper function generates state handlers from generators. It is called by
# the `__iter__` method above::

    def _initialize_state_generators(self):
        """Generic function to initialise state handlers from generators

        functions whose name matches `[^_]<state>_handler_generator` will
        be converted to iterators and their `.__next__()` method stored as
        `self.<state>`.
        """
        suffix = self.state_handler_generator_suffix
        shg_names = [name for name in dir(self)
                      if name.endswith(suffix)
                      and not name.startswith("_")]
        for name in shg_names:
            shg = getattr(self, name)
            setattr(self, name[:-len(suffix)], shg().__next__ )

# Use instances like functions
# ----------------------------
#
# To allow use of class instances as callable objects, we add a `__call__`
# method::

    def __call__(self):
        """Iterate over state-machine and return results as a list"""
        return [token for token in self]

# Command line usage
# ==================
#
# running this script does a doctest::

if __name__ == "__main__":
    import doctest
    doctest.testmod()
