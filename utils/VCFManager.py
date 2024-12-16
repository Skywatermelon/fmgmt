import os
import sys
import vobject
from collections import defaultdict

class VCFManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.contacts = []
        self.tally = defaultdict(int)
        self.total_contacts = 0

        if os.path.exists(file_path):
            self.load_vcf()
        else:
            print(f"ERROR: File '{file_path}' not found.")
            sys.exit(2)

    def load_vcf(self):
        try:
            with open(self.file_path, 'r') as file:
                vcf_data = file.read()
            self.contacts = list(vobject.readComponents(vcf_data))
            self.total_contacts = len(self.contacts)
            print(f"INFO: Loaded {self.total_contacts} contacts.")
        except Exception as e:
            print(f"ERROR: Could not load VCF file: {e}")
            sys.exit(2)

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
            print(f"ERROR: Could not export VCF file: {e}")

    def split_vcf(self, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        unknown_contact_counter = 1

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

            # Remove unsupported fields
            if hasattr(contact, 'categories'):
                del contact.categories

            contact_file = os.path.join(output_folder, f"{file_name}.vcf")

            try:
                with open(contact_file, 'w') as file:
                    file.write(contact.serialize())
            except Exception as e:
                print(f"ERROR: Could not export VCF file: {file_name}.vcf: {e}")

    def combine_vcf(directory, output_file):
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
            print(f"ERROR:  writing to {output_file}: {e}")

    def generate_report(self):
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
