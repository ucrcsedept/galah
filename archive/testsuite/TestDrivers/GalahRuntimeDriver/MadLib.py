#!/usr/csshare/bin/python

# The global function getAvailableTests must be made available in all testing
# files and it should return a list/set of all the test classes in the file. Any
# test class that is not listed will not be accessible by the runtime tester.
def getAvailableTests():
	return {WordsExist, LineLengths}

# Preparers are given a process and are responsible for running the program and
# saving its output in a meaningful way for the test classes. Multiple preparers
# may be specified, preparers will be run as needed for the test classes.
class DefaultPreparer:
	def __init__(self):
		self.programOutput = ""
		self.words = ["asdikloo%0.2d" % i for i in range(0, 100)]
		
	def run(self, zexec):
		# Save the program's output (ignore stderr output for now)
		self.programOutput = zexec.communicate("\n".join(self.words))[0]

# This is the first test class
class WordsExist:
	"""
	Tests whether or not the words made it into the output. Only
	tests up to 10 words. A point is marked off for every
	missing word. Max points is 10.
	"""
			   
	# Test classes must define a preparer function that returns the preparer
	# that must be given to the test class.
	def preparer(self):
		return DefaultPreparer
		
	# This function is called once a preparer is ready. The readied preparer is
	# given to the test class for use.
	def run(self, zpreparer):
		# Start with full points
		score = 10
		
		# Subtract a point for every missing word. Note only 10 words are
		# tested
		for i in zpreparer.words[:10]:
			if i not in zpreparer.programOutput:
				score -= 1
				
		return (score, 10)

# Just another simple testing class
class LineLengths:
	"""
	Tests whether every line of the output is between 60 and 80 characters
	long. A point is taken off for every erroneous line. The total amount of
	points possible is equal to the number of lines of output.
	"""
	
	def preparer(self):
		return DefaultPreparer
		
	def run(self, zpreparer):
		# Split the output into lines
		lines = zpreparer.programOutput.splitlines()
		
		# Start with full points
		score = len(lines)
		
		for i in zpreparer.programOutput.splitlines():
			if len(i) in range(60, 81):
				score -= 1
				
		return (score, len(lines))
