'''Unit tests for BinMap implementation.'''

import pytest

from .. import BinMap


TESTDATA = bytes([0x12, 0x34, 0x56, 0x78, 0x34, 0x32, 0x30, 0x30, 0x20])


def _get_default_binmap():
    binmap = BinMap()

    binmap.add(dt='bool', name='enabled', start=1, length=1)
    binmap.add(dt='uint', name='testval', start=8, length=8)
    binmap.add(dt='ascii', name='answer', start=8*4, length=8*2)

    binmap.set_data(TESTDATA)

    return binmap


def test_binmap():
    '''Simple test for extracting values.'''

    binmap = _get_default_binmap()

    assert binmap.get_value('enabled') == 1
    assert binmap.get_value('testval') == 0x34
    assert binmap.get_value('answer') == '42'


def test_binmap_setup_missing_param():
    '''Try to add data item with missing parameters.'''
    binmap = _get_default_binmap()

    with pytest.raises(KeyError):
        binmap.add(dt='bool1', name='b1')


def test_binmap_str():
    '''Test string conversion of BinMap instance.'''
    binmap = _get_default_binmap()

    # ensure that we can convert to string
    print(binmap)


TESTSPEC_ALL_DATATYPES = [
    ({'dt':'raw', 'start':0, 'length':8}, bytes([0x12])),
    ({'dt':'uint', 'start':0, 'length':8}, 0x12),
    ({'dt':'uint8', 'start':0}, 0x12),
    ({'dt':'uint16', 'start':0}, 0x3412),
    ({'dt':'uint16', 'start':0, 'endian': 'big'}, 0x1234),
    ({'dt':'uint32', 'start':0}, 0x78563412),
    ({'dt':'uint64', 'start':0}, 0x3030323478563412),
    ({'dt':'ascii', 'start':4*8, 'length':16}, '42'),
    ({'dt':'utf8', 'start':4*8, 'length':16}, '42'),
    ({'dt':'bool', 'start':0, 'length':1}, False),
    ({'dt':'bool1', 'start':1}, True),
    ({'dt':'bool8', 'start':0}, True),
]

@pytest.mark.parametrize('params,result', TESTSPEC_ALL_DATATYPES)
def test_all_datatypes(params, result):
    '''Run through all available data types and use them at least once.'''

    binmap = BinMap()

    params['name'] = 'testval'

    binmap.add(**params)
    binmap.set_data(TESTDATA)

    item = binmap.get_item('testval')

    # check for expected value
    assert item.value == result
    # ensure that length calculation always works
    assert item.length == item.end - item.start + 1


def test_fill_unmapped():
    '''Test function to add raw data items for all unmapped areas.'''

    binmap = _get_default_binmap()
    binmap.fill_unmapped()

    binmap.set_data(TESTDATA)

    um0 = binmap.get_item('unmapped_000')
    assert um0.start == 0
    assert um0.end == 0
    assert um0.length == 1

    um1 = binmap.get_item('unmapped_001')
    assert um1.start == 2
    assert um1.end == 7
    assert um1.length == 6

    um2 = binmap.get_item('unmapped_002')
    assert um2.start == 16
    assert um2.end == 31
    assert um2.length == 16


def test_fill_unmapped_with_end_address():
    '''Check if filling up to end address works.'''

    binmap = _get_default_binmap()
    binmap.fill_unmapped(end_addr=800)

    um3 = binmap.get_item('unmapped_003')
    assert um3.start == 48
    assert um3.end == 800


def test_dict_access():
    '''Test successful dict based access to binmap information.'''

    binmap = _get_default_binmap()

    assert binmap['enabled']
    assert binmap['testval'] == 0x34


def test_dict_access_non_existent_element():
    '''Test unsuccessful dict based access to binmap information.'''

    binmap = _get_default_binmap()

    with pytest.raises(KeyError):
        _ = binmap['non_existent_value']


def test_binmap_iterator():
    '''Test to iterate over the key,value tuples in binmap.'''

    binmap = _get_default_binmap()

    for name,val in binmap:
        print(name, ':', val)
        

def test_binmap_item_iterator():
    '''Iterate over the underlying DataItem instances.'''

    binmap = _get_default_binmap()

    for item in binmap.items():
        print(item.name, ':', item.value)
