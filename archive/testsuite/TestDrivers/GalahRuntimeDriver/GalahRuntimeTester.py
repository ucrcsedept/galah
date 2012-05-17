#!/usr/csshare/bin/python

import picklexml
import argparse
import xml.dom.minidom as minidom
import threading
import os
import imp
import subprocess
import textwrap
from GalahGlobal import *

def main(zargs):
	# Parse the test specification
	specDom = minidom.parse(zargs.SpecFile)
	
	# Create a node list of all the runtime elements which list runtime testing
	# files
	runtimeEles = \
		specDom.documentElement.getElementsByTagName("runtime")
	
	# Figure out what directory the test specification is so we can find test
	# files it specifies with relative paths easier.
	testSpecDirectory = os.path.dirname(os.path.abspath(zargs.SpecFile))
		
	# Create a list of test files from the test spec. by walking the DOM
	testFiles = []
	for curRuntimeEle in runtimeEles:
		for curFileEle in curRuntimeEle.getElementsByTagName("file"):
			# Find the absolute path of the test file
			filePath = \
				os.path.join(testSpecDirectory, curFileEle.attributes["path"].value)
			
			# Create a new test file object
			testFiles.append(TestFile(filePath))
			
			# Add all of the tests to the test file object
			for curTestEle in curFileEle.getElementsByTagName("test"):
				# Convert the attribute list to a regular dictionary and store
				# the name seperately
				atts = dict(curTestEle.attributes.items())
				testName = atts["name"]
				del atts["name"]
				
				testFiles[-1].addTest(testName, atts)
	
	if not zargs.Programs:
		print "Displaying tests specified by %s." % zargs.SpecFile
		print
		
		for f in testFiles:
			for t in f.tests.values():
				# Get the description from the test class if it provides one
				desc = t.testClass.__doc__ or "[No Description Provided]"
				
				# Make sure the description is wrapped nicely
				desc = textwrap.fill(textwrap.dedent(desc), 70)
				print "Test %s: " % t.name
				print desc
				print
	else:		
		for p in zargs.Programs:			
			keeper = ScoreKeeper()
			
			try:
				for f in testFiles:
					f.runTests(p, keeper)
				
				print "<results program='%s' grade='%f'>" % (p, keeper.getWeightedScore())
				
				if p in PreparerCache.savedOutputs:
					for i in PreparerCache.savedOutputs[p]:
						print "<preparer>"
						print i
						print "</preparer>"
				
				DefaultScoreRenderer().render(keeper)
				
				print "</results>"
				print
			except OSError:
				print "<attention>Error: Could not execute program %s!</attention>" % p
				print
	
def parseArgs():
	"""Sets up the argument parser and returns the result of parse_args()."""
	
	argParser = argparse.ArgumentParser(
		description = "Runs the Galah Runtime Tester on a program given a test " \
					  "specification")
	argParser.add_argument("SpecFile",
						   help="The XML file containing the test specification.")
	argParser.add_argument("Programs", nargs="*",
						   help="The program(s) to run the test(s) on. If no " \
								"programs are specified, information on tests " \
								"listed in the SpecFile is given.")
	return argParser.parse_args()

class PreparerCache:
	"""
	Caches preparers for all test files.
	"""
	
	class __TestFilePreparerCache:
		"""
		A preparer cache for a single test file. Simple struct.
		"""
		
		def __init__(self):
			# Dictionary: key = class, value = instance of key class
			self.cache = {}
			
		def getPreparer(self, zpreparer, ztestProgramPath, zfresh = False):
			"""
			Retrieves an instance of zpreparer from the cache and returns it, if
			an instance does not exist in the cache (or zfresh is True) then a
			new instance of zpreparer is created and prepared.
			"""
		
			readyPreparer = None
			if zpreparer not in self.cache:
				# Used with timeout()
				marker = []
				
				try:
					r = timeout(newPreparer.inititialize, [], {}, 5, marker)
					if r is marker:
						return None
				except AttributeError:
					# Execute the test file
					testProcess = subprocess.Popen(ztestProgramPath,
												   stdin=subprocess.PIPE,
												   stdout=subprocess.PIPE,
												   stderr=subprocess.PIPE)
				
				# Create a new instance of the preparer
				newPreparer = zpreparer()
				
				# Run the preparer on the test file. In case the preparer hangs,
				# the function is ran in a seperate thread and it is killed if
				# it takes too long to return.
				marker = []
				r = timeout(newPreparer.run, [testProcess], {}, 5, marker)
				if r is marker:
					return None
					
				# Cache the preparer
				self.cache[zpreparer] = newPreparer
			
				readyPreparer = newPreparer
			else:
				readyPreparer = self.cache[zpreparer]
				
			return readyPreparer
	
	# Dictionary: key = test program path, value = list of outputs
	savedOutputs = {}
	
	def __init__(self):
		# Dictionary: key = test file, value = __TestFilePreparerCache
		self.caches = {}
	
	def clear(self):
		self.caches.clear()
		
	def saveOutputs(self, ztestProgramPath):
		if ztestProgramPath not in self.savedOutputs:
			PreparerCache.savedOutputs[ztestProgramPath] = []
			
		for i in self.caches.values():
			for j in i.cache.values():
				PreparerCache.savedOutputs[ztestProgramPath].append(j.savedOutput())
	
	def getPreparer(self, ztestFile, zpreparer, ztestProgramPath, zfresh = False):
		"""
		Retrieves an instance of zpreparer from ztestFile's cache and returns
		it, if an instance does not exist in the cache (or zfresh is True) then
		a new instance of zpreparer is created and prepared.
		"""
		
		if ztestFile not in self.caches:
			self.caches[ztestFile] = PreparerCache.__TestFilePreparerCache()
			
		return self.caches[ztestFile].getPreparer(zpreparer, ztestProgramPath, zfresh)

