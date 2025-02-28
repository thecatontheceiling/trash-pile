from importlib.metadata import files
from typing import List, Optional, Tuple

class FolderHeader:
    def __init__(self, name: str, num_entries: int):
        self.name = name
        self.num_entries = num_entries
        self.len_name = len(name.encode('utf-16le') + b'\x00\x00')

    @classmethod
    def parse_from_bytes(cls, data: bytes, offset: int) -> Tuple['FolderHeader', int]:
        initial_offset = offset

        len_name = int.from_bytes(data[offset:offset+4], 'little')
        offset += 4

        name_bytes = data[offset:offset+len_name]
        name = name_bytes.decode('utf-16le').rstrip('\x00')
        offset += len_name

        num_entries = int.from_bytes(data[offset:offset+4], 'little')
        offset += 4

        # padding is aligned to 4 bytes
        padding = (4 - (offset - initial_offset) % 4) % 4
        offset += padding

        tsd_header = cls(name, num_entries)
        tsd_header.len_name = len_name
        return tsd_header, offset

    def to_bytes(self) -> bytes:
        name_bytes = self.name.encode('utf-16le') + b'\x00\x00'
        self.len_name = len(name_bytes)

        result = b''
        result += self.len_name.to_bytes(4, 'little')
        result += name_bytes
        result += self.num_entries.to_bytes(4, 'little')

        padding = (4 - len(result) % 4) % 4
        result += b'\x00' * padding

        return result


class File: # TSDData
    def __init__(self, unk1: int, unk2: int, unk3: int, name: str, value: bytes):
        self.unk1 = unk1
        self.unk2 = unk2
        self.unk3 = unk3
        self.name = name
        self.value = value
        self.len_name = len(name.encode('utf-16le') + b'\x00\x00')
        self.len_val = len(value)

    @classmethod
    def parse_from_bytes(cls, data: bytes, offset: int) -> Tuple['File', int]:
        initial_offset = offset

        unk1 = int.from_bytes(data[offset:offset+4], 'little')
        offset += 4
        unk2 = int.from_bytes(data[offset:offset+4], 'little')
        offset += 4

        len_name = int.from_bytes(data[offset:offset+4], 'little')
        offset += 4
        len_val = int.from_bytes(data[offset:offset+4], 'little')
        offset += 4

        unk3 = int.from_bytes(data[offset:offset+4], 'little')
        offset += 4

        name_bytes = data[offset:offset+len_name]
        name = name_bytes.decode('utf-16le').rstrip('\x00')
        offset += len_name

        value = data[offset:offset+len_val]
        offset += len_val

        padding = (4 - (offset - initial_offset) % 4) % 4
        offset += padding

        tsd_data = cls(unk1, unk2, unk3, name, value)
        tsd_data.len_name = len_name
        tsd_data.len_val = len_val
        return tsd_data, offset

    def to_bytes(self) -> bytes:
        name_bytes = self.name.encode('utf-16le') + b'\x00\x00'
        self.len_name = len(name_bytes)
        self.len_val = len(self.value)

        result = b''
        result += self.unk1.to_bytes(4, 'little')
        result += self.unk2.to_bytes(4, 'little')
        result += self.len_name.to_bytes(4, 'little')
        result += self.len_val.to_bytes(4, 'little')
        result += self.unk3.to_bytes(4, 'little')
        result += name_bytes
        result += self.value

        padding = (4 - len(result) % 4) % 4
        result += b'\x00' * padding

        return result


class Folder: # TSEntry
    def __init__(self, header: FolderHeader, files: Optional[List[File]] = None):
        self.header = header
        self.files = files if files is not None else []

    @classmethod
    def parse_from_bytes(cls, data: bytes, offset: int) -> Tuple['Folder', int]:
        header, offset = FolderHeader.parse_from_bytes(data, offset)
        files = []
        for _ in range(header.num_entries):
            file, offset = File.parse_from_bytes(data, offset)
            files.append(file)
        return cls(header, files), offset

    def to_bytes(self) -> bytes:
        self.header.num_entries = len(self.files)
        result = self.header.to_bytes()
        for file in self.files:
            result += file.to_bytes()
        return result

    def add_file(self, file: File):
        self.files.append(file)
        self.header.num_entries = len(self.files)
    
    def find_file_by_name(self, file_name: str) -> Optional[File]:
        for file in self.files:
            if file.name == file_name:
                return file
        return None
    
    def remove_file(self, file_name: str) -> bool:
        for i, file in enumerate(self.files):
            if file.name == file_name:
                del self.files[i]
                self.header.num_entries = len(self.files)
                return True
        return False


class DataStore:
    def __init__(self, folders: Optional[List[Folder]] = None):
        self.folders = folders if folders is not None else []
        self.num_entries = len(self.folders)

    @classmethod
    def parse_from_bytes(cls, data: bytes, offset: int = 0x140) -> Tuple['DataStore', int]:
        num_entries = int.from_bytes(data[offset:offset+4], 'little')
        offset += 4

        folders = []
        for _ in range(num_entries):
            folder, offset = Folder.parse_from_bytes(data, offset)
            folders.append(folder)
        
        data_store = cls(folders)
        data_store.num_entries = num_entries
        return data_store, offset

    def to_bytes(self) -> bytes:
        self.num_entries = len(self.folders)
        result = b''
        result += self.num_entries.to_bytes(4, 'little')
        for folder in self.folders:
            result += folder.to_bytes()
        return result

    def add_folder(self, folder: Folder):
        self.folders.append(folder)
        self.num_entries = len(self.folders)
    
    def remove_folder(self, folder_name: str) -> bool:
        for i, folder in enumerate(self.folders):
            if folder.header.name == folder_name:
                del self.folders[i]
                self.num_entries = len(self.folders)
                return True
        return False
    
    def find_folder_by_name(self, entry_name: str) -> Optional[Folder]:
        for entry in self.folders:
            if entry.header.name == entry_name:
                return entry
        return None