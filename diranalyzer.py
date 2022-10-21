#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import logging
import re

class Diranalyzer:
    def __init__(self, dirlist, afile, outputfile = "results.csv", baseshare = ""):
        self.logger = logging.getLogger("DIRANALYZER")

        self.outputfile=outputfile
        self.baseshare = baseshare
        self.BaseLevels = []
        self.ShareLevels = {}

        self.noresults = []

        with open(afile, "r") as f:
            lines = [line.rstrip() for line in f]

        for line in lines:

            if line == "":
                continue

            sharelevel = line.replace("\\","/")
            if sharelevel[-1:] != "/":
                sharelevel +="/"
            self.BaseLevels.append(sharelevel)

        dirlistLines = open(dirlist,'r')

        for dirlistLine in dirlistLines:
            if dirlistLine[:1] == ".":
                dirlistLine = dirlistLine[1:]

            found_match = False
            for BaseLevel in self.BaseLevels:
                regex = re.compile(re.escape(BaseLevel))                
                match = re.match(regex, dirlistLine.rstrip())
                if match:
                    if "." in os.path.basename(match.string):
                        self.logger.debug("Found "+match.string)
                        sharelevel = match.string.replace(BaseLevel,"").split("/")[0]
                        if sharelevel not in self.ShareLevels:
                            self.ShareLevels[sharelevel] = ShareLevel(BaseLevel+sharelevel)

                        self.ShareLevels[sharelevel].add_filepath(match.string)
                        found_match = True

            if not found_match:
                if "." in os.path.basename(dirlistLine):
                    self.noresults.append(dirlistLine)

        for level in self.ShareLevels:
            self.logger.info("Found "+str(len(self.ShareLevels[level].filepaths))+" files in path "+self.ShareLevels[level].base)

        self.write_results()
        self.write_noresults()

    def write_results(self):
        # CSV format:
        # ShareLevel,countfiles

        f = open(self.outputfile,"w")
        for level in self.ShareLevels:
            f.write(self.baseshare+self.ShareLevels[level].base.replace("/","\\")+","+str(len(self.ShareLevels[level].filepaths))+"\n")

        f.close()
        self.logger.info("Results written to: "+self.outputfile)

    def write_noresults(self):
        f = open ("no-"+self.outputfile,"w")
        for noresult in self.noresults:
            f.write(self.baseshare+noresult.replace("/","\\"))

        f.close()
        self.logger.info("No results written to: no-"+self.outputfile)

class ShareLevel:
    def __init__(self, base):
        self.base = base
        self.filepaths = []

    def add_filepath(self, filepath):
        self.filepaths.append(filepath)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(add_help =  True, description = "Parse dirlisting file to provide insights of permissive (department) folders based on an input file of desired levels of access.")
    parser.add_argument('-dirlist', help='[required] File that contains the dirlist (newline seperated) ', required=True)
    parser.add_argument('-afile', help='[required] File used to analyse department shares, this should be a newline seperated list of paths of which level of access is acceptable. I.e.: /Global/US/departments/', required=True)
    parser.add_argument('-baseshare', action='store', help='Prepend this string to all results as the base of the fileshare. i.e. \\dc01\SYSVOL', default="")
    parser.add_argument('-outputfile', action='store', help='Output file to write CSV of results to.', default="results.csv")
    parser.add_argument('-debug', action='store_true', help='Turn DEBUG output ON')
    options = parser.parse_args()

    logger = logging.getLogger("MAIN")

    if (options.debug):
        logging.basicConfig(format='%(name)-11s | %(asctime)s - %(levelname)-5s - %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(name)-11s | %(asctime)s - %(levelname)-5s - %(message)s', level=logging.INFO)

    logger.info("Diranalyzer v0.1")

    logger.debug("Dirlist file: "+options.dirlist)
    logger.debug("Analysis file: "+options.afile)
    logger.debug("Output file: "+options.outputfile)

    if not os.path.exists(options.dirlist):
        logger.error("Dirlist file not found!")
        exit()
    if not os.path.exists(options.afile):
        logger.error("Analysis file not found!")
        exit()

    dc = Diranalyzer(options.dirlist, options.afile, options.outputfile, options.baseshare)
