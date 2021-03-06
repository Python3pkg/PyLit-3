#!/usr/bin/env python
# -*- coding: utf8 -*-

# ************************************
# Extending Iterators for use as Queue
# ************************************
#
# :Version:   0.2
# :Date:      2007-01-15
# :Copyright: 2005, 2007 Guenter Milde.
#             Released under the terms of the GNU General Public License
#             (v. 2 or later)
# :Changelog: 2005-06-29 Initial version
#             2007-01-07 literate version, more examples
# :Abstract:  There are many variants of "rich iterators" with varying
#             efficiency, conventions, naming, and behaviour. This survey will
#             compare them and provide a case for the inclusion of a "rich
#             iterator wrapper" to the Python Standard Library
#
# .. contents::
#
# ::

"""iterqueue: mutable iterators

Classes for "extended iterators" with methods to let iterators be used as
queue

   `push` or
   `append left`     -- push back values
   `peek`           -- get a value without "using it up"
   `__bool__`    -- test for empty iterator

"""

# Imports
#
# The `itertools` module provides a set of building blocks for the work with
# iterators (but misses a class for "mutable" iterators). ::

import itertools

# The `collections` module with the efficient double-sided queue was
# introduced in Python 2.4. The following construct provides a minimal
# compatibility definition if it is not available::

try:
    from collections import deque
except ImportError:
    class deque(list):
        def appendleft(self, value):
            self.insert(0, value)


# Iterables and Iterators
# =======================
#
# Iterables and iterators are defined by the iterator protocol as laid out in
# the section on `Iterator Types`_ in the Python Library Reference`:
#
# Iterables:
#   One method needs to be defined for container objects to provide iteration
#   support:
#
#   :__iter__(): Return an iterator object. [...] If a container supports
#                different types of iteration, additional methods can be
#                provided to specifically request iterators for those
#                iteration types. [...]
#
# ::

def is_iterable(object):
    """Check if the argument is iterable"""
    return hasattr(object, "__iter__") and is_iterator(iter(object))

# Iterators:
#   The *iterator objects* themselves are required to support the following
#   two methods, which together form the *iterator protocol*:
#
#   :__iter__(): Return the iterator object itself. This is required to allow
#                both containers and iterators to be used with the `for` and
#                `in` statements...
#
#   :__next__(): Return the next item from the container. If there are no further
#            items, raise the `StopIteration` exception.
#
#            [...] once an iterator's next() method raises `StopIteration`,
#            it will continue to do so on subsequent calls. Implementations
#            that do not obey this property are deemed broken.
#
# Check if an object is a Python3 iterator.
# For Python 3, we *should* use ABC's: `collections.Iterator` as a superclass
# ::

def is_iterator(object):
    """check if the argument is an iterator"""
    if not hasattr(object, "__iter__"):
        return False
    return (object.__iter__() is object) and hasattr(object, "__next__")


# Try it:
#
#   >>> import iterqueue
#   >>> iterqueue.is_iterator(23)
#   False
#   >>> iterqueue.is_iterator(iter(range(3)))
#   True
#
# The iterator protocol was primarily designed to be the *minimum* necessary
# to work in `for statements`, translating (behind the scene)::

# |  for item in iterable:
# |      <statements>
#
# into the equivalent of::

