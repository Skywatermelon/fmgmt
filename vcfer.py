import os
import sys
import getopt
from datetime import datetime
from pathlib import Path

### Local Imports
from utils.file_handler import FileHandler
from utils.vcf_manager import VCFManager
from utils.directory_comparer import DirectoryComparer

def print_help():
    help_text = """
    Usage: vcf_analyzer.py [OPTIONS]

    Settings:
    -i, --input FILE                  INPUT: Set the input file or directory.
    -o, --output FILE                 OUTPUT: Set the ouptut file or directory.

    Options:
    -n, --new FILE,FN[,TEL,EMAIL]     NEW: Create a new contact and add it to the specified VCF file.
    -r, --report FILE                 REPORT: Generate a contact report from the specified VCF file.
    -m, --memberships FILE            MEMBERSHIPS: Display membership groups from the specified VCF file.
    -s, --split FILE                  SPLIT: Split the specified VCF file into individual files.
    -u, --uncommon FILE[DIR1, DIR2]   UNCOMMON: Compare and output the uncommon or different contacts between two directories.
    -c, --combine FILE                COMBINE: Combine a directory of VCF files into a single VCF file.
    -h, --help                        HELP: Display this help text.

    Examples:
    python vcf_analyzer.py -c "contacts.vcf,John Doe,+123456789,john@example.com"
    python vcf_analyzer.py -r contacts.vcf
    python vcf_analyzer.py -m contacts.vcf
    python vcf_analyzer.py -s contacts.vcf
    """
    print(help_text)

def get_download_folder():
    if os.name == 'nt':  # Windows
        download_folder = Path(os.getenv('USERPROFILE')) / 'Downloads'
    else:  # macOS and Linux
        download_folder = Path.home() / 'Downloads'
    return download_folder

def main():
    input_paths = None
    output_path = os.path.join(
        get_download_folder(),
        f"vcfer_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], "i:o:n:r:such",
            ["input=", "output=", "new=", "report=", "split", "uncommon", "combine", "help"]
        )
    except getopt.GetoptError as err:
        sys.exit(f"ERROR: {err}")

    flag_split_contacts = False
    flag_uncommon_files = False
    flag_combine_files = False

    file_handler = FileHandler()

    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input_paths = arg
        elif opt in ("-o", "--output"):
            output_path = arg
        elif opt in ("-n", "--new"):
            details = arg.split(",")
            if len(details) < 2:
                sys.exit("ERROR: FILE and FN (Full Name) are required.")
            file_path, fn = details[0], details[1]
            tel = details[2] if len(details) > 2 else None
            email = details[3] if len(details) > 3 else None
            analyzer = VCFManager(file_path)
            analyzer.create_contact(fn, tel, email)
        elif opt in ("-r", "--report"):
            if not input_paths:
                sys.exit("ERROR: Input path is required for reporting (-i).")
            file_handler.set_inputs(input_paths)
            if len(file_handler.input_files) != 1 or not os.path.isfile(file_handler.input_files[0]):
                sys.exit("ERROR: Reporting requires a single VCF file as input.")
            analyzer = VCFManager(file_handler.input_files[0])
            analyzer.tally_contents()
            analyzer.generate_report()
        elif opt in ("-s", "--split"):
            flag_split_contacts = True
        elif opt in ("-u", "--uncommon"):
            flag_uncommon_files = True
            file_handler.set_inputs(arg)
            if file_handler.count_input_files() != 2 or not file_handler.input_is_directory:
                sys.exit("ERROR: Uncommon comparison requires exactly two directories.")
            for path in file_handler.input_files:
                if not file_handler.has_file_type(".vcf", is_input=True):
                    sys.exit(f"ERROR: Directory '{path}' must contain at least one .vcf file.")
        elif opt in ("-c", "--combine"):
            flag_combine_files = True
            file_handler.set_inputs(input_paths)
            if file_handler.count_input_files() != 1 or not file_handler.input_is_directory:
                sys.exit("ERROR: Combine requires exactly one directory containing .vcf files.")
            if not file_handler.has_file_type(".vcf", is_input=True):
                sys.exit("ERROR: The directory must contain at least one .vcf file.")
        elif opt in ("-h", "--help"):
            print_help()
            sys.exit()

    # Validate output path
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)

    # Handle split functionality
    if flag_split_contacts:
        file_handler.set_inputs(input_paths)
        if file_handler.count_input_files() != 1 or not os.path.isfile(file_handler.input_files[0]):
            sys.exit("ERROR: Split requires exactly one VCF file as input.")
        analyzer = VCFManager(file_handler.input_files[0])
        analyzer.split_vcf(output_path)
        print(f"INFO: Split files saved in '{os.path.join(output_path, 'split')}'")

    # Handle uncommon comparison functionality
    if flag_uncommon_files:
        directories = file_handler.input_files
        dc = DirectoryComparer(
            dir1=directories[0],
            dir2=directories[1],
            output_dir=output_path
        )
        dc.compare()
        print(f"INFO: Uncommon files saved in '{os.path.join(output_path, 'uncommon')}'")

    # Handle combine functionality
    if flag_combine_files:
        directory = file_handler.input_files[0]
        
        # Ensure output file ends with .vcf
        if not output_path.lower().endswith(".vcf"):
            if "." in os.path.basename(output_path):
                sys.exit("ERROR: Output file must have a .vcf extension.")
            else:
                output_path += ".vcf"

        analyzer = VCFManager(directory, directory_mode=True)
        analyzer.combine_vcf(output_file=output_path)
        print(f"INFO: Combined files saved in '{output_path}'")

if __name__ == "__main__":
    main()