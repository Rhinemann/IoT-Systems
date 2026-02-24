from UARTReader import UARTReader
import os

PORT = os.environ.get("PORT", None) or "/dev/ttyUSB0"
FILE = os.environ.get("FILE", None) or "savefile.csv"

r = UARTReader(PORT)

with open(FILE, "w") as f:
    f.write("x,y,z\n")

    for i in range(500):
        v = r.read_next()
        f.write(",".join(tuple(map(str, v))) + "\n")

r.close()