# |  iterator = iter(iterable)
# |  while 1:
# |    try:
# |          item = next(iterator)
# |    except StopIteration: break
# |          <statements>
#
#
# To add iterator behaviour to your classes, define an `__iter__` method which
# returns an object with a `__next__` method.  If the class defines `__next__`, then
# `__iter__` can just return `self`.  (`tutorial chapter on iterators`_)
#
# Python's *generators* provide a convenient way to implement the iterator
# protocol. Generator objects are returned by *generator functions* (functions
# with the ``yield`` keyword, new in 2.3) and *generator expressions* (new in
# 2.4).
#
# .. _`Iterator Types`:
#    http://docs.python.org/library/stdtypes.html#iterator-types
# .. _`tutorial chapter on iterators`:
#    http://docs.python.org/tutorial/classes.html#iterators
#
# Limitations of iterator objects
# ===============================
#
# Most built-in Python iterator objects (including generator objects) are
# non-mutable (except the call to the `__next__` method). They "produce the data
# just in time", which is fast and memory efficient.
#
# However:
#
# 1. In some occasions, it is important to
#
#    * find out whether an iterator is empty or
#    * to "peek" at a data value
#
#    without advancing the iterator.
#
# 2. In a state machine, an iterator holding the input values can be passed
#    around to the state handling functions. If a state handler realises that
#    a value should be processed by another state handler, it needs to
#    "push it back".
#
# 3. One might want modify the object iterated over in a `for` statement.
#
#    Generally, the object in a `for` statement can not be changed inside the
#    loop.
#
#      >>> from collections import deque
#      >>> it = deque(range(3))
#      >>> for v in it:
#      ...     print( v, sep=',')
#      ...     if v == 1:
#      ...        it.appendleft("eins")
#      ...
#      Traceback (most recent call last):
#        File "doctest.py", line 1248, in __run
#          compileflags, 1) in test.globs
#        File "<doctest iterqueue.py.txt[8]>", line 1, in ?
#          for v in it:
#      RuntimeError: deque mutated during iteration
#
# Pushing the limits
# ====================
#
# There are many ways to live with the limits of iterators. Most often it
# helps to get a true understanding of their nature and try to count for it in
# the code.  However, the "never ending" discussion and varying recipes for
# enhanced iterators show the ongoing public demand. This is why I argue for
# the inclusion of a 'rich iterator' wrapper class into the standard library
# based on the _`standardisation argument` in the itertools_ module.
#
#   Standardisation helps avoid the readability and reliability problems which
#   arise when many different individuals create their own slightly varying
#   implementations, each with their own quirks and naming conventions.
#
#
# .. _itertools: http://docs.python.org/library/itertools.html
#
# Recode to work with iterators as they are
# -----------------------------------------
#
# The most straightforward way is to translate code like
#
#   >>> def print_first(l):
#   ...     if not l:
#   ...         print( "list empty" )
#   ...     else:
#   ...         print( l[0] )
#   ...
#   >>> print_first([1, 2])
#   1
#   >>> print_first([])
#   list empty
#
# into something in the line of
#
#   >>> def print_next(it):
#   ...     try:
#   ...         value = next(it)
#   ...     except StopIteration:
#   ...         print( "list empty" )
#   ...     else:
#   ...         print( value )
#   ...
#   >>> print_next(iter([1, 2]))
#   1
#   >>> print_next(iter([]))
#   list empty
#
# In a `for` statement, the `else` keyword can be utilised to call an
# expression (or a block) if the end of the iterator is reached:
#
#   >>> def find_five(iterable):
#   ...     for i in iterable:
#   ...         if i == 5:
#   ...             print( "5 found" )
#   ...             break
#   ...     else:
#   ...         print( "5 not found" )
#
# If the loop is aborted, the else clause is skipped
#
#   >>> find_five(range(7))
#   5 found
#
# Otherwise it prints its message:
#
#   >>> find_five(range(3))
#   5 not found
#
# However, there might be cases where this is not applicable and a test for
# the emptiness or a peek at the first value without advancing the iterator
# would enable much cleaner code.
#
# Use a container object
# ----------------------
#
# One could wrap e.g. a generator into a `list` or `collections.deque` to add
# random access as well as extensibility.
#
#   >>> que = deque(range(3))
#   >>> que.appendleft("foo")
#   >>> print( que )
#   deque(['foo', 0, 1, 2])
#
# However, it will put all iterator values into memory which becomes a problem
# for large iterators (and is non-feasible for unlimited iterators).
#
# Also, iterating in a `for` statement will loose the rich behaviour. Instead
# a construct with a `while` statement is needed, e.g:
#
#   >>> que = deque(range(3))
#   >>> while que:
#   ...     v = que.popleft()
#   ...     print( v, end=',' )
#   ...     if v == 1:
#   ...        que.appendleft("eins")
#   ...
#   0,1,eins,2,
#
# Use a rich iterator
# -------------------
#
# If the argument of a `for` statement is an iterator (whose `__iter__`
# method returns `self`), it is available unchanged inside the loop. A *rich
# iterator* provides additional methods besides the ones required for the
# iterator protocol.
#
# State Reporting Iterator
# ~~~~~~~~~~~~~~~~~~~~~~~~
#
# An iterator that returns an indicator "full or empty" (values waiting or
# not) when converted to Boolean will be called *state reporting iterator*::

def is_state_reporting(object):
    return hasattr(object, "__bool__") or hasattr(object, "__len__")

# Peekable Iterator
# ~~~~~~~~~~~~~~~~~
#
# An iterator that provides a `peek` method will be called a
# *peekable iterator*::

