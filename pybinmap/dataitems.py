from collections import OrderedDict


class DataItem():
    '''Base class for binary data extraction. Needs to be subclassed to interpret
    data.'''

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


    @property
    def spec(self):
        '''The arguments used to create this data item.'''

        return self._args


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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._encoding = kwargs.get('encoding', 'ascii')

    def calc_value(self):
        return self._raw_value.decode('ascii')


class UIntDataItem(DataItem):
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
