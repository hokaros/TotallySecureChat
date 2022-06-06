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
        path = os.path.join(self.directory, self.file_name)
        if os.path.exists(path):
            print(f"File {self.file_name} already exists")
            os.remove(path)

        open(path, "x")

    def write(self, content):
        with open(os.path.join(self.directory, self.file_name), "ab") as file:
            file.write(content)


class UserDirectory:
    main = None

    def __init__(self, user_id: int):
        self.__directory = os.path.join("users", str(user_id))
        if not os.path.exists(self.__directory):
            os.makedirs(self.__directory)

        if self.main is None:
            self.main = self

    @property
    def directory(self) -> str:
        return self.__directory