def is_peekable(object):
    return hasattr(object, "peek")


# Push Iterator
# ~~~~~~~~~~~~~
#
# An iterator that provides for push-back will be called *push-iterator*::

def is_pushable(object):
    return hasattr(object, "appendleft") or hasattr(object, "push")

# Push iterators can be easily extended with `peek` and test of emptiness
# (see `PushIterator`_).
#
# Iterator Queue
# ~~~~~~~~~~~~~~
# An iterator that also provides methods for appending and extending will be
# called *iterator_queue*.
#
# Methods that need access from the "right" side or knowledge of the length of
# the iterator are not included in the iterator_queue specification as they
# clash with the "just in time" acquisition of the values that give iterators
# time and memory advantage over sequences. ::

def is_iterator_queue(object):
    return (is_state_reporting(object)
            and hasattr(object, "append")
            and hasattr(object, "appendleft")
            and hasattr(object, "extend")
            and hasattr(object, "extendleft")
            and hasattr(object, "clear")
            and hasattr(object, "rotate")
           )

# Rich iterator examples
# ======================
#
# The following examples are the result of a net survey and own ideas.
# The will be compared and profiled in this paper.
#
# All of them are iterator-wrappers::

def is_iterator_wrapper(obj):
    """Try if obj can wrap an iterator"""
    try:
        it = obj(list(range(1)))
    except:
        return False
    try:
        return is_iterator(it)
    except:
        return False

# Xiterwrapper
# ------------
#
# Tom Andersson suggested in the Python list an `xiterable protocol`__ for
# extended iterables and a wrapper to convert a "traditional" iterator to an
# extended version
#
# __ http://mail.python.org/pipermail/python-list/2006-January/360162.html
#
# ::

def xiter(iterable):
    if (hasattr(iterable, "__xiter__")):
        return iterable.__xiter__()
    else:
        return xiterwrapper(iter(iterable))

class xiterwrapper(object):
    def __init__(self, it):
        self.it = it
        self.advance()
    def hasNext(self):
        return hasattr(self, "_next")
    def __next__(self):
        try:
            cur = self._next
            self.advance()
            return cur
        except AttributeError:
            raise StopIteration
    def peek(self):
        try:
            return self._next
        except AttributeError:
            raise StopIteration
    def advance(self):
        try:
            self._next = next(self.it)
        except StopIteration:
            if (hasattr(self, "_next")):
                del self._next
    def __xiter__(self):
        return self
    def __iter__(self):
        return self

# Usage
# ~~~~~
#
#   >>> import iterqueue
#   >>> it = iterqueue.xiter(range(3))
#   >>> iterqueue.is_iterator(it)
#   True
#   >>> iterqueue.is_peekable(it)
#   True
#   >>> iterqueue.is_pushable(it)
#   False
#
# We add the __bool__ method for a non-destructive test of waiting values
# to add the state reporting feature::

    __bool__ = hasNext

# >>> iterqueue.is_state_reporting(it)
# True
#
# Adding a `push` method is not possible without major changes to the code.
#
# IteratorWrapper BFL
# -------------------
#
# In a `post on python-3000`__ Guido van Rossum argued against inclusion of an
# "emptiness" test in the iterator protocol, as  "that's just not something
# that generators can be expected to support" and hence would exclude
# generators from the definition of an iterator.
#
# __ http://mail.python.org/pipermail/python-3000/2006-March/000058.html
#
#    ... you can always write a helper class that takes an iterator and
#    returns an object that represents the same iterator, but sometimes
#    buffers one element. But the buffering violates the coroutine-ish
#    properties of generators, so it should not be the only (or even the
#    default) way to access generators.
#    ...
#
#    Here's a sample wrapper (untested)
#
# ::

class IteratorWrapperBFL(object):
    def __init__(self, it):
        self.it = iter(it)
        self.buffer = None
        self.buffered = False
        self.exhausted = False
    def __iter__(self):
        return self
    def __next__(self):
        if self.buffered:
            value = self.buffer
            self.buffered = False
            self.buffer = None
            return value
        if self.exhausted:
            raise StopIteration()
        try:
            return next(self.it)
        except StopIteration:
            self.exhausted = True
            raise
    def __bool__(self):
        if self.buffered:
            return True
        if self.exhausted:
            return False
        try:
            self.buffer = next(self.it)
        except StopIteration:
            self.exhausted = True
            return False
        self.buffered = True
        return True

