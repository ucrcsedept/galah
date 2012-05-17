#!/usr/csshare/bin/python

import re
from GalahGlobal import *

# Licensed under PSF, replace with own code to avoid conflictions.
## {{{ http://code.activestate.com/recipes/473878/ (r1)
def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
	import threading
	class InterruptableThread(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.result = None
			self.daemon = True

		def run(self):
			try:
				self.result = func(*args, **kwargs)
			except:
				self.result = default

	it = InterruptableThread()
	it.start()
	it.join(timeout_duration)
	if it.isAlive():
		return default
	else:
		return it.result
## end of http://code.activestate.com/recipes/473878/ }}}

def nonBlockingRead(zfile):
	result = None
	output = ""
	
	while True:
		result = timeout(zfile.read, (1,), {}, 0.1)
		
		if result == None:
			break
		else:
			output += result
	
	return output

# The global function getAvailableTests must be made available in all testing
# files and it should return a list/set of all the test classes in the file. Any
# test class that is not listed will not be accessible by the runtime tester.
def getAvailableTests():
	return {CorrectlyCalculated, NameIsSplit, NumbersFormatted, NeatFormatting, }

# Preparers are given a process and are responsible for running the program and
# saving its output in a meaningful way for the test classes. Multiple preparers
# may be specified, preparers will be run as needed for the test classes.
class DefaultPreparer:
	def __init__(self):
		self.first = "AfroMan"
		self.last = "OSullivan"
		self.nameString = "%s,%s" % (self.last, self.first)
		self.janIncome = 10023.3923
		self.febIncome = 7485495.2132
		self.marIncome = 9.23645
		self.programOutput = ""
	
	def savedOutput(self):
		return self.programOutput
	
	def run(self, zexec):
		userInput = "\n".join([self.nameString, str(self.janIncome), 
							   str(self.febIncome), str(self.marIncome)])
		
		# Save the program's output (ignore stderr output for now)
		self.programOutput = zexec.communicate(userInput)[0]

class CorrectlyCalculated:
	"""
	Tests whether the user correctly calculated the values.
	
		-6: For each improperly computed value (max -18)
		-2: If no value was computed properly
	"""
	
	def preparer(self):
		return DefaultPreparer
		
	def run(self, zpreparer):
		matches = re.findall(r"\d+\.?\d*(?:e[\+-])?\d*", zpreparer.programOutput, re.IGNORECASE | re.MULTILINE)
		
		score = Score()
		score.numerator = score.denominator = 20
		
		if len(matches) != 6:
			score.attention = True
			score.numerator = 0
			score.messages.append("%d numbers found in output, expected 6." % len(matches))
			
			return score
			
		grossIncome = sum([float(i) for i in matches[:3]])
		incomeTax = grossIncome * 0.15
		netIncome = grossIncome - incomeTax
		
		numMissed = 0
		if not (grossIncome - 5.0 <= float(matches[3]) <= grossIncome + 5.0):
			numMissed += 1
			score.numerator -= 6
			score.messages.append("-6: Gross income not calculated properly.")
			
		if not (incomeTax - 5.0 <= float(matches[4]) <= incomeTax + 5.0):
			numMissed += 1
			score.numerator -= 6
			score.messages.append("-6: Income tax not calculated properly.")
			
		if not (netIncome - 5.0 <= float(matches[5]) <= netIncome + 5.0):
			numMissed += 1
			score.numerator -= 6
			score.messages.append("-6: Net income not calculated properly.")
			
		# If they didn't get any of them don't give them the free 2 points
		if numMissed == 3:
			score.numerator = 0
			
		return score
		

class NameIsSplit:
	"""
	Tests whether the user correctly extracted the first and last name from the
	input. Out of 20 points.
	
		-5: For each incorrect name (first and last) up to 10.
		-10: For static substr() usage.
	"""
			   
	# Test classes must define a preparer function that returns the preparer
	# that must be given to the test class.
	def preparer(self):
		return DefaultPreparer
		
	def findSplitText(self, zsource, zsearchString, ztolerant = False):
		"""
		Finds the zsearchString within zsource even if zsearchString has been
		split at a single point. For example, given the search string "bigbear",
		all the following sources contain a match "dfbig bear", "bigdasfadbear",
		"bi sdfsdfsd gbear". Note that "bi gb ear" would not match however, as
		it was split at multiple points.
		
		If ztolerant is True, then, given the search string "bigbear", the
		following sources would also contain matches: "big gbear", "bigbigbear",
		"bigasdfbigbear". So the split can be a bit clumsy.
		
		Returns a tuple containing each part of how it was split. If the search
		string was not split at all, the first item of the tuple contains
		zsearchString. None is returned if no match was found.
		"""
		
		return NotImplemented
		
	# This function is called once a preparer is ready. The readied preparer is
	# given to the test class for use.
	def run(self, zpreparer):
		score = Score()
		
		score.messages = []
		score.denominator = score.numerator = 20
		
		# Here we will attempt to find the split name in their output. Here we
		# will progessively get more and more tolerant.
		
		# Least tolerant, they must have followed the format almost exactly
		match = re.search(r"\s*first\s*name\s*:\s*(?P<first>[\w,]*)\s*last\s*name\s*:\s*(?P<last>[\w,]*)\s*$", zpreparer.programOutput, re.IGNORECASE | re.MULTILINE)
		
		if match == None:
			# Very tolerant, will find the first and last name as long as they
			# are preceeded by colons or equal signs on the same line.
			match = re.search(r"^\s*(first\s*)?(name\s*)?[:=]\s*(?P<first>\w*)\s+(last\s*)?(name\s*)?[:=]\s*(?P<last>\w*)\s*$", zpreparer.programOutput, re.IGNORECASE | re.MULTILINE)
		
		# If the program couldn't find the names then set the attention flag
		if match == None:
			# Could not figure it out
			score.attention = True
			score.numerator = 0
			
			return score
		
		first, last = match.group("first", "last")
		
		# If the names are overly short then set the attention flag. This is
		# necessary because the slices we take later will error if the names
		# are too short.
		if len(first) <= 2 or len(last) <= 2:
			score.attention = True
			score.numerator = 0
			
			return score
		
		if first != zpreparer.first:
			score.numerator -= 5
			score.messages.append("-5: First name not extracted properly.")
		
		if last != zpreparer.last:
			score.numerator -= 5
			score.messages.append("-5: Last name not extracted properly.")

		# If a comma is embedded in the middle of either first or last then
		# the user definitely statically split the string.
		if ',' in first[1:-1] or ',' in last[1:-1]:
			score.numerator -= 10
			score.messages.append("-10: Static substr() split used.")
				
		return score

class NumbersFormatted:
	"""
	Tests whether the user correctly put the correct number of fixed point
	digits after any number.
	
		-20.0 / 6.0 : for every number incorrectly formatted.
	"""
	
	wrong_pts = 20.0 / 6.0
	
	# Test classes must define a preparer function that returns the preparer
	# that must be given to the test class.
	def preparer(self):
		return DefaultPreparer
	
	# This function is called once a preparer is ready. The readied preparer is
	# given to the test class for use.
	def run(self, zpreparer):
		score = Score()

		score.messages = []
		score.denominator = 20
		total_probs = 6

		match = re.findall(r"\d+\.?\d*(?:e[\+-])?\d*", zpreparer.programOutput, re.IGNORECASE | re.MULTILINE)
		
		score.numerator = min(20, len(match) * self.wrong_pts)
		
		if match == None or len(match) == 0:
			score.attention = True
			score.numerator = 0
		else:
			for numb in match:
				if numb.count('.') != 1 or len(numb.split('.')[1]) != 2:
					score.messages.append("-3.3*: Value '%s' incorrectly formatted." % numb)
					score.numerator -= self.wrong_pts
					
		score.numerator = max(0, score.numerator)
		
		return score


class NeatFormatting:
	"""
	Tests whether the user correctly formatted the output neatly.
	"""
	
	wrong_pts = 5
	
	# Test classes must define a preparer function that returns the preparer
	# that must be given to the test class.
	def preparer(self):
		return DefaultPreparer
	
	def mode(self, zlist, zminOccurences = 1):
		"""Gets the mode of a list."""
		
		if len(zlist) == 0:
			return None
		
		d = {}
		for i in zlist:
			if i in d:
				d[i] += 1
			else:
				d[i] = 1
		
		biggestKey = None
		biggestValue = None
		for k, v in d.items():
			if biggestValue == None or v > biggestValue:
				biggestKey = k
				biggestValue = v
		
		if biggestValue < zminOccurences:
			return None
		else:
			return biggestKey
		
	def removeOccurences(self, zlist, zitem):
		return [i for i in zlist if i != zitem]
	
	# This function is called once a preparer is ready. The readied preparer is
	# given to the test class for use.
	def run(self, zpreparer):
		lines = zpreparer.programOutput.splitlines()

		firstColumnWidths = []
		secondColumnWidths = []

		reg = re.compile(r" {3,}")

		for i in lines:
			matches = list(reg.finditer(i.strip()))
			
			# Ignore this line if there are no columns
			if matches == None:
				continue
				
			firstColumnWidths.append(matches[0].end() if len(matches) >= 1 else -1)
			secondColumnWidths.append(matches[1].end() - firstColumnWidths[-1] if len(matches) >= 2 else -1)

		firstColumnWidth = self.mode(self.removeOccurences(firstColumnWidths, -1), 2)
		secondColumnWidth = self.mode(self.removeOccurences(secondColumnWidths, -1), 2)
		
		score = Score()
		score.denominator = 20
		score.numerator = 20
		
		if firstColumnWidth != None:
			for i, j in zip(firstColumnWidths, secondColumnWidths):
				if i != -1 and i != firstColumnWidth:
					score.numerator -= 4 if j != -1 else 2
				elif j != -1 and j != secondColumnWidth:
					score.numerator -= 2
					
		score.numerator = max(score.numerator, 0)
		
		return score
