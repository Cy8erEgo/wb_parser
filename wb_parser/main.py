from pprint import pprint

from cli import parse_args
from parser import WBParser


def main():
    # parse command line arguments
    args = parse_args()

    # parse information about products and categories
    parser = WBParser(args.url)
    products_collection = parser.parse_products(exclude_desc=args.brief)
    categories_collection = parser.parse_categories()

    # display it
    print("~~~ Products ~~~")
    pprint(products_collection)
    print("\n~~~ Categories ~~~")
    pprint(categories_collection)


if __name__ == "__main__":
    main()
