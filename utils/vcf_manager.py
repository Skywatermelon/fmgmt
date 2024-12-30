import os
import sys
import vobject
from collections import defaultdict

class VCFManager:
    """
    A class to manage VCF (vCard) files. Supports loading, splitting, combining,
    creating contacts, exporting, and generating reports.
    """

    def __init__(self, file_path):
        """
        Initializes the VCFManager with the provided file path. Validates the file's existence.
        """
        self.file_path = file_path
        self.contacts = []  # List to store individual contact objects
        self.tally = defaultdict(int)  # Dictionary to keep track of contact statistics
        self.total_contacts = 0  # Counter for the total number of contacts

        if os.path.exists(file_path):
            self.load_vcf()
        else:
            print(f"ERROR: File '{file_path}' not found.")
            sys.exit(2)

    def load_vcf(self):
        """
        Loads and parses the VCF file, storing contacts in the `contacts` list.
        """
        try:
            with open(self.file_path, 'r') as file:
                vcf_data = file.read()
            self.contacts = list(vobject.readComponents(vcf_data))
            self.total_contacts = len(self.contacts)
            print(f"INFO: Loaded {self.total_contacts} contacts.")
        except Exception as e:
            print(f"ERROR: Could not load VCF file: {e}")
            sys.exit(2)

    def split_vcf(self, output_path):
        """
        Splits the contacts in the VCF file into individual files, one for each contact.
        Files are saved in a folder named 'split' within the specified output path.
        """
        # Create a 'split' directory within the output path
        split_folder = os.path.join(output_path, "split")
        os.makedirs(split_folder, exist_ok=True)

        unknown_contact_counter = 1

        for contact in self.contacts:
            # Determine the file name based on available contact details
            if hasattr(contact, 'fn') and contact.fn.value.strip():
                file_name = contact.fn.value.replace(" ", "_")
            elif hasattr(contact, 'n') and (contact.n.value.given or contact.n.value.family):
                first_name = contact.n.value.given if contact.n.value.given else "Unknown"
                last_name = contact.n.value.family if contact.n.value.family else "Unknown"
                file_name = f"{first_name}_{last_name}".replace(" ", "_")
            else:
                file_name = f"unknown_contact_{unknown_contact_counter:04d}"
                unknown_contact_counter += 1

            # Normalize CATEGORIES field to ensure compatibility
            if hasattr(contact, 'categories'):
                contact.categories.value = [cat.replace(" ", "_") for cat in contact.categories.value]

            # Generate the path for the contact file
            contact_file = os.path.join(split_folder, f"{file_name}.vcf")

            try:
                # Write the contact to a file
                with open(contact_file, 'w') as file:
                    file.write(contact.serialize())
            except Exception as e:
                print(f"ERROR: Could not export VCF file: {file_name}.vcf: {e}")
                
    def combine_vcf(self, directory, output_file):
        """
        Combines multiple VCF files from a specified directory into a single VCF file.
        """
        if not os.path.isdir(directory):
            print(f"ERROR: '{directory}' is not a valid directory.")
            return

        merged_contacts = []

        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith('.vcf'):
                try:
                    with open(file_path, 'r') as file:
                        vcf_data = file.read()
                        contacts = list(vobject.readComponents(vcf_data))
                        for contact in contacts:
                            # Normalize CATEGORIES field for compatibility
                            if hasattr(contact, 'categories'):
                                contact.categories.value = [cat.replace(" ", "_") for cat in contact.categories.value]
                        merged_contacts.extend(contacts)
                        print(f"INFO: Merged: {file_name}")
                except Exception as e:
                    print(f"ERROR: Could not read VCF file {file_name}: {e}")

        try:
            with open(output_file, 'w') as file:
                for contact in merged_contacts:
                    file.write(contact.serialize())
            print(f"INFO: VCF merge completed. Output saved to {output_file}.")
        except Exception as e:
            print(f"ERROR: Could not write to {output_file}: {e}")

    def tally_contents(self):
        """
        Generates a tally of various contact attributes, such as those with full names,
        multiple numbers, birthdays, etc.
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

    def generate_report(self):
        """
        Prints a summary report of the tally data, including percentages for each category.
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