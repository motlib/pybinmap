from collections import OrderedDict

from .dataitems import *

class BinMap():
    '''The BinMap organized a set of data items to interpret unstructured binary
    data.'''
    
    def __init__(self):
        # a list for maintaining sort order of the items
        self._map_list = []
        # a dict for name based access
        self._map_dict = {}
        
        self._data = None

        self._type_tbl = {
            'raw': {'cls': RawDataItem},
            'uint': {'cls': UIntDataItem},
            'uint8': {'cls': UIntDataItem, 'length': 8},
            'uint16': {'cls': UIntDataItem, 'length': 16},
            'uint32': {'cls': UIntDataItem, 'length': 32},
            'uint64': {'cls': UIntDataItem, 'length': 64},
            'ascii': {'cls': CharDataItem, 'encoding': 'ascii'},
            'utf8': {'cls': CharDataItem, 'encoding': 'utf-8'},
            'bool': {'cls': BoolDataItem},
            'bool1': {'cls': BoolDataItem, 'length': 1},
            'bool8': {'cls': BoolDataItem, 'length': 8},
        }

        self._unmapped_counter = 0

        
    def add(self, **kwargs):
        '''Add a new data item definition to this binary map.'''

        if 'dt' not in kwargs:
            raise ValueError("Must specify the data type with 'dt' parameter.")
        
        spec = self._type_tbl[kwargs['dt']]

        kwargs.update(spec)
        
        # we do not pass on the class
        del kwargs['cls']
        
        cls = spec['cls']
        bd = cls(**kwargs)

        self._add_bd(bd)

        
    def add_from_spec(self, spec):
        '''Use a list of dict structure to specify data items to add.'''
        
        for item in spec:
            self.add(**spec)

            
    def get_spec(self):
        return [item.spec for item in self._map_list]

    
    def _add_bd(self, bd):
        '''Add a DataItem instance.'''
        
        self._map_dict[bd.name] = bd
        self._map_list.append(bd)
        
        # keep the list sorted by start address
        self._map_list.sort(key=lambda bd: bd.start)

        
    def set_data(self, data):
        '''Set the data to be interpreted.

        :param data: A bytes() object containing the data to be interpreted.'''
        
        for bd in self._map_list:
            bd.set_data(data)

            
    def get_value_dict(self):
        '''Return an ordered dictionary containing mapping the data item names to their
        values. The dict is ordered by start address of the data items.

        '''
        
        odict = OrderedDict()
        for bd in self._map_list:
            odict[bd.get_name()] = bd.get_value()

        return odict

    
    def get_value(self, name):
        '''Return the value of a data item by its name.'''

        return self._map_dict[name].value


    def __getitem__(self, key):
        '''Index based access to values.'''
        
        return self._map_dict[key].value
    
    
    def get_item(self, name):
        '''Returns the underlying DataItem instance for the given name.'''
        return self._map_dict[name]
    

    def _add_unmapped(self, start, end):
        '''Add a 'raw' data item for the given address range.'''
        
        self.add(
            dt='raw',
            name='unmapped_{:03}'.format(self._unmapped_counter),
            start=start,
            length=(end - start + 1))

        self._unmapped_counter += 1
                

    def fill_unmapped(self, end_addr=None):
        '''Fill all unmapped areas 'raw' type mappings. 

        If end_addr is not specified, address space is filled up to the last
        mapped data item. Adress space beyond the last data item is not filled
        in any way.

        :param end_addr: Fill address space between mapped items and optionally
          up to this address.

        '''

        if self._map_list[0].start > 0:
            self._add_unmapped(0, self._map_list[0].start - 1)

        for (di1,di2) in zip(self._map_list[:-1], self._map_list[1:]):
            if di1.end + 1 < di2.start:
                self._add_unmapped(di1.end + 1, di2.start - 1)

        if (end_address is not None) and (end_address > self._map_list[:-1].end):
            self._add_unmapped(self._map_list[:-1].end + 1, end_address)

                
    def __str__(self):
        '''Convert the whole binmap to string, i.e. print the information from all
        contained data items.'''
        
        return '\n'.join(str(bd) for bd in self._map_list)
