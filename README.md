# PyBinMap

`pybinmap` is a library to help interpreting binary data. This is e.g. useful
when reverse engineering a data structure or when receiving any kind of
unstructured binary data dump and need to make sense of it. 

The functionality is comparable to the `struct` module in the Python standard
library, but with many more features. 


## Usage

Let's say you have binary data like this:

```python
data = bytes([0x12, 0x34, 0x56, 0x78, 0x34, 0x32])
```

And you know, that there is 

* a bit called `enabled` in the first byte, bit 2
* an 4 bit unsigned int called `testval` in the second byte
* an two-character ascii string called `answer` in bytes 4 and 5

Then you can do the following:

```python
bm = BinMap()
bm.add(dt='bool', name='enabled', start=2, length=1)
bm.add(dt='uint', name='testval', start=8, length=4)
bm.add(dt='ascii', name='answer', start=4*8, length=2*8)

print(str(bm))
```

The result looks like this:

```text
0000:1+1 enabled = True [raw: 0x01]
0001:0+8 testval = 52 [raw: 0x34]
0004:0+16 answer = 42 [raw: 0x34 0x32]
```

Note: Addresses are written as `byte_pos:bit_pos+bit_length`. 

You can also retrieve single values or a dictionary with all values:

```python
answer = bm.get_value('answer')
idata = bm.get_dict()
```

## Development

Development takes place here: https://github.com/motlib/pybinmap

Feel free to create issues if you find bugs or have suggestions for
improvement. Pull requests are also fine :-)

