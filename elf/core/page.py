"""
  Copyright (C) 2011-2013  Tomasz Bursztyka

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

""" Page class """

from elf.core.chunk import Chunk

class Page( Chunk ):
    """ A page is an headed chunk """

    def __init__(self, header, offset, size):
        """ Constructor """

        self.header = header

        Chunk.__init__(self, self.header.prop, True, offset, size, header)

    def chunks(self):
        """ Returns the chunks it possesses """

        return [self.header, self]

    def remove(self, force = False, forward = True):
        """ Remove the page and its header according to forward """

        if forward == True:
            ret = self.header.remove(force)

        return Chunk.remove(self, force)

#######
# EOF #
#######

