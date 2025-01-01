import os
import sys
import vobject
from collections import defaultdict

class VCFManager:
    """
    A class to manage VCF (vCard) files. Supports loading, splitting, combining,
    creating contacts, exporting, and generating reports.
    """

    def __init__(self, file_path, directory_mode=False):
        """
        Initializes the VCFManager with the provided file path. Supports both
        file and directory operations via the `directory_mode` flag.

        Args:
            file_path (str): Path to the VCF file or directory.
            directory_mode (bool): Whether the manager is operating in directory mode.
        """
        self.file_path = file_path  # Path to the file or directory.
        self.directory_mode = directory_mode  # Flag to toggle between file and directory modes.
        self.contacts = []  # List to store individual contact objects.
        self.tally = defaultdict(int)  # Dictionary to keep track of contact statistics.
        self.total_contacts = 0  # Counter for the total number of contacts.

        if os.path.exists(file_path):
            self.load_vcf()
        else:
            print(f"ERROR: File or directory '{file_path}' not found.")
            sys.exit(2)

    def load_vcf(self):
        """
        Loads and parses the VCF file(s), storing contacts in the `contacts` list.
        If in directory mode, loads all `.vcf` files in the directory.
        """
        if self.directory_mode:
            # Directory mode
            if not os.path.isdir(self.file_path):
                print(f"ERROR: Path '{self.file_path}' is not a directory.")
                sys.exit(2)
            
            # Gather only vcf files
            for file_name in os.listdir(self.file_path):
                file_path = os.path.join(self.file_path, file_name)
                if os.path.isfile(file_path) and file_name.lower().endswith('.vcf'):
                    try:
                        with open(file_path, 'r') as file:
                            vcf_data = file.read()
                            contacts = list(vobject.readComponents(vcf_data))
                            self.contacts.extend(contacts)
                            print(f"INFO: Loaded {len(contacts)} contacts from {file_name}.")
                    except Exception as e:
                        print(f"ERROR: Could not read VCF file {file_name}: {e}")
        else:
            # Single file mode
            try:
                with open(self.file_path, 'r') as file:
                    vcf_data = file.read()
                self.contacts = list(vobject.readComponents(vcf_data))
                self.total_contacts = len(self.contacts)
                print(f"INFO: Loaded {self.total_contacts} contacts from {self.file_path}.")
            except Exception as e:
                print(f"ERROR: Could not load VCF file: {e}")
                sys.exit(2)

    def split_vcf(self, output_path):
        """
        Splits the contacts in the VCF file into individual files, one for each contact.
        Files are saved in a folder named 'split' within the specified output path.
        """
        split_folder = os.path.join(output_path, "split")
        os.makedirs(split_folder, exist_ok=True)

        unknown_contact_counter = 0

        for contact in self.contacts:
            if hasattr(contact, 'fn') and contact.fn.value.strip():
                file_name = contact.fn.value.replace(" ", "_")
            elif hasattr(contact, 'n') and (contact.n.value.given or contact.n.value.family):
                first_name = contact.n.value.given if contact.n.value.given else "Unknown"
                last_name = contact.n.value.family if contact.n.value.family else "Unknown"
                file_name = f"{first_name}_{last_name}".replace(" ", "_")
            else:
                file_name = f"unknown_contact_{unknown_contact_counter:04d}"
                unknown_contact_counter += 1

            if hasattr(contact, 'categories'):
                contact.categories.value = [cat.replace(" ", "_") for cat in contact.categories.value]

            contact_file = os.path.join(split_folder, f"{file_name}.vcf")

            try:
                with open(contact_file, 'w') as file:
                    file.write(contact.serialize())
            except Exception as e:
                print(f"ERROR: Could not export VCF file: {file_name}.vcf: {e}")

    def combine_vcf(self, output_file):
            """
            Combines the contents of the loaded VCF contacts into a single output VCF file.

            Args:
                output_file (str): Path for the output combined VCF file.
            """
            if not self.contacts:
                print("ERROR: No contacts loaded. Use load_vcf to load contacts first.")
                return

            try:
                with open(output_file, 'w') as file:
                    for contact in self.contacts:
                        if hasattr(contact, 'categories'):
                            # Normalize CATEGORIES field for compatibility
                            contact.categories.value = [cat.replace(" ", "_") for cat in contact.categories.value]
                        file.write(contact.serialize())
                print(f"INFO: Combined VCF file saved to {output_file}.")
            except Exception as e:
                print(f"ERROR: Could not write to {output_file}: {e}")

    def tally_contents(self):
        """
        Generates a tally of various contact attributes.
        """
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
            if hasattr(contact, 'categories'):
                self.tally['Contacts with Categories'] += 1

    def assign_group(self, contacts, group_name):
        """
        Assigns a group name to the provided list of contact objects.
        """
        for contact in contacts:
            if not hasattr(contact, 'categories'):
                contact.add('categories').value = []

            if group_name not in contact.categories.value:
                contact.categories.value.append(group_name)

    def generate_report(self):
        """
        Prints a summary report of the tally data.
        """
        if not self.tally:
            print("ERROR: No data to report.")
            return

        print("\nVCF File Analysis Report:")
        print("=" * 50)
        print(f"Total Contacts: {self.total_contacts}")
        print("=" * 50)

        for key, count in sorted(self.tally.items()):
            percentage = (count / self.total_contacts) * 100
            print(f"{key}: {count} ({percentage:.2f}%)")
        print("=" * 50)

    def create_contact(self, fn, tel=None, email=None):
        """
        Creates a new contact with the specified details and adds it to the contacts list.
        """
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
        """
        Exports the current contacts list to a specified VCF file.
        """
        try:
            with open(output_file, 'w') as file:
                for contact in self.contacts:
                    file.write(contact.serialize())
            print(f"VCF file updated: {output_file}.")
        except Exception as e:
            print(f"ERROR: Could not export VCF file: {e}")