# This example provides an "emptiness" test but no peek or push-back:
#
# >>> it = iterqueue.IteratorWrapperBFL(range(3))
# >>> iterqueue.is_state_reporting(it)
# True
#
# Peeking could be easily added, though::

    def peek(self):
        self.buffer = next(self)
        self.buffered = True
        return self.buffer

# >>> iterqueue.is_peekable(it)
# True
#
# IteratorWrapper DD
# ------------------
#
# Daniel Dittmar wrote on Di 22 Jul. 2003 on comp.lang.python
#
# It shouldn't be too difficult to write an iterator wrapper class that does
# exactly what you want (not tested)::

class IteratorWrapperDD:
    def __init__ (self, iterArg):
        iterArg = iter (iterArg)
        try:
            self.firstElement = next(iterArg)
            self.isEmpty = false
            self.__next__ = self.returnFirstElement
            self.baseIter = iterArg
        except StopIteration:
            self.isEmpty = true
            self.__next__ = self.throwStopIteration

    def returnFirstElement(self):
        self.__next__ = self.baseIter.__next__
        return self.firstElement

    def throwStopIteration(self):
        raise StopIteration


# PushIterator
# ------------
#
# In the slides to the `Effective Python Programming`_ OSCON 2005 tutorial by
# Anthony Baxter, I found a genially simple example for an iterator with a
# `push` method.
#
# .. _`Effective Python Programming`:
#    http://www.interlink.com.au/anthony/tech/talks/OSCON2005/effective_r27.pdf
#
# ::

class PushIterator:
    def __init__(self, iterable):
        """Store iterator as data argument and set up cache"""
        self.it = iter(iterable)
        self.cache = []

    def __iter__(self):
        return self

    def __next__(self):
        """Return next value (from cache or iterator)"""
        if self.cache:
            return self.cache.pop()
        return next(self.it)

    def push(self, value):
        """Push back one value (will become the `next` value)"""
        self.cache.append(value)

# Once `push` is defined, it is easy to add `peek` and `__bool__`.
#
# The question arises, what should be returned by `peek()` if the iterator is
# empty. The easiest option is to raise `StopIteration`, but this might come
# unhandy in some cases. My proposal is to add an optional `default` argument,
# which is returned in case the iterator is empty. (As there is no sensible
# default value for the `default` argument, it cannot be implemented as
# keyword arg, instead an argument list is used)::

    def peek(self, *defaults):
        """Return next value but do not advance the iterator"""
        try:
            value = next(self)
        except StopIteration:
            if defaults:
                return defaults[0]
            raise
        self.push(value)
        return value

    def __bool__(self):
        """Test whether the iterator is empty"""
        try:
            self.peek()
        except StopIteration:
            return False
        return True

# An alias makes the class more compatible with `collections.deque` ::

    appendleft = push

# Optimisation of `peek` and `__bool__` is is left out in favour of
# improved clarity.
#
# Usage
# ~~~~~
#
# Create an instance from an iterable object:
#
#   >>> it = iterqueue.PushIterator(range(4))
#
# Test for values:
#
#   >>> bool(it)
#   True
#
# Have a peek ...
#
#   >>> it.peek(None)
#   0
#
# the value is still there:
#
#   >>> next(it)
#   0
#
# See what is left
#
#   >>> [i for i in it]
#   [1, 2, 3]
#
# It should be empty now:
#
#   >>> bool(it)
#   False
#
# So a peek will return the default:
#
#   >>> print( it.peek(None) )
#   None
#
# PushIt
# -------------
#
# The wrapping of an iterator in a class leads to performance loss, as every
# call to `next()` is a relatively costly function call.
#
# Remapping of self.__next__ leads to a more more efficient implementation
# of the PushIterator for the case that `peek` or `push` is called far
# less frequently than `__next__` ('normal' iterating with occasional peek or
# backtrack).  ::

class PushIt(PushIterator):
    def __init__(self, iterable):
        self.it = iter(iterable)
        self.cache = []
        self.__next__ = self.it.__next__

    def _next(self):
        """Return next element. Try cache first."""
        if self.cache:
            return self.cache.pop()
        self.__next__ = self.it.__next__
        return next(self)

    def push(self, value):
        """Push back one value to the iterator"""
        self.cache.append(value)
        self.__next__ = self._next

    def peek(self):
        """Return next value but do not advance the iterator"""
        if self.cache:
            return self.cache[-1]
        value = next(self.it)
        self.push(value)
        return value


# IterQueue
# ---------
#
# The `IterQueue` class adds iterator behaviour to a double-ended queue::

