import os
import sys
import shutil
import getopt

def print_usage():
    print("Usage: python3 script.py -p <path> [-f <file_extension>] [-d] [-c <directory_base_name>] [-n <number>] [-z <leading_zeros>]")
    print("### Variables:\n")
    print("-p: PATH: Specify the target path. The target path is relevant to whatever operation is being performed.")
    print("-r: RECURSIVE: Set the recursion flag which applies for multiple operation modes.")
    print("-n: NUMBER: Specify the number of operations (e.g., number of folders to create or number of files to process).")
    print("-z: ZEROS: Specify the number of enforced leading zeros for folder names when creating new folders using the -c flag.")
    print("### Operations:\n")
    print("-f: FOLDERIFY: Create folders for files by the same name and move them into each corresponding folder that match their names. Specify the file extension as an argument to filter or leave empty for all file type. Will operate recursively with the -r flag.")
    print("-m: MERGE: Take files that have names that start with a partial match of a folder in the same directory and move the file inside. Specify the file extension as an argument to filter or leave empty for all file type. Will operate recursively with the -r flag.")
    print("-d: DELETE: Delete empty folders in the target path.")
    print("-c: CREATE: Create new folders in the target path. The base name of the folders should follow this flag.")
    print("### Program Behaviour:\n")
    print("-V: VERBOSE: See verbose output during program execution as well as debug messages.")

    sys.exit(2)

# Variables
path = None
file_extension = None
folder_base_name = None
number_of_operations = 0
leading_zeros = None

# Flags
recursive = False
create_folders_for_files = False
create_folders_bulk = False
delete_empty = False
merge_files_named_folders = False

# Program Behaviour
verbose_mode = False
staging_mode = False

# Process command line arguments using getopt
try:
    opts, args = getopt.getopt(sys.argv[1:], "p:f:dVrc:n:z:m:") 
except getopt.GetoptError as e:
    print(f"ERROR: {e}")
    print_usage()

# Parse options
for opt, arg in opts:
    if opt == '-p':
        path = os.path.normpath(arg)
        if not os.path.isdir(path):
            print(f"ERROR: '{path}' is not a directory. Please specify a directory.")
            sys.exit(1)
    elif opt == '-f':
        create_folders_for_files = True
        file_extension = arg
        if not file_extension.startswith('.'):
            file_extension = '.' + file_extension
    elif opt == '-d':
        delete_empty = True
    elif opt == '-c':
        create_folders_bulk = True
        folder_base_name = arg
    elif opt == '-n':
        number_of_operations = int(arg)
    elif opt == '-m':
        merge_files_named_folders = True
        file_extension = arg
    elif opt == '-z':
        leading_zeros = int(arg)
    elif opt == '-r':
        recursive = True
    elif opt == '-V':
        verbose_mode = True
    elif opt == '-s':
        staging_mode = True


# If no path specified, use current directory
if not path:
    path = os.path.normpath(".")

def delete_empty_folders(path):
    empty_folders = [os.path.join(path, d) for d in os.listdir(path) 
                     if os.path.isdir(os.path.join(path, d)) and not os.listdir(os.path.join(path, d))]
    if not empty_folders:
        print("INFO: No empty folders found.")
        return

    print(f"INFO: Found {len(empty_folders)} empty folders:")
    for folder in empty_folders:
        print(folder)

    confirm = input("Do you want to delete these folders? (y/n): ")
    if confirm.lower() == 'y':
        for folder in empty_folders:
            os.rmdir(folder)
        print(f"INFO: Deleted ({len(empty_folders)}) empty folders.")
    else:
        print("INFO: Deletion cancelled.")

def create_folders_in_path(base_name, number, path, leading_zeros):
    total_digits = len(str(number)) if leading_zeros is None else leading_zeros+1
    for i in range(1, number + 1):
        folder_name = f"{base_name}{str(i).zfill(total_digits)}"
        try:
            os.mkdir(os.path.join(path, folder_name))
        except OSError as e:
            print(f"ERROR: Could not create folder {folder_name}: {e}")

