import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL of WB product page")
    parser.add_argument("-b", "--brief", action="store_true", default=False, help="Not to parse product descriptions")
    args = parser.parse_args()

    return args
