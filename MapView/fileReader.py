from csv import reader
import config


class FileReader:
    def __init__(
        self, data_filename: str,
    ) -> None:
        self.file_path = data_filename
        pass

    def read(self):
        return [1, 2, 3]

    def startReading(self, *args, **kwargs):
        self.file = open(self.file_path, newline='')
        self.file_reader = reader(self.acc_file)
        file_header = next(self.file_reader)

    def stopReading(self, *args, **kwargs):
        pass

