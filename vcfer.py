import os
import sys
import getopt
from datetime import datetime
from pathlib import Path

### Local Imports
from utils.selection_menu import SelectionMenu
from utils.file_handler import FileHandler
from utils.VCFManager import VCFManager



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
    file_handler = FileHandler()
    input_path = None
    output_path = os.path.join(
        get_download_folder(),
        f"vcfer_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )

    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], "i:o:n:r:s:c:h", 
            ["input=", "output=", "new=", "report=", "split=", "combine=", "help"]
        )
    except getopt.GetoptError as err:
        sys.exit(f"ERROR: {err}")

    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input_path = arg
            file_handler.set_input(input_path)
        elif opt in ("-o", "--output"):
            output_path = arg
            file_handler.set_output(output_path)
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
            analyzer = VCFManager(arg)
            analyzer.tally_contents()
            analyzer.generate_report()
        elif opt in ("-s", "--split"):
            split_filename = arg
            output_directory = os.path.join(output_path, os.path.splitext(split_filename)[0])
            analyzer = VCFManager(input_path)
            analyzer.split_vcf(output_directory)
        elif opt in ("-c", "--combine"):
            analyzer = VCFManager(input_path)
            analyzer.combine_vcf(input_path, output_path)
        elif opt in ("-h", "--help"):
            print_help()
            sys.exit()

    # if not file_handler.input_file or not file_handler.output_file:
    #     sys.exit("ERROR: Both input and output must be specified.")

if __name__ == "__main__":
    main()