from ts_parser import DataStore, Folder, FolderHeader, File
import sys

def print_data_store(data_store):
    for i, folder in enumerate(data_store.folders):
        print(f"Folder {i}:")
        print(f" Header Name: {folder.header.name}")
        print(f" Number of Data Entries: {folder.header.num_entries}")
        for j, file in enumerate(folder.files):
            print(f" File {j}:")
            print(f" Name: {file.name}")
            print(f" Value Length: {file.len_val}")
            #print(f"   Value: {file.value.decode('utf-.value, bytes) else file.value}")
            print(f" Unk1: {file.unk1}, Unk2: {file.unk2}, Unk3: {file.unk3}")
        print()

def main():
    if len(sys.argv) < 2:
        print("usage: python parse_ts_file.py <input_file> [<output_file>]")
        exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) >= 3 else None

    with open(input_filename, 'rb') as f:
        data = f.read()
    
    data_store, _ = DataStore.parse_from_bytes(data, offset=0x140)
    print("Parsed Data Store:")
    print_data_store(data_store)

    basic_header = FolderHeader(name="NewFolder", num_entries=0)
    basic_folder = Folder(header=basic_header)

    basic_file = File(
        unk1=0,
        unk2=0,
        unk3=0,
        name="BasicFile",
        value=b"BasicValue"
    )
    basic_folder.add_file(basic_file)
    data_store.add_folder(basic_folder)

    print("after adding new basic folder:")
    print_data_store(data_store)

    # how to modify an existing entry
    if data_store.folders:
        first_folder = data_store.folders[0]
        first_folder.header.name = "ModifiedFolderName"
        
        if first_folder.files:
            first_file = first_folder.files[0]
            first_file.value = b"ModifiedValue"
            first_file.name = "ModifiedFileName"
    
    print("after modifying the first entry and its first data entry:")
    print_data_store(data_store)

    # adding multiple data entries to an entry
    cooler_header = FolderHeader(name="CoolerFolder(entry)", num_entries=0)
    cooler_folder = Folder(header=cooler_header)
    
    for i in range(3):
        cooler_file = File(
            unk1=i,
            unk2=i+1,
            unk3=i+2,
            name=f"CoolerFile{i}",
            value=f"CoolerValue{i}".encode('utf-8')
        )
        cooler_folder.add_file(cooler_file)
    data_store.add_folder(cooler_folder)
    
    print("after adding cooler entry:")
    print_data_store(data_store)

    # find specific entry and specific data field to modify
    folder_name = "SPPSVC\\55c92734-d682-4d71-983e-d6ec3f16059f"
    file_name = "__##USERSEP-RESERVED##__$$REARM-COUNT$$"

    specific_folder = data_store.find_folder_by_name(folder_name)
    if specific_folder:
        specific_file = specific_folder.find_file_by_name(file_name)
        if specific_file:
            # set to all 0's
            specific_file.value = bytes(len(specific_file.value))
            print(f"updated value of `{file_name}` in entry `{folder_name}` to all zeros")
    else:
        print(f"entry `{folder_name}` not found.")

    print("after modifying specific file:")
    print_data_store(data_store)

    folder_to_remove = "SPPSVC\\55c92734-d682-4d71-983e-d6ec3f16059f"
    if data_store.remove_folder(folder_to_remove):
        print(f"{folder_to_remove} deleted succesfully")
    else:
        print("womp womp")
    
    print("after removing folder:")
    print_data_store(data_store)

    folder = data_store.find_folder_by_name("__##USERSEP##\\$$_RESERVED_$$\\NAMESPACE__")
    if folder:
        if folder.remove_file("__##USERSEP-RESERVED##__$$RECOVERED-FLAG$$"):
            print("file removed succesfully")
        else:
            print("womp womp")

    if output_filename:
        modified_data = data[:0x140] + data_store.to_bytes()
        with open(output_filename, 'wb') as f:
            f.write(modified_data)
        
        print(f"modified data written to {output_filename}")

if __name__ == '__main__':
    main()
