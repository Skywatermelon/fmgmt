#!/usr/bin/env python3

import sys
import getopt
import os
import json
import re
import time
from datetime import datetime
import pprint

# ==================================================
# INITIALIZE DIRECTORIES
# ==================================================
REPLACEMENTS_DIR = "renamer_replacements"

# Create replacement directory if it doesn't exist
if not os.path.exists(REPLACEMENTS_DIR):
    os.makedirs(REPLACEMENTS_DIR)
    print(f"INFO: Created replacement directory {REPLACEMENTS_DIR}.")
    print("INFO: Please add your custom replacement JSON files and restart the program.")
    sys.exit(2)

# ==================================================
# FLAG VARIABLES - Initialized for program settings
# ==================================================
backup_flag = False
step_flag = False
sleep_arg = -1
verbose_flag = False
path_arg = ""
replace_args = []
replace_json_args = []
extension_arg = ""
expression_flag = False
position_arg = -1
reverse_flag = False
recursive_flag = False
delete_arg = -1
add_arg = ""
whitespace_arg = ""

# ==========================
# HELP MESSAGE SECTION
# ==========================
def print_help():
    help_text = """
Program Behaviour:
  -h, --help               Print this help message
  -b, --backup             Backup: All filenames are backed up to a text file
  -s, --step               Step: Prompts for each file and replacement category.
  -t, --sleep=<SECONDS>    Sleep: A timer between 1 and 60 seconds to wait between renaming operations.
  -b, --verbose            Verbose: More output messages.

Program Functions:
  -p, --path=<DIRECTORY>   Target path for renaming operations.
  -l, --replace=<STRING>   Inline replacements "{target,replace}" format.
  -j, --replace_json=<FILE(S)>  JSON files in renamer_replacements directory (comma-separated).
  -e, --extension=<EXT>    File extension filter (e.g., ".txt" or "txt").
  -x, --expression         Enables regular expressions in replacements.
  -c, --position=<NUM>     Position for add/delete operations.
  -v, --reverse            Reverses delete (-d) or add (-a) operations.
  -r, --recursive          Recursively processes directories.
  -d, --delete=<NUM>       Deletes characters from the specified position.
  -a, --add=<STRING>       Adds a string at the specified position.
  -w, --whitespace=<CHAR>  Replaces remaining whitespace in filenames.
"""
    print("INFO:", help_text)
    sys.exit(0)

# =====================================================
# ARGUMENT PROCESSING SECTION
# =====================================================
def process_args(argv):
    global backup_flag, step_flag, sleep_arg, path_arg, replace_args, verbose_flag
    global replace_json_args, extension_arg, expression_flag, position_arg
    global reverse_flag, recursive_flag, delete_arg, add_arg, whitespace_arg

    try:
        opts, args = getopt.getopt(
            argv,
            "hbkst:p:l:j:e:xc:vrd:a:w:",
            [
                "help", "verbose", "backup", "step", "sleep=",
                "path=", "replace=", "replace_json=",
                "extension=", "expression", "position=",
                "reverse", "recursive", "delete=", "add=",
                "whitespace=",
            ],
        )
    except getopt.GetoptError as err:
        print("ERROR:", str(err))
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
        elif opt in ("-b", "--verbose"):
            verbose_flag = True
        elif opt in ("-k", "--backup"):
            backup_flag = True
            if verbose_flag:
                print(f"INFO: Backup mode enabled.")
        elif opt in ("-s", "--step"):
            step_flag = True
            if verbose_flag:
                print(f"INFO: Step mode enabled.")
        elif opt in ("-t", "--sleep"):
            sleep_arg = int(arg)
            if not (1 <= sleep_arg <= 60):
                print("ERROR: Sleep time must be between 1 and 60 seconds.")
                sys.exit(2)
            if verbose_flag:
                print(f"INFO: Sleep mode set to {sleep_arg} seconds.")
        elif opt in ("-p", "--path"):
            path_arg = arg
            if verbose_flag:
                print(f"INFO: Path set to: {path_arg}")
        elif opt in ("-l", "--replace"):
            replace_args.extend(parse_replacements(arg))
        elif opt in ("-j", "--replace_json"):
            files = [os.path.join(REPLACEMENTS_DIR, f.strip()) for f in arg.split(",")]
            replace_json_args.extend(files)
        elif opt in ("-e", "--extension"):
            extension_arg = arg.lstrip(".")
            if verbose_flag:
                print(f"INFO: Extension(s): {extension_arg}.")
        elif opt in ("-x", "--expression"):
            expression_flag = True
            if verbose_flag:
                print(f"INFO: Expressions enabled.")
        elif opt in ("-c", "--position"):
            position_arg = int(arg)
        elif opt in ("-v", "--reverse"):
            reverse_flag = True
            if verbose_flag:
                print(f"INFO: Reverse mode enabled.")
        elif opt in ("-r", "--recursive"):
            recursive_flag = True
            if verbose_flag:
                print(f"INFO: Recursive mode enabled.")
        elif opt in ("-d", "--delete"):
            delete_arg = int(arg)
        elif opt in ("-a", "--add"):
            add_arg = arg
        elif opt in ("-w", "--whitespace"):
            whitespace_arg = arg

    # Argument Validation
    if (delete_arg != -1 and position_arg == -1) or (delete_arg == -1 and position_arg != -1):
        print("ERROR: Both --delete (-d) and --position (-c) must be set.")
        sys.exit(2)

    if (add_arg != "" and position_arg == -1) or (add_arg == "" and position_arg != -1):
        print("ERROR: Both --add (-a) and --position (-c) must be set.")
        sys.exit(2)

