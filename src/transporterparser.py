"""
This module defines the class TransporterParser, a parser for transporter files.


This file is part of metano.
Copyright (C) 2010-2019 Alexander Riemer, Julia Helmecke
Braunschweig University of Technology,
Dept. of Bioinformatics and Biochemistry

metano is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

metano is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with metano.  If not, see <http://www.gnu.org/licenses/>.
"""

from builtins import object
import re

class TransporterParser(object):
    """Parser for transporter files.
    It reads lines of the format

    <name> [<factor>] [co(<name>)]

    into a list. Lines beginning with a # sign are ignored
    """

    # line pattern : <name> [<factor>] [co(<name>)]
    line_pattern = re.compile(r"(\S*)(?:\s*([\d\.]*))?(?:\s*co\((\S*)\))?")

    # name pattern: *_<type>_* (e.g. "trans_c_glu" => type "c")
    name_pattern = re.compile(r"[^_]*_([^_]*)_")


    def __init__(self):
        """ initialize the TransporterParser
        """
        self.clear()


    def clear(self):
        """ clear all internal variables, warnings and info messages
        """
        self.transporters = []


    def parse(self, filename):
        """ parse transporter file

        Keyword arguments:

        filename -- name of the file to be parsed

        Returns: list of (transporter_name, flux_factor, cotransporter_name)

        cotransporter_name is None if no cotransporter is to be checked
        flux_factor is None if the transporter is not of the "main" type (e.g.
        if it is not a C source)
        """
        try:
            line_no = 0
            with open(filename) as f:
                for line in f:
                    line_no += 1
                    line = line.strip()
                    if line == "" or line[0] == "#":
                        continue  # skip blank and comment lines
                    m = self.line_pattern.match(line)
                    transname = m.group(1)
                    transfac = m.group(2)
                    if transfac == "":
                        transfac = None
                    else:
                        transfac = float(transfac)
                    cotrans = m.group(3)
                    self.transporters.append((transname, transfac, cotrans))

        except ValueError:
            raise ValueError("Illegal float value %s in line %u of transporter "
                             "file." % (transfac, line_no))
        except AttributeError:
            raise SyntaxError("Syntax error in line %u of transporter file." %
                              line_no)

        return self.transporters


    def split_by_type(self, l=None):
        """ split transporters by type (e.g. element source - C, N, etc.)

        Keyword arguments:

        l -- list of (transporter_name, flux_factor, cotransporter_name),
                self.transporters (generated by parse()) is used if l is None

        Returns: list of lists of (type, transporter_name, flux_factor,
                 cotransporter_name), where type is the same for every
                 individual list
        """
        if l is None:
            l = self.transporters

        dict_of_types = {}  # dictionary { type : index in list_of_lists }
        list_of_lists = []
        try:
            for entry in l:
                m = self.name_pattern.match(entry[0])
                typ = m.group(1)
                if typ not in dict_of_types:
                    dict_of_types[typ] = len(list_of_lists)
                    list_of_lists.append([(typ,)+entry])
                else:
                    list_of_lists[dict_of_types[typ]].append((typ,)+entry)

        except AttributeError:
            raise SyntaxError("Malformed transporter name: %s (cannot identify "
                              "typ)" % entry[0])

        return list_of_lists
