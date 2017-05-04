import functools
class dedupe(object):
   '''Decorator. Caches a function's previous argument and skips calling
    the wrapped fnction if the value the same as last time.
   '''
   def __init__(self, func):
      self.func = func
      self.last_value = None

   def __call__(self, arg):

      if arg == self.last_value:
         return
      else:
         self.last_value = arg
         return self.func(arg)

   def __repr__(self):
      return self.func.__doc__
   def __get__(self, obj, objtype):
      return functools.partial(self.__call__, obj)


@dedupe
def test_func1(arg1):
   print("test_func1: {}".format(arg1))


@dedupe
def test_func2(arg1):
   print("test_func2: {}".format(arg1))

test_func1(1)
test_func1(2)
test_func1(3)
test_func1(3)
test_func1(4)