class TestFile:
	"""
	Wrapper around a single test file.
	"""
			
	def __init__(self, zpath):
		"""
		zpath: The test file's *absolute* path.
		"""
		
		self.path = zpath
		self.name = os.path.basename(zpath)
		self.preparerCache = PreparerCache()
		self.tests = {}
		
		# Import the test file
		foundModule = imp.find_module(self.name, [os.path.dirname(zpath)])
		if foundModule == None:
			raise ImportError("Cannot find test module %s. Bad test " \
							  "specification." % curModulePath)
		self.module = imp.load_module(self.name, *foundModule)
		
		# Store the supported test classes in a set
		self.availableTests = set(self.module.getAvailableTests())
	
	def addTest(self, zname, zattributes):
		"""Convenience function for adding tests to the self.tests dict."""
		
		self.tests[zname] = Test(self, zname, zattributes, self.preparerCache)
		
	def runTests(self, ztestProgramPath, zscores):
		for i in self.tests.values():
			i.run(ztestProgramPath, zscores)

		self.preparerCache.saveOutputs(ztestProgramPath)

		self.resetPreparers()
			
	def resetPreparers(self):		
		self.preparerCache.clear()
		
class Test:
	"""
	Wrapper around a single Test Class.
	"""

	def __init__(self, zparent, zname, zattributes, zcache):
		self.parent = zparent
		self.attributes = dict(zattributes)
		self.name = zname
		self.preparerCache = zcache
		
		# Find the test class
		self.testClass = None
		for i in self.parent.module.getAvailableTests():
			if i.__name__ == self.name:
				self.testClass = i
		
		# Error if the test class can't be found
		if self.testClass == None:
			raise ImportError("Cannot find test %s in test module %s. " \
							  "Bad test specification" %
							  (self.name, self.parent.name))
							   
	def run(self, ztestProgramPath, zscores):
		testInstance = self.testClass()
		
		desiredPreparer = testInstance.preparer()
		
		readyPreparer = \
			self.preparerCache.getPreparer(self.parent, desiredPreparer, ztestProgramPath)
		
		# This will happen if the preparer timed out
		if readyPreparer == None:
			failedScore = Score(self.name)
			failedScore.attention = True
			failedScore.messages.append("Preparer's run function timed out.")
			
			zscores.addScore(self.parent.name, failedScore)
			
			return
			
		resultScore = testInstance.run(readyPreparer)
		
		score = None
		if resultScore == None:
			score = Score(self.name)
		elif isinstance(resultScore, tuple):
			score = Score(self.name, *resultScore)
		elif isinstance(resultScore, Score):
			if resultScore.name == "None Specified":
				resultScore.name = self.name
			score = resultScore
			
		score.weight = self.attributes["weight"] if "weight" in self.attributes else 1.0
		
		zscores.addScore(self.parent.name, score)
		
class ScoreKeeper:
	"""
	Records scores for a run of tests.
	"""
			
	def __init__(self):
		# Holds all the sets of scores.
		self.scores = {}
	
	def addScore(self, zset, zscore):
		"""Convenience function for adding a score to a given set."""
		
		if zset not in self.scores:
			self.scores[zset] = [zscore]
		else:
			self.scores[zset].append(zscore)
	
	def getWeightedScore(self, zset = None):
		"""
		Calculates the total score for the given list of scores and returns
		it as a percentage.
		"""
		
		# The sum of all the score's weights
		totalWeight = 0.0
		
		# The total score. Maximum score is equal to totalWeight.
		totalScore = 0.0
		
		scores = []
		if zset == None:
			for i in self.scores.values():
				scores += i
		else:
			scores = self.scores[zset]
		
		for i in scores:
			# Ignore any tests which aren't worth any points (and avoid divide
			# by zero errors)
			if i.denominator == 0.0:
				continue
			
			totalWeight += i.weight
			totalScore += i.weight * (float(i.numerator) / i.denominator)
	
		return totalScore / totalWeight
		
class DefaultScoreRenderer:
	def render(self, zkeeper):
		for k, v in zkeeper.scores.items():
			for t in v:
				if t.attention:
					print "<testresult test='%s' attention='true'>" % t.name
				else:
					print "<testresult test='%s' score='%g' maxscore='%g' weight='%g'>" %
						(t.name, t.numerator, t.denominator, t.weight)
				
				if t.messages:
					for i in t.messages:
						print "\t<message>%s</message>" % i
				print "</testresult>"

# Run the script if its not being imported
if __name__ == "__main__":
    main(parseArgs())
    
    os.sys.exit()
