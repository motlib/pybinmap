import pytest

from .. import BinMap


testdata = bytes([0x12, 0x34, 0x56, 0x78, 0x34, 0x32, 0x30, 0x30, 0x20])


def test_binmap():
    bm = BinMap()
    
    bm.add(dt='bool', name='enabled', start=1, length=1)
    bm.add(dt='uint', name='testval', start=8, length=8)
    bm.add(dt='ascii', name='answer', start=8*4, length=8*2)

    bm.set_data(testdata)

    assert bm.get_value('enabled') == 1
    assert bm.get_value('testval') == 0x34
    assert bm.get_value('answer') == '42'

    
def test_binmap_predef_params():
    bm = BinMap()
    bm.add(dt='bool1', name='b1', start=1)
    bm.add(dt='ascii', name='ascii', start=8*3, length=8*3)
    bm.add(dt='uint', name='test', start=0, length=8)

    bm.set_data(testdata)

    assert bm.get_value('b1') == 1

    
def test_binmap_missing_param():
    bm = BinMap()

    with pytest.raises(TypeError):
        bm.add(dt='bool1', name='b1')

        
def test_binmap_str():
    bm = BinMap()
    
    bm.add(dt='bool', name='enabled', start=1, length=1)
    bm.add(dt='uint', name='testval', start=8, length=8)
    bm.add(dt='ascii', name='answer', start=8*4, length=8*2)

    bm.set_data(testdata)
    
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
    bm = BinMap()

    params['name'] = 'testval'
    
    bm.add(**params)
    bm.set_data(testdata)

    assert bm.get_value('testval') == result


def test_fill_unmapped():
    bm = BinMap()
    
    bm.add(dt='bool', name='enabled', start=1, length=1)
    bm.add(dt='uint', name='testval', start=8, length=8)
    bm.add(dt='ascii', name='answer', start=8*4, length=8*2)

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

    
