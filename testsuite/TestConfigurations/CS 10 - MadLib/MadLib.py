#!/usr/bin/python

import subprocess
from StandardOutputDriverSDK import HarnessConfiguration, TestResult

def testWordsExist(zoutput, zwords):
    """
    Tests whether or not the words made it into the output. Only
    tests up to 10 words. A point is marked off for every
    missing word. Max points is 10.
    """
    
    # Start with full points
    score = 10
    
    # Subtract a point for every missing word. Note only 10 words are
    # tested
    for i in zwords[:10]:
        if i not in zoutput:
            score -= 1
            
    return TestResult("WordsExist", score, 10)
        
def testLineLengths(zoutput):
    """
    Tests whether every line of the output is between 60 and 80 characters
    long. A point is taken off for every erroneous line. The total amount of
    points possible is equal to the number of lines of output.
    """
    
    # Split the output into lines ignoring blank ones
    lines = \
        [i for i in zpreparer.programOutput.splitlines() if len(i.strip()) > 0]
    
    
    # Start with full points (minimum of 9 lines: 3 paragraphs each 3 lines min)
    maxScore = max(len(lines), 9)
    score = maxScore
    
    for i in zpreparer.programOutput.splitlines():
        if len(i) in range(60, 81):
            score -= 1
    
    return TestResult("LineLengths", score, maxScore)
    
def testParagraphs(zoutput):
    """Tests whether three paragraphs exist, each seperated by blank line."""
    
    # Split the output into lines
    lines = zpreparer.programOutput.splitlines()
    
    # Collect the lines into paragraphs
    paragraphs = [[]]
    for i in lines:
        isLineBlank = len(i.strip()) == 0
        
        # If the line seperates a paragraph, create a new list in paragraphs
        # otherwise if the line isn't blank add it to the current paragraph
        if isLineBlank and len(paragraphs[-1]) != 0:
            paragraphs.append([])
        elif not isLineBlank:
            paragraphs[-1].append(i)
            
    # Create an ordered list containing the number of sentences in each
    # paragraph in descending order.
    def countSentences(zstring):
        return zstring.count(".")
    paragraphLengths = [countSentences(i.join(" ")) for i in paragraphs]
    paragraphLenghts.sort(reverse = True)

    # Calculate the total points. The total points is given by taking the three
    # largest paragraphs and adding up their total number of sentences.
    score = 0
    for i in paragraphLengths[:3]:
        score += min(3, i)
        
    return TestResult("Paragraphs", score, 9)

def main():
    config = HarnessConfiguration.instance().read()
    
    if len(config.testables) != 1:
        config.errors.append("Fatal Error: Exactly one testable may be passed.")
        return 1
        
    def id_generator(zsize, zchars):
        return "".join(random.choice(chars) for x in xrange(zsize))
    
    # Generate the words we will send to the testable
    words = [id_generator(8, string.ascii_lowercase) + "%0.2d" % i
             for i in range(0, 100)]
    
    # Execute the testable
    subprocess.Popen([config.testables[0]],
                     stdin = subprocess.PIPE,
                     stdout = subprocess.PIPE,
                     stderr = subprocess.STDOUT)
    
    subprocess.stdin.write(words.join(" "))
    subprocess.stdin.close()
    
    # Grab all the output
    output = subprocess.stdout.readlines().join("\n")
    
    # Kill the process if it's still running
    if subprocess.poll() == None:
        subprocess.kill()
    
    testResults = []
    if "WordsExist" in config.tests:
        testResults.append(testWordsExist(output, words))
    if "LineLengths" in config.tests:
        testResults.append(testLineLengths(output))
    if "Paragraphs" in config.tests:
        testResults.append(testLineLengths(output))
        
    json.dump(testResults, sys.stdout)
    sys.stderr.write("\n")
    
    return 0
    
if __name__ == "__main__":  
    exit(main())
    