# =====================================================
# REPLACEMENTS SECTION
# =====================================================

def parse_replacements(replacement_str):
    pattern = re.compile(r"\{(.*?),(.*?)\}")
    matches = pattern.findall(replacement_str)
    if not matches:
        print("ERROR: Invalid replacement string format.")
        sys.exit(2)
    return [{"from": m[0], "to": m[1]} for m in matches]


def load_json_files(files):
    merged_replacements = {"Replacements": []}

    for file in files:
        if not file.lower().endswith(".json"):
            print(f"ERROR: {file} is not a JSON file.")
            sys.exit(2)
        if verbose_flag:
            print(f"File: {file}")
        try:
            with open(file, "r") as f:
                data = json.load(f)
                if "Replacements" not in data or not isinstance(data["Replacements"], list):
                    raise ValueError("Missing or invalid 'Replacements' key in JSON file.")

                # Step-through processing for each category
                for category in data["Replacements"]:
                    if "pairs" in category and isinstance(category["pairs"], list):
                        if step_flag:
                            user_response = input(
                                f"Include category '{category.get('category', 'Unknown')}'? (y/n): "
                            ).strip().lower()
                            if user_response not in ("y", "yes"):
                                continue

                        merged_replacements["Replacements"].append(category)

                        if verbose_flag:
                            print(
                                f"INFO: Loaded category '{category.get('category', 'Unknown')}' from '{file}' "
                                f"with {len(category['pairs'])} replacement pair(s)."
                            )
                    else:
                        print(
                            f"ERROR: Missing or invalid 'pairs' in category {category.get('category', 'Unknown')}."
                        )

        except (json.JSONDecodeError, ValueError) as e:
            print(f"ERROR: Failed to load or parse {file}: {str(e)}")
            sys.exit(2)

    if verbose_flag:
        print(f"\nINFO: Loaded a total of {len(merged_replacements['Replacements'])} categories from {len(files)} file(s).")
        print("INFO: Final Merged Replacements:")
        pprint.pprint(merged_replacements, indent=4, width=100, compact=False)

    return merged_replacements

# =====================================================
# BACKUP SECTION
# =====================================================

def create_backup_dir():
    if backup_flag:
        os.makedirs("renamer_backups", exist_ok=True)


def backup_filenames(files, replacements_merged_json):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file = f"renamer_backups/{timestamp}_renamer_backup.txt"
    with open(backup_file, "w") as f:
        f.write(json.dumps(replacements_merged_json, indent=4))
        f.write("\n\n")
        for old, new in files:
            f.write(f"{old} -> {new}\n")
    print(f"INFO: Backup completed {backup_file}.")

# =====================================================
# FILE RENAMING SECTION
# =====================================================

def rename_files(files, preview_mode=False):
    """
    Renames files or previews changes if preview_mode is enabled.

    Args:
        files (list): List of file rename pairs (old, new).
        preview_mode (bool): If True, previews changes without renaming.

    Returns:
        bool: True if changes proceeded, False if the user canceled.
    """
    # Initialize return value
    return_value = False

    if not files:
        print("INFO: No files to process.")
        return return_value

    total_files = len(files)
    number_width = len(str(total_files))  # Calculate width for numbering

    # Preview Mode: Display proposed changes
    if preview_mode:
        print("\nPREVIEW OF CHANGES:")
        print("=" * (number_width + 50))

        for idx, (old, new) in enumerate(files, start=1):
            old_name = os.path.basename(old)
            new_name = os.path.basename(new)
            # Use padded numbering based on total file count
            print(f"[{idx:>{number_width}}] {old_name} -> {new_name}")

        print("=" * (number_width + 50))
        print("\nDo you want to proceed with these changes? (y/n): ", end="")

        # Prompt user confirmation
        user_input = input().strip().lower()
        if user_input not in ("y", "yes"):
            print("INFO: Operation canceled by the user.")
            return return_value  # Return False if user cancels
        
        print("INFO: Proceeding with file renaming.\n")
        return_value = True

    # Rename Files
    for idx, (old, new) in enumerate(files, start=1):
        if not os.path.exists(old):
            print(f"ERROR: File not found {os.path.basename(old)}, skipping.")
            continue

        try:
            # Extract directory, filename, and extension
            file_dir, file_name = os.path.split(new)
            name, ext = os.path.splitext(file_name)

            # Clean up file name
            cleaned_name = re.sub(r'\s+', ' ', name).strip()
            cleaned_file = f"{cleaned_name}{ext}"
            cleaned_path = os.path.join(file_dir, cleaned_file)

            # Rename operation
            os.rename(old, cleaned_path)

            percentage = int((idx / total_files) * 100)
            print(f"[{percentage:>{number_width}}%] {os.path.basename(old)} -> {cleaned_file}")
            time.sleep(sleep_arg)

        except Exception as e:
            print(f"ERROR: Failed to rename {os.path.basename(old)} to {os.path.basename(new)}: {str(e)}")

    # Ensure correct return value is set if renaming succeeded
    return_value = True
    return return_value

