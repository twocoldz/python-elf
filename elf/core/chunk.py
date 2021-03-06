"""
  Copyright (C) 2008-2013  Tomasz Bursztyka

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

""" ChunkCounter and Chunk classes """

class ChunkCounter( object ):
    """ Basic Singleton counter class for chunks """

    _instance = None
    count = 0

    def __new__(cls):
        """ Singleton instanciation """

        if cls._instance is None:
            cls._instance = object.__new__(cls)
            cls._instance.count = -1

        cls._instance.count += 1

        return cls._instance


class Chunk( object ):
    """ Basic Chunk class: all parts of ELF format are assumed as chunks """
    issuer = None

    def __init__(self, prop=None, load=False, offset=None, size=0, issuer=None):
        """ Constructor """

        self.issuer = issuer

        self.prop = prop
        self.offset_start = offset
        self.offset_end = offset + size
        self.data = None
        self.modified = False
        # unique reference
        self.inside = None
        # Mutltiple includes, see accessors below
        self.includes = []

        self.protected = False
        self.suppressed = False
        self.inserted = False

        self.counter = ChunkCounter()

        if load:
            self.load()

    def __del__(self):
        """ Finalize before deletion """

        try:
            self.finalize()
        except Exception:
            pass

    def __getattr__(self, name):
        if name == 'size':
            return self.offset_end - self.offset_start

        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        """ Attribute setter rewrite """

        if name == 'data' and value is not None:
            self.modified = True
            self.offset_end = self.offset_start + len(value)

        elif name == 'size' and value is not None:
            self.modified = True
            self.offset_end = self.offset_start + value
            return

        elif name.find('offset') > -1 and value is not None:
            self.modified = True

        self.__dict__[name] = value

        if self.issuer != None:
            self.issuer.affect(self)

    def load(self, offset=None, filemap=None):
        """ Loads chunk content into data attribute from filemap """

        if offset == None:
            if self.offset_start == None:
                return
            else:
                offset = self.offset_start

        if self.size <= 0:
            return

        f_m = None
        if filemap != None:
            f_m = filemap
        elif self.prop.map_src != None:
            f_m = self.prop.map_src
        else:
            return

        f_m.seek(self.offset_start)
        self.data = f_m.read(self.size)

    def remove(self, force = False):
        """ Remove the chunk """

        if self.protected == True and force == False:
            return -1

        if self.issuer != None:
            self.issuer.affect(self)

        self.suppressed = True
        return 0

    def affect(self, from_chunk):
        """ Apply changes from relevant chunk """

        pass

    def add_include(self, include):
        """ add an include to the chunk, this chunk becomes the parent """

        if include not in self.includes:
            self.includes.append(include)
            include.inside = self

    def del_include(self, include):
        """ delete an include from the chunk """

        if include not in self.includes:
            return

        idx = self.includes.index(include)
        del self.includes[idx]

        include.inside = None

    def chunks(self):
        """ Returns the chunks it possesses """

        return [self]

    def finalize(self):
        """ Decreasing the ChunkCounter """

        self.counter.count -= 1

    def write(self, filemap):
        """ Write the chunk and its includes """

        if self.size <= 0 or self.data == None:
            return 0

        filemap.seek(self.offset_start)

        if len(self.includes) == 0:
            filemap.write(self.data)
            return self.size

        cur_data = 0
        cur_offset = self.offset_start

        for inc in self.includes:
            if cur_offset < inc.offset_start:
                new_cur_data = cur_data + inc.offset_start - cur_offset
                filemap.write(self.data[cur_data:new_cur_data])

                cur_data = new_cur_data
                cur_offset = inc.offset_start

            w_size = inc.write(filemap)

            cur_data += w_size
            cur_offset += w_size

        if cur_data < self.size:
            filemap.write(self.data[cur_data:])

        return self.size

#######
# EOF #
#######

