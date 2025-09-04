#

from ._chinese import ChineseHouse

def main(*args):

    house = ChineseHouse(ChineseHouse.play())
    composition = house.composition
    print(composition)



if __name__ == "__main__":
    from sys import argv

    exit(main(argv[1:]))