class IterQueue(deque):
    """Iterator object that is also a queue"""
    def __iter__(self):
        return self
    def __next__(self):
        try:
            return self.popleft()
        except IndexError:
            raise StopIteration
    #
    def peek(self):
        """Return next value but do not advance the iterator"""
        value = next(self)
        self.appendleft(value)
        return value


# Usage
# ~~~~~
#
# Creating an instance wraps an iterable in an iterator queue
#
#   >>> it = iterqueue.IterQueue(range(3))
#
# which is an iterator according to the iterator protocol with "queue"
# methods
#
#   >>> iterqueue.is_iterator_queue(it)
#   True
#
# We can test whether there is data in the iterator or get the length of it:
#
#   >>> bool(it)
#   True
#   >>> len(it)
#   3
#
# It is possible to modify this iterator in the middle of a `for` statement:
#
#   >>> for v in it:
#   ...     print( v, end=',' )
#   ...     if v == 1:
#   ...        it.appendleft("eins")
#   ...
#   0,1,eins,2,
#
# As iteration is done on the object itself and not on a copy, it is exhausted
# now:
#
#   >>> print( it )
#   IterQueue([])
#
# (the iterator advertises itself as `deque`, as we did not override the
# `__str__` method)
#
# We can make up for this ::

    def __str__(self):
        return "{0}({1})".format( self.__class__.__name__, list(self) )

# but there might be other problems left...
#
#
# Problems
# ~~~~~~~~
#
# Converting an iterable to a `collections.deque` object creates a list of all
# values in the memory, loosing the memory saving advantages of generator
# objects with "just in time" production of the data.
#
# Printing (and probably other uses as well) "use up" the iterator
#
#   >>> it = iterqueue.IterQueue(range(3))
#   >>> print( it )
#   IterQueue([0, 1, 2])
#   >>> print( it )
#   IterQueue([])
#
#
# IQueue
# ------
#
# The following class implements an iterator queue that is
#
# * memory efficient, as generators are kept as generators
#
# * mostly compatible to `collections.deque` (offering all methods of a
#   `deque` for appends)
#
# It does not offer
#
# * random access to the values, nor
#
# * pop from the right end,
#
# as this would require to convert the iterator to a sequence loosing the
# memory-saving advantage.
#
# Iterating over instances is less fast, as the __next__() method is redefined
# (a function call is needed for every step). Implementing in C would help
# to improve speed.
#
# But,
#
#     itertools.queue() was rejected because it didn't fit naturally into
#     applications -- you had to completely twist your logic around just to
#     accommodate it.  Besides, it is already simple to iterate over a list
#     while appending items to it as needed.
#
#     -- Raymond Hettinger 03-13-05 http://www.codecomments.com/message423138.html
#
# However, both, the speed increase as well as the `standardisation argument`_
# given for the `itertools` hold also in this case
# Maybe IQueue should become a collections candidate?
#
# ::

class IQueue:
    """Iterator with "on-line extensibility"

    An iterator with methods to append or extend it from left or right
    (even while the iterator is in use).

    Can be conceived as a mixture of `itertools.chain` and
    `collections.deque`.

    As `__next__` is redefined, there is a performance loss when iterating
    over large iterators.
    """

    def __init__(self, *iterables):
        """Convert `iterables` to a queue object"""
        self.iterators = deque(iterables)
    #
    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                return next(self.iterators[0])
            except AttributeError:      # convert iterable to iterator
                self.iterators[0] = iter(self.iterators[0])
            except StopIteration:       # switch to next iterator
                del(self.iterators[0])
            except IndexError:          # all iterators exhausted
                raise StopIteration
    #
    def append(self, value):
        """append `value` to self

        The value is wrapped in an iterable and
        appended to the queue of iterables
        """
        self.iterators.append(iter((value,)))
    #
    def appendleft(self, value):
        """Prepend one (scalar) value to the iterator.

        The value is wrapped in an iterable and
        inserted at the first position in the list of iterables
        """
        self.iterators.appendleft(iter((value,)))
    #
    def clear(self):
        """Remove all elements from the iterator.
        """
        self.iterators.clear()
    #
    def extend(self, iterable):
        """append `iterable` to self"""
        self.iterators.append(iter(iterable))
    #
    def extendleft(self, iterable):
        """prepend `iterable` to self"""
        self.iterators.appendleft(iter(iterable))
    #
    def peek(self):
        """Return the next value without advancing the iterator

        Yield next value but push back a copy of the result.
        This way you may "peak" at an iterator without loss.

        Raises `StopIteration` if the iterator is empty.
        """
        value = next(self)
        self.iterators.appendleft(iter((value,)))
        return value
    #
    def rotate(self, n=1):
        """append the next `n` values to the end of the iterator

        Similar to `container.deque.rotate`, but
         * negative `n` leads to error
         * a list of the `n` rotated values is returned
        """
        result = list(itertools.islice(self, n))
        self.iterators.append(result)
        return result

    #
    def __repr__(self):
        """Return a string representation"""
        return "IQueue({0!r})".format(self.iterators)
    #
    def  __bool__(self):
        """Test for a non-zero length of the iterator"""
        if len(self.iterators) > 1:
            return True
        try:
            self.peek()
        except StopIteration:
            return False
        return True

