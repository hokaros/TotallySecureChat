import os


class FileWriter:
    def __init__(self, directory):
        self.directory = directory
        self.file_name = None
        try:
            os.mkdir(directory)
        except OSError as error:
            print(error)

    def create_file(self, file_name):
        print("create file")
        self.file_name = file_name
        open(os.path.join(self.directory, self.file_name), "x")

    def write(self, content):
        with open(os.path.join(self.directory, self.file_name)) as file:
            file.write(content)
