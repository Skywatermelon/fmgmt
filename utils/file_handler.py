import os
import sys

class FileHandler:
    def __init__(self):
        self.input_file = None
        self.output_file = None
        self.input_is_directory = False
        self.output_is_directory = False
        self.input_file_extension = None
        self.output_file_extension = None

    def set_input(self, input_path):
        if os.path.exists(input_path):
            self.input_file = input_path
            self.input_is_directory = os.path.isdir(input_path)
            if not self.input_is_directory:
                self.input_file_extension = os.path.splitext(input_path)[1].lower()
        else:
            sys.exit(f"ERROR: Input file or directory '{input_path}' does not exist.")

    def set_output(self, output_path):
        if os.path.exists(output_path):
            self.output_file = output_path
            self.output_is_directory = os.path.isdir(output_path)
            if not self.output_is_directory:
                self.output_file_extension = os.path.splitext(output_path)[1].lower()
        else:
            if self.input_is_directory:
                os.makedirs(output_path, exist_ok=True)
                self.output_file = output_path
                self.output_is_directory = True
            else:
                self.output_file = output_path
                self.output_is_directory = False
                self.output_file_extension = os.path.splitext(output_path)[1].lower()
                open(output_path, 'w').close()