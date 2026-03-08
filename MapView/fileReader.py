from csv import reader
import config
from domain.accelerometer import Accelerometer



class FileReader:
    def __init__(
        self, data_filename: str,
    ) -> None:
        self.file_path = data_filename
        pass

    def read(self):
        return self.getNextValue()

    def startReading(self, *args, **kwargs):
        self.file = open(self.file_path, newline='')
        self.file_reader = reader(self.file, skipinitialspace=True)
        file_header = next(self.file_reader)
        
        self.x_idx = file_header.index('X')
        self.y_idx = file_header.index('Y')
        self.z_idx = file_header.index('Z')

    def getNextValue(self):
        while True:
            row = next(self.file_reader, None)
            if row is None:
                self._rewind_file()
                continue
            try:
                x = int(row[self.x_idx])
                y = int(row[self.y_idx])
                z = int(row[self.z_idx])
                return Accelerometer(x=x, y=y, z=z)
            except Exception as e:
                continue
        
    def _rewind_file(self):
        self.file.seek(0)
        self.file_reader = reader(self.file)
        next(self.file_reader)
        
    def stopReading(self, *args, **kwargs):
        if self.file:
            self.file.close()
        self.file_reader = None
        

