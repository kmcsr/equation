
import math
import threading
from abc import ABC, abstractmethod

__all__ = [
	'Element', 'Expr', 'Op1Expr', 'Op2Expr',
	'Algebra', 'Number',
	'Neg', 'Add', 'Sub', 'Mul', 'Div'
]

class Element(ABC):
	@staticmethod
	def from_obj(obj):
		if isinstance(obj, Element):
			return obj
		if isinstance(obj, (int, float)):
			return Number(obj)
		if isinstance(obj, str):
			return Algebra(obj)
		raise ValueError(f'Unsupported type: {type(obj)}')

	@property
	@abstractmethod
	def value(self) -> float:
		raise NotImplementedError()

	def round(self) -> int:
		val = self.value
		return math.ceil(val) if val % 1 >= 0.5 else math.floor(val)

	def floor(self) -> int:
		return math.floor(self.value)

	def ceil(self) -> int:
		return math.ceil(self.value)

	def __float__(self) -> float:
		return self.value

	def __int__(self) -> int:
		return int(self.value)

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}>'

	__str__ = __repr__

	@abstractmethod
	def eq(self, other) -> bool:
		raise NotImplementedError()

	def veq(self, other) -> bool:
		return (isinstance(other, self.__class__) and self.eq(other)) or self.value == other.value

	def lt(self, other) -> bool:
		return self.value < other.value

	def __eq__(self, other) -> bool:
		return isinstance(other, self.__class__) and self.eq(other)

	def __ne__(self, other) -> bool:
		return not isinstance(other, self.__class__) or not self.eq(other)

	def __lt__(self, other) -> bool:
		return self.lt(other)

	def __le__(self, other) -> bool:
		return self.veq(other) or self.lt(other)

	def __gt__(self, other) -> bool:
		return not self.veq(other) and not self.lt(other)

	def __ge__(self, other) -> bool:
		return not self.lt(other)

	def __neg__(self):
		return Neg(self)

	def __add__(self, other):
		return Add(self, other)

	def __sub__(self, other):
		return Sub(self, other)

	def __mul__(self, other):
		return Mul(self, other)

	def __div__(self, other):
		return Div(self, other)

	def calc(self):
		return self

class Algebra(Element):
	ATTR_NAME = '__equation_algebra_values'

	def __init__(self, name: str):
		assert Algebra.check_name(name)
		self._name = name

	@staticmethod
	def check_name(name: str) -> bool:
		num = False
		for c in name:
			if '0' <= c and c <= '9':
				if not num:
					num = True
				continue
			if num:
				return False
			if (c < 'a' or 'z' < c) and (c < 'A' or 'Z' < c):
				return False
		return True

	@property
	def name(self) -> str:
		return self._name

	@property
	def value(self) -> float:
		curthr = threading.current_thread()
		values = getattr(curthr, Algebra.ATTR_NAME, None)
		if values is None:
			raise RuntimeError('Not in an algebra context')
		v = values.get(self.name, None)
		if v is None:
			raise RuntimeError('Undefined algebraic value')
		return v

	def __str__(self) -> str:
		return self.name

	def __repr__(self) -> str:
		return f'<Algebra name={str(self.name)}>'

	def eq(self, other) -> bool:
		return self.name == other.name

Algebra.A = Algebra('a')
Algebra.B = Algebra('b')
Algebra.C = Algebra('c')
Algebra.D = Algebra('d')
Algebra.W = Algebra('w')
Algebra.X = Algebra('x')
Algebra.Y = Algebra('y')
Algebra.Z = Algebra('z')

class Number(Element):
	def __new__(cls, n):
		return super().__new__(cls)

	def __init__(self, n):
		self.__v = float(n)

	@property
	def value(self) -> float:
		return self.__v

	def __str__(self) -> str:
		return str(self.__v)

	def __repr__(self) -> str:
		return f'<Number {str(self.__v)}>'

	def eq(self, other) -> bool:
		return self.__v == other.__v

	def lt(self, other) -> bool:
		return self.__v < other.__v