# =====================================================
# MAIN FUNCTION
# =====================================================

def main():
    process_args(sys.argv[1:])

    # Load JSON files
    for file in os.listdir(REPLACEMENTS_DIR):
        if file.lower().endswith(".json"):
            if verbose_flag:
                print(f"INFO: Found {file} replacement file.")
            replace_json_args.append(os.path.join(REPLACEMENTS_DIR, file))

    replacements = load_json_files(replace_json_args)
    create_backup_dir()

    # Collect files
    if os.path.isfile(path_arg):
        if verbose_flag:
            print(f"INFO: Single file operation: {path_arg}.")
        files_to_process = [path_arg]

    elif os.path.isdir(path_arg):
        files_to_process = [
            os.path.join(root, file)
            for root, _, files in os.walk(path_arg) if recursive_flag
            for file in files
            if file.lower().endswith(f".{extension_arg.lower()}") or not extension_arg
        ] if recursive_flag else [
            os.path.join(path_arg, file)
            for file in os.listdir(path_arg)
            if os.path.isfile(os.path.join(path_arg, file)) and
            (file.lower().endswith(f".{extension_arg.lower()}") or not extension_arg)
        ]

        if verbose_flag:
            print(f"INFO: Found {len(files_to_process)} files to process.")
    else:
        print("ERROR: Specified path is invalid.")
        sys.exit(2)

    processed_files = []

    for idx, file_path in enumerate(files_to_process, start=1):
        if not os.path.exists(file_path):
            print(f"ERROR: File not found {file_path}, skipping.")
            continue

        file_dir, file_name = os.path.split(file_path)
        original_name, file_ext = os.path.splitext(file_name)

        # Apply replacements
        for category in replacements["Replacements"]:
            for pair in category["pairs"]:
                target, replacement = pair["from"], pair["to"]

                if not target.strip():
                    print(f"WARNING: Skipping empty target '{target}'.")
                    continue

                try:
                    # Check if expressions are enabled and if this category allows regular expressions
                    if expression_flag and category.get("regular_expressions", False):
                        
                        # Perform a regex search for the target in the original file name
                        if re.search(target, original_name):
                            
                            # Replace occurrences of the target with the replacement using regex
                            updated_name = re.sub(target, replacement, original_name)
                            
                            # Check if the file name was updated
                            if updated_name != original_name:
                                original_name = updated_name
                                
                                # Print info if verbose mode is enabled
                                if verbose_flag:
                                    print(f"INFO: Regex match found: '{target}' in {original_name}")
                        
                        else:
                            # Print info if no regex match was found and verbose mode is enabled
                            if verbose_flag:
                                print(f"INFO: No regex match for '{target}' in '{original_name}'.")

                    else:  # String-based replacement if regex is not enabled
                        
                        # Check if the target string exists in the original file name
                        if target in original_name:
                            
                            # Perform a string replacement
                            updated_name = original_name.replace(target, replacement)
                            
                            # Check if the file name was updated
                            if updated_name != original_name:
                                original_name = updated_name
                                
                                # Print info if verbose mode is enabled
                                if verbose_flag:
                                    print(f"INFO: String found: '{target}' in {original_name}")
                        
                        else:
                            # Print info if no string match was found and verbose mode is enabled
                            if verbose_flag:
                                print(f"INFO: No string match for '{target}' in '{original_name}'.")

                except re.error as e:
                    print(f"ERROR: Invalid regex '{target}' in '{category['category']}': {str(e)}")

        # Generate new file path
        new_file_name = f"{original_name}{file_ext}"
        new_file_path = os.path.join(file_dir, new_file_name)

        # Check if renaming is required
        if file_path != new_file_path:
            processed_files.append((file_path, new_file_path))

    # Rename files
    rename_files(processed_files, preview_mode=True)

    # Backup filenames if required
    if backup_flag:
        backup_filenames(processed_files, replacements)

    print("INFO: Processing complete.")


if __name__ == "__main__":
    main()