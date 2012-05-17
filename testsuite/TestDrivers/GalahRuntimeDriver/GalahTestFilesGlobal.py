class Score:
	"""Holds a single score."""
	
	def __init__(self, zname = "None Specified", znumerator = 0.0, zdenominator = 0.0, zweight = 0.0):
		self.name = zname
		self.numerator = znumerator
		self.denominator = zdenominator
		self.weight = zweight
		self.messages = []
		self.attention = False
		
	def __str__(self):
		import textwrap
		
		if self.attention:
			s = "%s: Attention Required" % self.name
		else:
			s = "%s: %g/%g (Weight: %g)" % (self.name, self.numerator, self.denominator, self.weight)
			if self.messages:
				s += "\n"
				for i in self.messages:
					s += textwrap.fill("%s\n" % i, initial_indent = "\t", subsequent_indent = "\t")
				
		return s
