import os
import sys

class FileHandler:
    def __init__(self):
        self.input_files = [] 
        self.output_file = None
        self.input_is_directory = None
        self.output_is_directory = False
        self.input_file_extension = None
        self.output_file_extension = None
        self.input_file_types = set()
        self.output_file_types = set()

    def set_inputs(self, input_paths):
        """
        Sets the input paths, validating that all are of the same type (directories or files).
        If files, ensures they all share the same extension.
        
        Args:
            input_paths (str): Comma-separated list of input paths.

        Raises:
            SystemExit: If input paths are not all directories or all files of the same type.
        """
        paths = input_paths.split(",")
        if not paths:
            sys.exit("ERROR: No input paths provided.")

        # Determine the type of the first path
        first_path = paths[0]
        if not os.path.exists(first_path):
            sys.exit(f"ERROR: Input path '{first_path}' does not exist.")
        
        first_is_directory = os.path.isdir(first_path)
        self.input_is_directory = first_is_directory
        self.input_file_extension = None if first_is_directory else os.path.splitext(first_path)[1].lower()

        for path in paths:
            if not os.path.exists(path):
                sys.exit(f"ERROR: Input path '{path}' does not exist.")

            is_directory = os.path.isdir(path)
            if is_directory != self.input_is_directory:
                sys.exit("ERROR: Input paths must be all directories or all files.")

            if not is_directory:  # If files, ensure extensions match
                extension = os.path.splitext(path)[1].lower()
                if extension != self.input_file_extension:
                    sys.exit("ERROR: Input files must all have the same extension.")

            self.input_files.append(path)

        # Gather file types if inputs are directories
        if self.input_is_directory:
            for path in self.input_files:
                self.input_file_types.update(self.gather_file_types(path))

    def set_output(self, output_path):
        """
        Sets the output path and identifies if it's a file or directory.
        If it's a directory, scans for unique file types.
        """
        if os.path.exists(output_path):
            self.output_file = output_path
            self.output_is_directory = os.path.isdir(output_path)
            if not self.output_is_directory:
                self.output_file_extension = os.path.splitext(output_path)[1].lower()
            else:
                self.output_file_types = self.gather_file_types(output_path)
        else:
            if self.input_is_directory:
                os.makedirs(output_path, exist_ok=True)
                self.output_file = output_path
                self.output_is_directory = True
                self.output_file_types = self.gather_file_types(output_path)
            else:
                self.output_file = output_path
                self.output_is_directory = False
                self.output_file_extension = os.path.splitext(output_path)[1].lower()
                open(output_path, 'w').close()

    def gather_file_types(self, path):
        """
        Recursively scans a directory to gather a list of unique file types.
        Handles permission errors gracefully.

        Args:
            path (str): Directory to scan for file types.

        Returns:
            set: A set of unique file extensions found in the directory.
        """
        if not os.path.isdir(path):
            sys.exit(f"ERROR: The path '{path}' is not a directory.")

        file_types = set()

        try:
            for root, _, files in os.walk(path):
                for file in files:
                    _, extension = os.path.splitext(file)
                    if extension:
                        file_types.add(extension.lower())
        except PermissionError:
            print(f"WARNING: Permission denied while scanning '{path}'. Skipping inaccessible files.")

        return file_types

    def has_file_type(self, file_type, is_input=True):
        """
        Checks if a specific file type exists in either the input or output directories.

        Args:
            file_type (str): The file extension to check (e.g., '.txt').
            is_input (bool): If True, checks the input directories. Otherwise, checks the output directory.

        Returns:
            bool: True if the file type is found, False otherwise.
        """
        file_type = file_type.lower()
        if is_input:
            return file_type in self.input_file_types
        else:
            return file_type in self.output_file_types

    def count_input_files(self):
        """
        Returns the number of input files or directories set.
        """
        return len(self.input_files)