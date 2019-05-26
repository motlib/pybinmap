'''Implementation of the BinMap class for mapping binary data to meaningful
fields.'''

from collections import OrderedDict

from .dataitems import DataItem, UIntDataItem, CharDataItem, BoolDataItem, \
    FloatDataItem

class BinMap():
    '''The BinMap organized a set of data items to interpret unstructured binary
    data.'''

    def __init__(self):
        '''Initialize a BinMap instance.'''

        # a list for maintaining sort order of the items
        self._map_list = []
        # a dict for name based access
        self._map_dict = {}
        # interpreted data
        self._data = None

        # type table for mapping names to DataItem classes and default arguments
        self._type_tbl = {
            'raw': {'cls': DataItem},
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
            'float': {'cls': FloatDataItem, 'length': 32},
            'double': {'cls': FloatDataItem, 'length': 64},
        }

        # helper counter to fill unmapped regions
        self._unmapped_counter = 0


    def add(self, **kwargs):
        '''Add a new data item definition to this binary map.

        :param dt: The data type which is looked up in the datatype table to
          determine the class and default parameters for the DataItem instance to
          created.
        :param **kwargs: Keyword arguments, which are passed to the underlying
          DataItem.

        '''

        # At least we need the data type.
        if 'dt' not in kwargs:
            raise ValueError("Data type must be specified with 'dt' parameter.")

        spec = self._type_tbl[kwargs['dt']]

        kwargs.update(spec)

        # we do not pass on the class
        del kwargs['cls']

        cls = spec['cls']
        item = cls(**kwargs)

        self._add_item(item)


    def add_from_spec(self, spec):
        '''Use a list of dict structure to specify data items to add.'''

        for item in spec:
            self.add(**item)


    def get_spec(self):
        '''Generate a dict / list based structure containing the specification of this
        BinMap. This can be used for saving to json or yaml and later restore it with
        the add_from_spec() method.'''

        return [item.spec for item in self._map_list]


    def _add_item(self, item):
        '''Add a DataItem instance.'''

        self._map_dict[item.name] = item
        self._map_list.append(item)

        # TODO: Check for overlapping

        # keep the list sorted by start address
        self._map_list.sort(key=lambda item: item.start)


    def set_data(self, data):
        '''Set the data to be interpreted.

        :param data: A bytes() object containing the data to be interpreted.'''

        for item in self._map_list:
            item.set_data(data)


    def get_value_dict(self):
        '''Return an ordered dictionary containing mapping the data item names to their
        values. The dict is ordered by start address of the data items.

        '''

        odict = OrderedDict()
        for item in self._map_list:
            odict[item.get_name()] = item.get_value()

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

        for (di1, di2) in zip(self._map_list[:-1], self._map_list[1:]):
            if di1.end + 1 < di2.start:
                self._add_unmapped(di1.end + 1, di2.start - 1)

        if (end_addr is not None) and (end_addr > self._map_list[-1].end):
            self._add_unmapped(self._map_list[-1].end + 1, end_addr)


    def __str__(self):
        '''Convert the whole binmap to string, i.e. print the information from all
        contained data items.'''

        return '\n'.join(str(bd) for bd in self._map_list)


    def __iter__(self):
        '''Iterate over the (key, value) tuples.'''

        for item in self._map_list:
            yield (item.name, item.value)


    def items(self):
        '''Return an iterator to iterate over the underlying DataItem instances
        in this BinMap.'''

        return self._map_list.__iter__()
