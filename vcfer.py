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
    input_path = None
    output_path = os.path.join(
        get_download_folder(),
        f"vcfer_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], "i:o:n:r:su:c:h",
            ["input=", "output=", "new=", "report=", "split", "uncommon=", "combine=", "help"]
        )
    except getopt.GetoptError as err:
        sys.exit(f"ERROR: {err}")

    flag_split_contacts = False
    uncommon_directories = None

    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input_path = arg
            print(f"INFO: Input file: {input_path}")
        elif opt in ("-o", "--output"):
            output_path = arg
            print(f"INFO: Output file: {output_path}")
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
            if not input_path:
                sys.exit("ERROR: Input path is required for reporting (-i).")
            analyzer = VCFManager(input_path)
            analyzer.tally_contents()
            analyzer.generate_report()
        elif opt in ("-s", "--split"):
            flag_split_contacts = True
            print(f"INFO: Split functionality triggered.")
        elif opt in ("-u", "--uncommon"):
            uncommon_directories = arg.split(",")
            if len(uncommon_directories) != 2:
                sys.exit("ERROR: Two directories are required for uncommon comparison (-u).")
        elif opt in ("-c", "--combine"):
            print(f"INFO: Combine functionality triggered.")
            if not input_path:
                sys.exit("ERROR: Input directory is required for combining (-i).")
        elif opt in ("-h", "--help"):
            print_help()
            sys.exit()

    # Validate input and output paths
    if not input_path:
        sys.exit("ERROR: Input path is required (-i).")
    if not os.path.exists(input_path):
        sys.exit(f"ERROR: Input path '{input_path}' does not exist.")
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)

    # Handle split functionality
    if flag_split_contacts:
        if not os.path.isfile(input_path):
            sys.exit("ERROR: Split requires a valid input VCF file (-i).")
        analyzer = VCFManager(input_path)
        analyzer.split_vcf(output_path)
        print(f"INFO: Split files saved in '{os.path.join(output_path, 'split')}'")

    # Handle uncommon comparison functionality
    if uncommon_directories:
        if not all(os.path.isdir(dir) for dir in uncommon_directories):
            sys.exit("ERROR: Both directories specified for uncommon comparison (-u) must exist.")
        dc = DirectoryComparer(
            dir1=uncommon_directories[0],
            dir2=uncommon_directories[1],
            output_dir=output_path
        )
        dc.compare()
        print(f"INFO: Uncommon files saved in '{os.path.join(output_path, 'uncommon')}'")

    # Handle combine functionality
    if input_path and os.path.isdir(input_path):
        analyzer = VCFManager(input_path)
        analyzer.combine_vcf(input_path, output_path)
        print(f"INFO: Combined files saved in '{output_path}'")

if __name__ == "__main__":
    main()