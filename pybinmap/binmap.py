from collections import OrderedDict


class DataItem():
    '''Base class for binary data extraction. Needs to be subclassed to interpret
    data.'''
    
    def __init__(self, name, start, length, **kwargs):
        self._name = name
        self._start = start
        self._length = length
        
        self._raw_value = None
        self._value = None
        
        self._data = None

        
    def set_data(self, data):
        '''Sets the data to interpret. Calling this function already interprets the
        data.

        :param data: bytes object containing the data to be interpreted.

        '''

        endbyte = self.end // 8
        if len(data) < endbyte + 1:
            raise ValueError("Data too short in data item '{0}'.".format(self.name))
        
        self._data = data
        self._raw_value = self.extract_raw_value()
        self._value = self.calc_value()

        
    def get_bit(self, abs_bit):
        '''Returns a single bit from the input data.

        :param abs_bit: Bit address of the bit to return.
        :returns: 0 or 1.
        '''
        
        (byte, bit) = divmod(abs_bit, 8)

        # extract one bit (0 or 1) from input data
        b = (self._data[byte] & (1 << bit)) >> bit

        return b

    
    def extract_raw_value(self):
        '''Extract the data area specified by start and length values into a bytes()
        structure.'''
        
        bytelist = []
        bc = 0
        d = 0
        
        # end + 1, because for range, the top value is not reached
        for abs_bit in range(self.start, self.end + 1):
            b = self.get_bit(abs_bit)
            
            # shift it to the correct output position
            d += b << (bc % 8)

            bc += 1
            if bc == 8:
                bytelist.append(d)
                d = 0
                bc = 0

        if bc != 0:
            bytelist.append(d)

        return bytes(bytelist)


    @property
    def name(self):
        '''Name of this data item.'''
        return self._name

    @property
    def start(self):
        '''Start address (bit address) of this data item.'''
        return self._start

    @property
    def end(self):
        '''End address (bit address) of this data item. This returns the address of the
        last bit belonging to this item.

        '''
        
        return self.start + self.length - 1
    
    @property
    def length(self):
        '''Length, number of bits belonging to this data item.'''
        
        return self._length

    @property
    def raw_value(self):
        '''The raw value of this data item. This is a bytes() object containing the data
        belonging to this data item.'''
        
        if self._data == None:
            raise ValueError('No data set.')
                
        return self._raw_value

    @property
    def value(self):
        '''The interpreted value of this data item.'''
        
        if self._data == None:
            raise ValueError('No data set.')
        
        return self._value


    def _fmt_addr(self, abs_bit):
        '''Format a bit address as byte / bit address string.'''
        
        byte, bit = divmod(abs_bit, 8)

        return '{byte:04x}:{bit}'.format(
            byte=byte,
            bit=bit)

    
    def __str__(self):
        '''Convert the data item to string.'''
        
        rs = ' '.join('0x{0:02x}'.format(v) for v in self.raw_value)
        
        return '{addr}+{length} {name} = {value} [raw: {r}]'.format(
            addr=self._fmt_addr(self.start),
            name=self._name,
            s=self._start,
            length=self._length,
            value=self.value,
            r=rs)

    
class RawDataItem(DataItem):
    
    def calc_value(self):
        return self._raw_value
    
    
class CharDataItem(DataItem):
    def __init__(self, encoding='ascii', **kwargs):
        super().__init__(**kwargs)

        self._encoding = encoding
        
    def calc_value(self):
        return self._raw_value.decode('ascii')


class UIntDataItem(DataItem):
    def __init__(self, endian='little', **kwargs):
        super().__init__(**kwargs)

        if endian not in ('little', 'big'):
            msg = "Must use either 'big' or 'little' endian. Got '{0}'."
            raise ValueError(msg.format(endian))
        
        self._endian = endian

                             
    def calc_value(self):
        if self._endian == 'big':
            d = reversed(self._raw_value)
        else:
            d = self._raw_value
        
        r = 0
        for p, b in enumerate(d):
            r += (1 << (8 * p)) * b

        return r

    
class BoolDataItem(UIntDataItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

                             
    def calc_value(self):
        v = super().calc_value()

        # Convert the integer value to bool (0: False, everything else: True)
        return bool(v)

    
class BinMap():
    '''The BinMap organized a set of data items to interpret unstructured binary
    data.'''
    
    def __init__(self):
        self._map_list = []
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

        
    def add(self, dt, **kwargs):
        '''Add a new data item definition to this binary map.'''
        spec = self._type_tbl[dt]

        kwargs.update(spec)
        cls = spec['cls']
        bd = cls(**kwargs)

        self._add_bd(bd)
        
        
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


    def __str__(self):
        '''Convert the whole binmap to string, i.e. print the information from all
        contained data items.'''
        
        return '\n'.join(str(bd) for bd in self._map_list)
