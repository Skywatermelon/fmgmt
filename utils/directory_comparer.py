import os
import hashlib
import shutil

class DirectoryComparer:
    def __init__(self, dir1, dir2, output_dir="./"):
        """
        Initializes the DirectoryComparer with two directories and an output directory.
        Creates subdirectories for uncommon and common files within the output directory.
        """
        self.dir1 = dir1
        self.dir2 = dir2
        self.output_dir = output_dir
        self.uncommon_dir = os.path.join(output_dir, "uncommon")
        self.common_dir = os.path.join(output_dir, "common")
        os.makedirs(self.uncommon_dir, exist_ok=True)
        os.makedirs(self.common_dir, exist_ok=True)

    def hash_file(self, file_path):
        """
        Computes the SHA-256 hash of the given file.
        """
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def compare(self):
        """
        Compares the files in the two directories.
        Identifies uncommon files and common files.
        """
        files1 = set(os.listdir(self.dir1))
        files2 = set(os.listdir(self.dir2))

        common_files = files1 & files2
        uncommon_files = (files1 - files2) | (files2 - files1)

        self.handle_uncommon(uncommon_files)
        self.handle_common(common_files)

    def handle_uncommon(self, uncommon_files):
        """
        Copies files that are present in one directory but not the other to the 'uncommon' directory.
        """
        for file_name in uncommon_files:
            src_dir = self.dir1 if file_name in os.listdir(self.dir1) else self.dir2
            src_file = os.path.join(src_dir, file_name)
            shutil.copy2(src_file, self.uncommon_dir)

    def get_file_modified_time(self, file_path):
        """
        Retrieves the last modified time of the given file.
        """
        return os.path.getmtime(file_path)

    def handle_common(self, common_files):
        """
        Handles common files by identifying differences in content and copying the most recent version
        of each common file to the 'common' directory.
        """
        for file_name in common_files:
            file1 = os.path.join(self.dir1, file_name)
            file2 = os.path.join(self.dir2, file_name)

            hash1 = self.hash_file(file1)
            hash2 = self.hash_file(file2)

            # Copy the most recently modified version of the file if hashes differ
            if hash1 != hash2:
                if self.get_file_modified_time(file1) >= self.get_file_modified_time(file2):
                    latest_file = file1
                else:
                    latest_file = file2
                
                target_path = os.path.join(self.common_dir, file_name)
                shutil.copy2(latest_file, target_path)
            else:
                # If the files are identical, copy either one (e.g., from dir1)
                target_path = os.path.join(self.common_dir, file_name)
                shutil.copy2(file1, target_path)