# -*- coding: utf-8 -*-

# Copyright (c) 2016 Felipe Gallego. All rights reserved.
#
# This file is part of kuicl: https://github.com/felgari/kuicl
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Process the program arguments received by the main function.

Define the arguments available, check for its correctness and coherence, 
and provides these arguments to other modules. 
"""

import argparse

from ctes import DEFAULT_INDEX

class ProgramArgumentsException(Exception):
    
    def __init__(self, msg):
        
        self._msg = msg
        
    def __str__(self):
        return self._msg

class ProgramArguments(object):
    """Encapsulates the definition and processing of program arguments.
    
    """                   
    
    def __init__(self):
        """Initializes parser. 
        
        Initialization of variables and the object ProgramArguments 
        with the definition of arguments to use.

        """               
            
        # Initialize arguments of the parser.
        self.__parser = argparse.ArgumentParser()  
        
        self.__parser.add_argument("-i", dest="i", metavar="index",
                                   default=DEFAULT_INDEX,
                                   help="Index to use.", type=int, 
                                   choices=xrange(1, 100))              
        
        self.__parser.add_argument("-r", dest="r", action="store_true", 
                                   help="Retrieve res.")   
        
        self.__parser.add_argument("-f", dest="f", action="store_true", 
                                   help="Force new calculations.")                   
        
        self.__args = self.__parser.parse_args()
        
    @property    
    def index_provided(self): 
        return self.__args.i != DEFAULT_INDEX      
        
    @property
    def index(self):
        return str(self.__args.i)          
    
    @property
    def retrieve_res(self):
        return self.__args.r    
    
    @property
    def force_calc(self):
        return self.__args.f              
 
    def print_usage(self):
        """Print arguments options.
        
        """
                
        self.__parser.print_usage()     
        
    def print_help(self):
        """Print help for arguments options.
        
        """
                
        self.__parser.print_help()  