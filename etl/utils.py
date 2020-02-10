import settings


def is_partner_link(url: str) -> bool:
    """Returns True if url is one of PARTNER_LINKS otherwise returns False"""
    return any([url.startswith(partner_link) for partner_link in settings.PARTNER_LINKS])


def is_internal_link(url: str) -> bool:
    """Returns True if url belongs to Shop otherwise False"""
    return url.startswith(settings.SHOP_HOME_PAGE)


def is_products_page(url: str) -> bool:
    """Returns True if url belongs to Shop's products page otherwise False"""
    return url.startswith(settings.PRODUCTS_PAGE)


def is_cart_page(url: str) -> bool:
    """Returns True if url belongs to Shop's cart page otherwise False"""
    return url.startswith(settings.CART_PAGE)


def is_checkout_page(url: str) -> bool:
    """Returns True if url belongs to Shop's checkout otherwise False"""
    return url.startswith(settings.CHECKOUT_PAGE)


def is_ours_service(url: str) -> bool:
    """Returns True if url belongs to Ours service otherwise False"""
    return url.startswith(settings.TARGET_REFERER)

