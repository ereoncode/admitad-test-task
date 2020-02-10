import pathlib

BASE_DIR = pathlib.Path(__file__).parent

LOG_FILE = BASE_DIR.joinpath("shop.log")
DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"  # RFC 3339

PARTNER_LINKS = [
    "https://ad.theirs1.com",
    "https://ad.theirs2.com",
    "https://referal.ours.com",
]

TARGET_REFERER = "https://referal.ours.com"
SHOP_HOME_PAGE = "https://shop.com"
PRODUCTS_PAGE = "https://shop.com/products"
CART_PAGE = "https://shop.com/cart"
CHECKOUT_PAGE = "https://shop.com/checkout"

# Minimum required redirects count: referer -> products page -> cart page -> checkout page
MIN_REDIRECTS_COUNT = 4
