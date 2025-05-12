from struct import unpack, pack
import mmap
from io import BytesIO

YCHUNK_TYPE = {
	'YOBJ': 2,
	'YANM': 3,
	'POF0': 1,
	}



def GetChunkType(wantedType='YOBJ'):

	return YCHUNK_TYPE.get(wantedType, None)

def ReadChunkData(file):
	file.seek(4)
	pointer = unpack('<I', file.read(4))[0]
	file.seek(8)
	file2 = file.read(pointer)
	file2 = BytesIO(file2)
	file.seek(pointer + 8)
	POF0 = unpack('4s', file.read(4))[0].decode('ascii')
	Length = unpack('<I', file.read(4))[0]
	entries, newFile = DecodePOF0(file, Length, file2)
	file.close()
	return entries, newFile

def DecodePOF0(file, Length, newFile, endian='<'):
	WORD = 0x80
	BYTE = 0x40
	DWORD = 0xC0
	Entries = []

	while 0 < Length:
		var1 = unpack('B', file.read(1))[0]
		if var1 & 0x00C0 == DWORD:
			file.seek(-1, 1)
			var1 = unpack(f'{endian}I', file.read(4))[0]
			var1 <<= 2
			newFile.seek(var1)
			ptr = unpack(f'{endian}I', newFile.read(4))[0]
			Entries.append(var1)
			Length -= 4

		elif var1 & 0x00C0 == WORD:
			file.seek(-1, 1)
			var1 = unpack(f'{endian}H', file.read(2))[0]
			decodedVar = var1 & 0x3FFF
			decodedVar <<= 2
			newFile.seek(decodedVar)
			ptr = unpack(f'{endian}I', newFile.read(4))[0]
			Entries.append(decodedVar)
			Length -= 2

		elif var1 & 0x00C0 == BYTE:
			decodedVar = var1 & 0x003F
			decodedVar <<= 2
			newFile.seek(decodedVar)
			ptr = unpack(f'{endian}I', newFile.read(4))[0]
			Entries.append(decodedVar)
			Length -= 2 # fix zeroes by faking consumption
		else:
			assert Length == 0,(f'{file.tell()}, {Length}')
	return Entries, newFile



	









