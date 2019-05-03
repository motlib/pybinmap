import pytest

from .. import BinMap


testdata = bytes([0x12, 0x34, 0x56, 0x78, 0x34, 0x32])


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
    bm.add(dt='ascii', name='answer', start=8*3, length=8*2)

    bm.set_data(testdata)
    
    print(bm)
