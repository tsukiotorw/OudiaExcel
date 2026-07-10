from parser.parser import OudiaParser
from excel.writer import ExcelWriter


def main():

    parser = OudiaParser()

    data = parser.parse("data/sample.oud2")

    writer = ExcelWriter()

    writer.write(data, "output/sample.xlsx")


if __name__ == "__main__":
    main()
    