def create_files_into_folders_same_name(path: str, file_extension: str = None, recursive: bool = False, number_of_operations: int = None):
    current_file_name = os.path.basename(__file__)
    directories_created = 0
    loop_iterations = 0
    renamed_files = 0

    # Set the directory walking mode based on the recursive flag
    if recursive:
        items = [(root, files, dirs) for root, dirs, files in os.walk(path)]
    else:
        root, dirs, files = next(os.walk(path))
        items = [(root, files, dirs)]

    for root, files, dirs in items:
        for file_name in files:
            # Skip hidden files and the script file itself
            if file_name.startswith('.') or file_name == current_file_name:
                continue

            # Check file extension if specified
            if file_extension and not file_name.endswith(file_extension):
                continue

            loop_iterations += 1
            
            # Split the filename into name and extension
            name, ext = os.path.splitext(file_name)
            # Remove any whitespace at the end of the name part (just before the extension)
            clean_name = name.rstrip()
            # Reattach the extension with the cleaned name
            clean_file_name = f"{clean_name}{ext}"

            if verbose_mode:
                print(f"DEBUG: Original file name = {file_name}.")
                print(f"DEBUG: Clean file name = {clean_file_name}.")
            
            # Rename the file to remove whitespace
            if clean_file_name != file_name:
                print(f"INFO: Renaming {file_name} to avoid files system issues.")
                renamed_files +=1
                old_file_path = os.path.join(root, file_name)
                new_file_path = os.path.join(root, clean_file_name)
                os.rename(old_file_path, new_file_path)
            else:
                if verbose_mode:
                    print(f"INFO: Renaming {file_name} to avoid file system issues.")
                new_file_path = os.path.join(root, clean_file_name)

            # Extract name and create directory without trailing whitespace
            name, ext = os.path.splitext(clean_file_name)
            new_directory = os.path.normpath(os.path.join(root, name))
            
            try:
                os.mkdir(new_directory)
                directories_created += 1
            except FileExistsError:
                pass

            dst_path = os.path.normpath(os.path.join(new_directory, clean_file_name))
            shutil.move(new_file_path, dst_path)

            # Limit the number of operations if specified
            if number_of_operations and loop_iterations >= number_of_operations:
                print(f"INFO: Reached operation limit: {number_of_operations}")
                return
    if renamed_files and verbose_mode:
            print(f"INFO: Renamed {renamed_files} files to prevent filesyems issues.")
    print(f"INFO: Directories created: {directories_created}")



def merge_files_into_folders_closest_match_directory_name(parent_directory: str, recursive: bool = False, file_extension: str = None):
    if recursive:
        items = [(root, dirs, files) for root, dirs, files in os.walk(parent_directory)]
    else:
        root, dirs, files = next(os.walk(parent_directory))
        items = [(root, dirs, files)]
        
    for root, dirs, files in items:
        for file in files:
            if file_extension is not None and not file.endswith(file_extension):
                print(f"INFO: Skipping {file}. Does not match file extension requirement {file_extension}.")
                continue
            
            file_path = os.path.join(root, file)
            best_match = None
            
            # Find the directory with the longest matching prefix
            for directory in dirs:
                if file.startswith(directory):
                    if best_match is None or len(directory) > len(best_match):
                        best_match = directory
            
            # Move the file if a matching directory is found
            if best_match:
                target_directory = os.path.join(root, best_match)
                os.makedirs(target_directory, exist_ok=True)
                target_path = os.path.join(target_directory, file)
                shutil.move(file_path, target_path)
                print(f"INFO: Moved '{file}' to '{target_directory}'")

# Execute based on options
if create_folders_for_files:
    create_files_into_folders_same_name(path, file_extension)

if delete_empty:
    delete_empty_folders(path)

if create_folders_bulk:
    if folder_base_name is None or number_of_operations <= 0:
        print("ERROR: Folder base name and number of operations must be specified for folder creation.")
        sys.exit(1)
    create_folders_in_path(folder_base_name, number_of_operations, path, leading_zeros)

if merge_files_named_folders:
    merge_files_into_folders_closest_match_directory_name(parent_directory=path, recursive=recursive, file_extension=file_extension)