Number.ZERO = Number(0)
Number.ONE = Number(1)

class Expr(Element):
	pass

class Op1Expr(Expr):
	def __init__(self, a: Element):
		self.__a = a if isinstance(a, Element) else Element.from_obj(a)

	@property
	def op1(self):
		return self.__a

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__} {repr(self.__a)}>'

	def calc(self):
		a = self.__a.calc()
		obj = self.__class__(a)
		if isinstance(a, Number):
			return Number(obj.value)
		return obj

class Op2Expr(Expr):
	def __init__(self, a: Element, b: Element):
		self.__a = a if isinstance(a, Element) else Element.from_obj(a)
		self.__b = b if isinstance(b, Element) else Element.from_obj(b)

	@property
	def op1(self):
		return self.__a

	@property
	def op2(self):
		return self.__b

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__} {repr(self.__a)}, {repr(self.__b)}>'

	def eq(self, other) -> bool:
		return self.__a == other.__a and self.__b == other.__b

	def calc(self):
		a, b = self.__a.calc(), self.__b.calc()
		obj = self.__class__(a, b)
		if isinstance(a, Number) and isinstance(b, Number):
			return Number(obj.value)
		return obj

class Neg(Op1Expr):
	def __new__(cls, a: Element):
		return super().__new__(cls)

	@property
	def value(self) -> float:
		return -self.op1.value

	def __str__(self) -> str:
		return f'-{str(self.op1)}'

	def eq(self, other) -> bool:
		return self.op1 == other.op1

	def lt(self, other) -> bool:
		return self.op1 > other.op1

	def calc(self):
		self = super().calc()
		a = self.op1
		if isinstance(a, Number):
			return a.__class__(-a.value)
		if isinstance(a, Neg):
			return a.op1
		return self

class Add(Op2Expr):
	@property
	def value(self) -> float:
		return self.op1.value + self.op2.value

	def __str__(self) -> str:
		return f'({str(self.op1)} + {str(self.op2)})'

	def eq(self, other) -> bool:
		return (self.op1 == other.op1 and self.op2 == other.op2) or \
			(self.op1 == other.op2 and self.op2 == other.op1)

	def calc(self):
		self = super().calc()
		o1, o2 = self.op1, self.op2
		if o1 == Neg(o2).calc():
			return Number.ZERO
		return self

class Sub(Op2Expr):
	@property
	def value(self) -> float:
		return self.op1.value - self.op2.value

	def __str__(self) -> str:
		return f'({str(self.op1)} - {str(self.op2)})'

	def eq(self, other) -> bool:
		return (self.op1 == other.op1 and self.op2 == other.op2) or \
			(self.op1 == -other.op2 and self.op2 == -other.op1)

	def calc(self):
		self = super().calc()
		o1, o2 = self.op1, self.op2
		if o1 == o2:
			return Number.ZERO
		return self

class Mul(Op2Expr):
	@property
	def value(self) -> float:
		return self.op1.value * self.op2.value

	def __str__(self) -> str:
		return f'{str(self.op1)} * {str(self.op2)}'

	def calc(self):
		cls = self.__class__
		self = super().calc()
		if isinstance(self.op1, (Add, Sub)):
			return self.op1.__class__(cls(self.op1.op1, self.op2).calc(), cls(self.op1.op2, self.op2).calc())
		if isinstance(self.op2, (Add, Sub)):
			return self.op2.__class__(cls(self.op1, self.op2.op1).calc(), cls(self.op1, self.op2.op2).calc())
		return self

class Div(Op2Expr):
	@property
	def value(self) -> float:
		return self.op1.value / self.op2.value

	def __str__(self) -> str:
		return f'{str(self.op1)} / {str(self.op2)}'

	def calc(self):
		cls = self.__class__
		self = super().calc()
		if isinstance(self.op1, (Add, Sub)):
			return self.op1.__class__(cls(self.op1.op1, self.op2).calc(), cls(self.op1.op2, self.op2).calc())
		return self
