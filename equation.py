
from .element import *

__all__ = [
	'Equation'
]

class Equation:
	def __init__(self, a: Element, b: Element):
		self._a = a
		self._b = b

	@property
	def left(self) -> Element:
		return self._a

	@property
	def right(self) -> Element:
		return self._b

	def is_valid(self) -> bool:
		return self.left.value == self.right.value

	def __str__(self) -> str:
		return f'{str(self.left)} = {str(self.right)}'

	def __repr__(self) -> str:
		return f'<Equation {str(self.left)}, {str(self.right)}>'

	def add(self, val: Element):
		self._a += val
		self._b += val

	def sub(self, val: Element):
		self._a -= val
		self._b -= val

	def mul(self, val: Element):
		self._a *= val
		self._b *= val

	def div(self, val: Element):
		self._a /= val
		self._b /= val

	def solve(self):
		self._a = self._a.calc()
		self._b = self._b.calc()

class EquationGroup:
	def __init__(self, equations: list[Equation]):
		self.equs = equations