# XIter
# -----
#
# The `XIter` class is an optimised version of the `IQueue` for the
# case when appending of a value is a done less frequently than calling `next`.
# It *could* do so by aliasing next to the underlying iterators `next` method in
# case there is only one iterator in the `iterables` chain.
#
# ::

class XIter:
    """'Mutable iterator' class"""
    def __init__(self, *iterables):
        self.iterators = deque(iter(i) for i in iterables)
        #if len(self.iterators) is 1:
        #    self.__next__ = self.iterators[0].__next__
        #else:
        #    self.__next__ = self._next     # iterate over argument
    #
    def __iter__(self): return self        # "I am an iterator!"
    #
    def __next__(self):
        """get next in turn if there are more than one iterators"""
        try:
            return next(self.iterators[0])
        except StopIteration:
            del(self.iterators[0])             # switch to next iterator
            if len(self.iterators) == 0: raise
            #assert len(self.iterators) >= 1
            #if len(self.iterators) is 1:
            #    self.__next__ = self.iterators[0].__next__
            return next(self)
        except IndexError:
            raise StopIteration
    #
    def append(self, element):
        """append `element` to self"""
        self.iterators.append(iter((element,)))
        #self.__next__ = self._next        # iterate over cache
    #
    def appendleft(self, element):
        """prepend `element` to self"""
        self.iterators.appendleft(iter((element,)))
        #self.__next__ = self._next        # iterate over cache
    #
    def extend(self, iterable):
        """append `iterable` to self"""
        self.iterators.append(iter(iterable))
        #self.__next__ = self._next        # iterate over cache
    #
    def extendleft(self, iterable):
        """prepend `iterable` to self"""
        self.iterators.appendleft(iter(iterable))
        #self.__next__ = self._next        # iterate over cache

    #
    def peek(self):
        """Return the next value without advancing the iterator

        Yield next value but push back a copy of the result.
        This way you may "peak" at an iterator without loss.

        Raises `StopIteration` if the iterator is empty.
        """
        value = next(self)
        self.appendleft(value)
        return value
    #
    def rotate(self, n=1):
        """append the next `n` values to the end of the iterator

        Similar to `container.deque.rotate`, but
         * negative `n` leads to error
         * a list of the `n` rotated values is returned
        """
        result = list(itertools.islice(self, n))
        self.iterators.append(result)
        return result

    #
    def __repr__(self):
        """Return a string representation"""
        return "XIter({0!r})".format(self.iterators)
    #
    def __bool__(self):
        """Test for a non-zero length of the iterator"""
        if len(self.iterators) > 1:
            return True
        try:
            self.peek()
        except StopIteration:
            return False
        return True


# Some optimisation could be done adapting a `round-robin example`__ posted by
# R. Hettinger on 2004-04-30 15:58 in comp.lang.python
#
# __ http://sourceforge.net/tracker/index.php?func=detail&aid=756253&group_id=5470&atid=305470
#
# ::

##
# For the record, here a simple and efficient roundrobin task
# server based on collections.deque:
#
# def roundrobin(*iterables):
#     pending = deque( iter(i).__next__ for i in iterables)
#     gettask, scheduletask = pending.popleft, pending.append
#     while pending:
#         task = gettask()
#         try:
#             yield task()
#         except StopIteration:
#             continue
#         scheduletask(task)
#
# for value in roundrobin('abc', 'd', 'efgh'):
#     print( value )


# Do a doctest if the module is run in nosetests::

def test():
    import doctest
    print( "doctest" )
    doctest.testmod( verbose=True )

if __name__ == "__main__":
    test()
