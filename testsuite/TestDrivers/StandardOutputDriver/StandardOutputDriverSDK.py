#!/usr/csshare/bin/python

import sys, json, atexit

class __HarnessConfiguration:
    def __init__(self):
        self.tests = []
        self.info = None
        self.testables = []
        self.errors = []

        atexit.register(self.__cleanup, self)

    def __cleanup(self):
        json.dump(self.errors, sys.stderr)
        
    def read(self, zfrom = sys.stdin):
        # Will throw value error if invalid input is caught
        self.rawInput = json.read(zfrom)
        
        self.tests = self.rawInput["tests"]
        self.info = self.rawInput["info"]
        self.testables = self.rawInput = self.rawInput["testables"]
        
        return self

class HarnessConfiguration:
    __instance = None
    
    @staticmethod
    def instance():
        if __instance == None:
            __instance = __HarnessConfiguration()
        
        return __instance

class TestResult:
    def __init__(self, zname = "", zscore = 0, zscoreMax = 0):
        self.name = ""
        self.testable = ""
        self.score = 0
        self.scoreMax = 0
        self.inconclusive = False
        self.messages = []
        
    def toDict(self):
        return {"name": self.name,
                "testable": self.testable,
                "score": self.score,
                "scoreMax": self.scoreMax,
                "inconclusive": self.inconclusive,
                "messages": self.messages}
