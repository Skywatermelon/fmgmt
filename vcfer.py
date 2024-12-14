import vobject
import os
import sys
import getopt
from collections import defaultdict

class VCFAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.contacts = []
        self.tally = defaultdict(int)
        self.total_contacts = 0

        if os.path.exists(file_path):
            self.load_vcf()
        else:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(2)

    def load_vcf(self):
        try:
            with open(self.file_path, 'r') as file:
                vcf_data = file.read()
            self.contacts = list(vobject.readComponents(vcf_data))
            self.total_contacts = len(self.contacts)
            print(f"Loaded {self.total_contacts} contacts.")
        except Exception as e:
            print(f"Error loading VCF file: {e}")
            sys.exit(2)

    def create_contact(self, fn, tel=None, email=None):
        new_contact = vobject.vCard()
        new_contact.add('fn').value = fn
        if tel:
            new_contact.add('tel').value = tel
        if email:
            new_contact.add('email').value = email
        self.contacts.append(new_contact)
        self.total_contacts += 1
        self.export_vcf(self.file_path)
        print(f"Contact '{fn}' created and added to {self.file_path}.")

    def export_vcf(self, output_file):
        try:
            with open(output_file, 'w') as file:
                for contact in self.contacts:
                    file.write(contact.serialize())
            print(f"VCF file updated: {output_file}.")
        except Exception as e:
            print(f"Error exporting VCF file: {e}")

    def split_vcf(self, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for contact in self.contacts:
            first_name = contact.n.value.given if hasattr(contact, 'n') else "Unknown"
            last_name = contact.n.value.family if hasattr(contact, 'n') else "Unknown"
            full_name = f"{first_name}_{last_name}".replace(" ", "_")
            contact_file = os.path.join(output_folder, f"{full_name}.vcf")
            
            try:
                with open(contact_file, 'w') as file:
                    file.write(contact.serialize())
                print(f"Exported {full_name}.vcf")
            except Exception as e:
                print(f"Error exporting {full_name}.vcf: {e}")
    def merge_vcf(directory, output_file):
        if not os.path.isdir(directory):
            print(f"Error: '{directory}' is not a valid directory.")
            return

        merged_contacts = []
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith('.vcf'):
                try:
                    with open(file_path, 'r') as file:
                        vcf_data = file.read()
                        contacts = list(vobject.readComponents(vcf_data))
                        merged_contacts.extend(contacts)
                        print(f"Merged: {file_name}")
                except Exception as e:
                    print(f"Error reading {file_name}: {e}")

        try:
            with open(output_file, 'w') as file:
                for contact in merged_contacts:
                    file.write(contact.serialize())
            print(f"VCF merge completed. Output saved to {output_file}.")
        except Exception as e:
            print(f"Error writing to {output_file}: {e}")
    def tally_contents(self):
        self.tally.clear()

        for contact in self.contacts:
            if hasattr(contact, 'fn'):
                self.tally['Contacts with Full Name (FN)'] += 1
            if hasattr(contact, 'n'):
                self.tally['Contacts with Display Name (N)'] += 1
            if hasattr(contact, 'tel_list') and len(contact.tel_list) > 1:
                self.tally['Contacts with Multiple Numbers'] += 1
            if hasattr(contact, 'email_list') and len(contact.email_list) > 1:
                self.tally['Contacts with Multiple Emails'] += 1
            if hasattr(contact, 'bday'):
                self.tally['Contacts with Birthdays'] += 1
            if hasattr(contact, 'member_list'):
                self.tally['Contacts with Memberships'] += len(contact.member_list)

    def generate_report(self):
        if not self.tally:
            print("No data to report. Run `tally_contents()` first.")
            return

        print("\nVCF File Analysis Report:")
        print("=" * 50)
        print(f"Total Contacts: {self.total_contacts}")
        print("=" * 50)

        for key, count in sorted(self.tally.items()):
            percentage = (count / self.total_contacts) * 100
            print(f"{key}: {count} ({percentage:.2f}%)")
        print("=" * 50)


def print_help():
    help_text = """
Usage: vcf_analyzer.py [OPTIONS]

Options:
  -c, --create FILE,FN[,TEL,EMAIL]  Create a new contact and add it to the specified VCF file.
  -r, --report FILE                 Generate a contact report from the specified VCF file.
  -m, --memberships FILE            Display membership groups from the specified VCF file.
  -s, --split FILE                  Split the specified VCF file into individual files.
  -h, --help                        Display this help text.

Examples:
  python vcf_analyzer.py -c "contacts.vcf,John Doe,+123456789,john@example.com"
  python vcf_analyzer.py -r contacts.vcf
  python vcf_analyzer.py -m contacts.vcf
  python vcf_analyzer.py -s contacts.vcf
    """
    print(help_text)


def main():
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], "c:r:m:s:h", ["create=", "report=", "memberships=", "split=", "help"]
        )
    except getopt.GetoptError as err:
        print(err)
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-c", "--create"):
            details = arg.split(",")
            if len(details) < 2:
                print("Error: FILE and FN (Full Name) are required.")
                sys.exit(2)
            file_path, fn = details[0], details[1]
            tel = details[2] if len(details) > 2 else None
            email = details[3] if len(details) > 3 else None
            analyzer = VCFAnalyzer(file_path)
            analyzer.create_contact(fn, tel, email)
        elif opt in ("-r", "--report"):
            analyzer = VCFAnalyzer(arg)
            analyzer.tally_contents()
            analyzer.generate_report()
        elif opt in ("-s", "--split"):
            analyzer = VCFAnalyzer(arg)
            output_folder = os.path.splitext(arg)[0]
            analyzer.split_vcf(output_folder)
        elif opt in ("-h", "--help"):
            print_help()
            sys.exit()

if __name__ == "__main__":
    main()