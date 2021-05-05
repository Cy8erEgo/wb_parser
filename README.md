# wb_parser
A simple wildberries.ru parser that takes product page URLs and returns general product information and a list of categories.

## Installation
Required Python version >= 3.7.5
```
poetry install  # install dependencies
poetry shell    # activate the virtual environment
```

## Usage 
```
usage: main.py [-h] [-b] url

positional arguments:
  url          URL of WB product page

optional arguments:
  -h, --help   show this help message and exit
  -b, --brief  Not to parse product descriptions
```
**Example:**
```bash
python main.py https://www.wildberries.ru/catalog/elektronika/kosmeticheskie-apparaty
```
