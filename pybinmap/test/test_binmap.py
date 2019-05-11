import pytest

from .. import BinMap


testdata = bytes([0x12, 0x34, 0x56, 0x78, 0x34, 0x32, 0x30, 0x30, 0x20])


def _get_default_binmap():
    bm = BinMap()

    bm.add(dt='bool', name='enabled', start=1, length=1)
    bm.add(dt='uint', name='testval', start=8, length=8)
    bm.add(dt='ascii', name='answer', start=8*4, length=8*2)

    bm.set_data(testdata)

    return bm


def test_binmap():
    bm = _get_default_binmap()

    assert bm.get_value('enabled') == 1
    assert bm.get_value('testval') == 0x34
    assert bm.get_value('answer') == '42'


def test_binmap_setup_missing_param():
    bm = _get_default_binmap()

    with pytest.raises(KeyError):
        bm.add(dt='bool1', name='b1')


def test_binmap_str():
    bm = _get_default_binmap()

    # ensure that we can convert to string
    print(bm)


testspec_all_datatypes = [
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

@pytest.mark.parametrize('params,result', testspec_all_datatypes)
def test_all_datatypes(params, result):
    '''Run through all available data types and use them at least once.'''

    bm = BinMap()

    params['name'] = 'testval'

    bm.add(**params)
    bm.set_data(testdata)

    tv = bm.get_item('testval')

    # check for expected value
    assert tv.value == result
    # ensure that length calculation always works
    assert tv.length == tv.end - tv.start + 1


def test_fill_unmapped():
    '''Test function to add raw data items for all unmapped areas.'''

    bm = _get_default_binmap()
    bm.fill_unmapped()

    bm.set_data(testdata)

    um0 = bm.get_item('unmapped_000')
    assert um0.start == 0
    assert um0.end == 0
    assert um0.length == 1

    um1 = bm.get_item('unmapped_001')
    assert um1.start == 2
    assert um1.end == 7
    assert um1.length == 6

    um2 = bm.get_item('unmapped_002')
    assert um2.start == 16
    assert um2.end == 31
    assert um2.length == 16


def test_fill_unmapped_with_end_address():
    '''Check if filling up to end address works.'''

    bm = _get_default_binmap()
    bm.fill_unmapped(end_addr=800)

    um3 = bm.get_item('unmapped_003')
    assert um3.start == 48
    assert um3.end == 800


def test_dict_access():
    '''Test successful dict based access to binmap information.'''

    bm = _get_default_binmap()

    assert bm['enabled'] == True
    assert bm['testval'] == 0x34


def test_dict_access_non_existent_element():
    '''Test unsuccessful dict based access to binmap information.'''

    bm = _get_default_binmap()

    with pytest.raises(KeyError):
        bm['non_existent_value']
