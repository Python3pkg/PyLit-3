#!/usr/bin/env python
# -*- coding: utf8 -*-

# iterqueue_test.py
# *****************
# Test the iterator wrappers from iterqueue.py
# ============================================
#
# Updated for Python3 and to replace nose with unittest.
#
# .. contents::
#
# ::

import sys, itertools
import iterqueue
from iterqueue import *
import unittest

# Get and sort the wrapper classes
# --------------------------------
#
# List all iterator wrapper objects::

wrappers = [obj for obj in list(iterqueue.__dict__.values())
            if is_iterator_wrapper(obj)]
# print( "\n".join(repr(wrapper) for wrapper in wrappers) )

# List iterator wrappers that provide a `peek` method::

peekables = [obj for obj in wrappers if is_peekable(obj)]
# print( "Peekables" )
# print( "\n".join(repr(peekable) for peekable in peekables) )

# List iterator wrappers that provide a `push` method::

pushables = [obj for obj in wrappers if is_pushable(obj)]
# print( "Pushables" )
# print( "\n".join(repr(pushable) for pushable in pushables) )

# List iterator wrappers that provide a test for "values available"::

state_reporters = [obj for obj in wrappers if is_state_reporting(obj)]
# print( "State Reporters" )
# print( "\n".join(repr(state_reporter) for state_reporter in state_reporters) )

# List iterator wrappers that implement the "queue" methods::

iqueues = [obj for obj in wrappers if is_iterator_queue(obj)]
# print( "Iterator Queues" )
# print( "\n".join(repr(iqueue) for iqueue in iqueues) )


# Test Wrappers
# -------------
#
# Test the basic iterator features of an iterator wrapper. ::

class Test_Wrappers( unittest.TestCase ):
    """Test the wrapping of iterator wrappers"""
    def wrap_ok(self, wrapper, base):
        """iterating over the wrapper should return the same
        as iterating over base
        """
        print( wrapper )
        self.assertEqual( list(wrapper(iter(base))), list(base) )
        self.assertEqual( [i for i in wrapper(iter(base))], [i for i in base] )

    def test_wrappers(self, base=list(range(3))):
        for wrapper in wrappers:
            self.wrap_ok( wrapper, base )


# Test Peekables
# --------------
#
# ::

class Test_Peekables( unittest.TestCase ):
    """Test the peek method of iterator wrappers"""
    def peek_ok(self, wrapper, base):
        """peek() should return next value but not advance the iterator"""
        print( wrapper )
        print(( wrapper.peek ))
        it = wrapper(iter(base))
        it.peek()
        first = it.peek()
        print( first )
        self.assertEqual( first, 0 )
        # peek() must not "use up" values
        result = list(it)
        print( result )
        self.assertEqual( result, list(base) )

    def test_peekables(self, base=list(range(3))):
        """Test generator for peekable iterator wrappers"""
        for wrapper in peekables:
            self.peek_ok( wrapper, base )

# Test Pushables
# --------------
#
# ::

class Test_Pushables( unittest.TestCase ):
    """Test the push method of iterator wrappers"""

    def push_ok(self, wrapper, base):
        """push(value) shall prepend `value` to iterator"""
        print(( wrapper.push ))
        it = wrapper(iter(base))
        it.push(9)
        result = list(it)
        print( result )
        self.assertEqual( result, [9] + list(base) )

    def push_while_iterating_ok(self, wrapper):
        """push shall work even in an iteration loop"""
        print( wrapper )
        it = wrapper(iter(list(range(3))))
        result = []
        for i in it:
            if i == 1:
                it.push("xx")
            result.append(i)
        self.assertEqual( result, [0, 1, 'xx', 2] )

    def test_pushables(self, base=list(range(3))):
        """Test generator for pushable iterator wrappers"""
        for wrapper in pushables:
            if not hasattr(wrapper, "push"):
                wrapper.push = wrapper.appendleft
            self.push_ok( wrapper, base )
            self.push_while_iterating_ok( wrapper )


# Test Iterator Queue
# -------------------
#
# ::

class TestIteratorQueue( unittest.TestCase ):
    """Test the queueing methods of iterator queues"""
    #
    def extend_ok(self, wrapper, base):
        """extend(iterable) shall append `iterable` to iterator"""
        print( wrapper )
        it = wrapper(iter(base))
        it.extend([9])
        expected= list(base)+[9] # Exhausts base!
        result= list(it) # Exhausts base, too!
        self.assertEqual( result, expected )

    def extendleft_ok(self, wrapper, base):
        """extendleft(iterable) shall prepend `iterable` to iterator"""
        print( wrapper )
        it = wrapper(iter(base))
        it.extendleft([9])
        result = [i for i in it]
        print( result )
        self.assertEqual( result, [9] + list(base) )

    def append_ok(self, wrapper, base):
        """append(value) shall append `value` to iterator"""
        print( wrapper )
        it = wrapper(iter(base))
        it.append(9)
        result = list(it)
        print( result )
        self.assertEqual( result, list(base) + [9] )

    def test_iqueues(self, base=list(range(3))):
        """Test generator for iterator-queue wrappers"""
        for wrapper in iqueues:
            self.extend_ok( wrapper, base )
            self.extendleft_ok( wrapper, base )
            self.append_ok( wrapper, base )


# Test State Reporters
# --------------------
#
# ::

class Test_StateReporters( unittest.TestCase ):
    """Test the state reporting when converted to bool"""
    def bool_ok(self, wrapper):
        """Empty iterator should evaluate to False
           Non-empty iterator should evaluate to True
           the evaluation should not advance the iterator
           """
        base = list(range(3)) # make sure it is not empty!
        it0 = wrapper(iter([]))
        self.assertFalse( bool(it0) )
        self.assertEqual( list(it0), [] )
        it1 = wrapper(iter(base))
        self.assertTrue( bool(it1) )
        self.assertEqual( list(it1), list(base) )
        self.assertFalse( bool(wrapper(iter([]))) )
        self.assertTrue( bool(wrapper(iter([1]))) )

    def test_iqueues(self):
        """Test generator for iterator-queue wrappers"""
        for wrapper in state_reporters:
            self.bool_ok( wrapper )


if __name__ == "__main__":
    unittest.main()
