'''Implementation of DataItem class and subclasses to convert binary data to a
meaningful representation.'''

def format_addr(addr):
    '''Format a bit address as byte / bit address string.'''

    byte, bit = divmod(addr, 8)

    return '{byte:04x}:{bit}'.format(
        byte=byte,
        bit=bit)


class DataItem():
    '''Base class for binary data extraction. This one just extracts a raw byte
    array. Needs to be subclassed to interpret data.

    '''

    def __init__(self, **kwargs):
        self._args = kwargs

        # todo check for required args
        self._name = kwargs['name']
        self._start = kwargs['start']
        self._length = kwargs['length']

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

        (byte_pos, bit_pos) = divmod(abs_bit, 8)

        # extract one bit (0 or 1) from input data
        bit_val = (self._data[byte_pos] & (1 << bit_pos)) >> bit_pos

        return bit_val


    def extract_raw_value(self):
        '''Extract the data area specified by start and length values into a bytes()
        structure.'''

        bytelist = []
        bit_count = 0
        byte_val = 0

        # end + 1, because for range, the top value is not reached
        for addr in range(self.start, self.end + 1):
            bit_val = self.get_bit(addr)

            # shift it to the correct output position
            byte_val += bit_val << (bit_count % 8)

            bit_count += 1
            if bit_count == 8:
                bytelist.append(byte_val)
                byte_val = 0
                bit_count = 0

        if bit_count != 0:
            bytelist.append(byte_val)

        return bytes(bytelist)


    def calc_value(self):
        '''Implementation in base class returns the raw byte array for this
        item. Subclasses have to override it to extract meaningful data.'''

        return self._raw_value


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

        if self._data is None:
            raise ValueError('No data set.')

        return self._raw_value


    @property
    def value(self):
        '''The interpreted value of this data item.'''

        if self._data is None:
            raise ValueError('No data set.')

        return self._value


    @property
    def spec(self):
        '''The arguments used to create this data item.'''

        return self._args

    
    def __str__(self):
        '''Convert the data item to string.'''

        raw_str = ' '.join('0x{0:02x}'.format(v) for v in self.raw_value)

        return '{addr}+{length} {name} = {value} [raw: {r}]'.format(
            addr=format_addr(self.start),
            name=self._name,
            length=self._length,
            value=self.value,
            r=raw_str)


class CharDataItem(DataItem):
    '''DataItem subclass for string interpretation.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._encoding = kwargs.get('encoding', 'ascii')


    def calc_value(self):
        return self._raw_value.decode('ascii')


class UIntDataItem(DataItem):
    '''DataItem subclass for unsigned integer interpretation.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._endian = kwargs.get('endian', 'little')

        if self._endian not in ('little', 'big'):
            msg = (
                "Parameter 'endian' must be either 'big' or 'little' endian. "
                "Got '{0}'."
            )
            raise ValueError(msg.format(self._endian))


    def calc_value(self):
        if self._endian == 'big':
            raw_val = reversed(self._raw_value)
        else:
            raw_val = self._raw_value

        val = 0
        for byte_pos, byte_val in enumerate(raw_val):
            val += (1 << (8 * byte_pos)) * byte_val

        return val


class BoolDataItem(UIntDataItem):
    '''DataItem subclass for bool value interpretation. This first converts the
    underlying value to an unstigned integer. Any value not equal zero is
    interpreted as True, zero is interpreted as false.'''

    def calc_value(self):
        val = super().calc_value()

        # Convert the integer value to bool (0: False, everything else: True)
        return bool(val)
