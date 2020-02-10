import json
import unittest
from datetime import datetime, timedelta
from random import randint, choice, randrange
from typing import List, Optional, Union, Dict
from random import shuffle

from mimesis import Internet, Person

from etl.utils import is_ours_service
from settings import (
    DATETIME_FMT,
    LOG_FILE,
    PRODUCTS_PAGE,
    TARGET_REFERER,
    PARTNER_LINKS)
from etl.types import LogRecord, CompletedOrder
from main import get_all_beneficial_orders

internet = Internet()
person = Person()


class UserBehaviour:
    """User behavior model"""

    def __init__(self, client_id: str, user_agent: str):
        self.client_id = client_id
        self.user_agent = user_agent

        self.access_logs: List[LogRecord] = []
        self.last_page: Optional[str] = None

    def open(self, browser_or_partner_site: str, date: Optional[datetime] = None):
        """User open browser or partner site
        :param browser_or_partner_site: Browser, https://referal.ours.com, https://ad.theirs1.com
        or https://ad.theirs2.com
        :param date: event date
        """
        self.last_page = browser_or_partner_site

        return self

    def click(self, link: str, date: Optional[Union[str, datetime]] = None):
        """User click on the link
        :param link: Link on the Shop site
        :param date: event date
        """
        date = date or datetime.utcnow()

        self.access_logs.append(LogRecord(**{
            'client_id': self.client_id,
            'User-Agent': self.user_agent,
            'document.location': link,
            'document.referer': self.last_page,
            'date': date.strftime(DATETIME_FMT) if isinstance(date, datetime) else date
        }))

        self.last_page = link

        return self


class TestUserActivityCase(unittest.TestCase):
    """Testing user behavior scenarios"""

    def tearDown(self) -> None:
        if LOG_FILE.exists():
            LOG_FILE.unlink()

    @staticmethod
    def save_access_logs(logs: List[LogRecord]):
        """Save access logs to settings.LOG_FILE for further analysis"""
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=4)

    def test_get_completed_orders(self):
        """Testing getting a list of completed orders made after redirect from Ours cashback service"""
        user = UserBehaviour(
            client_id="user7",
            user_agent="Chrome 65"
        )

        our_service = TARGET_REFERER

        user.open(our_service) \
            .click(link="https://shop.com/", date="2018-05-23T18:59:13.286000Z") \
            .click(link="https://shop.com/products/?id=10", date="2018-05-23T18:59:20.119000Z") \
            .click(link="https://shop.com/products/?id=25", date="2018-05-23T19:04:20.119000Z") \
            .click(link="https://shop.com/cart", date="2018-05-23T19:05:13.123000Z") \
            .click(link="https://shop.com/checkout", date="2018-05-23T19:05:59.224000Z")

        self.save_access_logs(user.access_logs)

        completed_orders: List[CompletedOrder] = list(get_all_beneficial_orders())
        cashback_services: List[str] = [o['cashback_referer_service'] for o in completed_orders]

        assert our_service in cashback_services

    def test_redirect_from_cashback_services_without_purchasing(self):
        """Testing redirects from different services without purchasing"""
        user = UserBehaviour(
            client_id="user7",
            user_agent=internet.user_agent()
        )

        shuffle(PARTNER_LINKS)

        for cashback_service in PARTNER_LINKS:
            user.open(cashback_service) \
                .click(link="https://shop.com/products/?id=10", date="2018-05-23T18:59:20.119000Z") \
                .click(link="https://shop.com/products/?id=25", date="2018-05-23T19:04:20.119000Z")

        self.save_access_logs(user.access_logs)

        completed_orders: List[CompletedOrder] = list(get_all_beneficial_orders())
        assert not completed_orders

    def test_redirect_from_several_cashback_services_with_purchasing(self):
        """Testing redirects from several services with purchasing"""
        user = UserBehaviour(
            client_id="user7",
            user_agent=internet.user_agent()
        )

        shuffle(PARTNER_LINKS)
        last_service: Optional[str] = PARTNER_LINKS[-1]

        # Check available offers from cashback services
        for cashback_service in PARTNER_LINKS:
            user.open(cashback_service) \
                .click(link="https://shop.com/products/?id=10") \
                .click(link="https://shop.com/products/?id=25")

        # Finally user make a purchase
        user.click(link="https://shop.com/cart") \
            .click(link="https://shop.com/checkout")

        self.save_access_logs(user.access_logs)

        completed_orders: List[CompletedOrder] = list(get_all_beneficial_orders())
        cashback_services: List[str] = [o['cashback_referer_service'] for o in completed_orders]

        if is_ours_service(last_service):
            assert last_service in cashback_services

    def test_redirect_from_browser(self):
        """Testing redirects from browser with purchasing"""
        user = UserBehaviour(
            client_id="user7",
            user_agent=internet.user_agent()
        )

        user.open("https://yandex.ru/search/?q=купить+котика") \
            .click(link="https://shop.com/products/?id=10") \
            .click(link="https://shop.com/cart") \
            .click(link="https://shop.com/checkout")

        self.save_access_logs(user.access_logs)

        completed_orders: List[CompletedOrder] = list(get_all_beneficial_orders())

        assert not completed_orders

    def test_get_all_beneficial_orders_from_several_users(self):
        """Testing getting all beneficial orders made by several users
        Each user came to the Shop site from different referer: browser, Ours service etc.
        with a 50% probability of making a purchase
        """
        users = [
            UserBehaviour(client_id=person.username(), user_agent=internet.user_agent())
            for _ in range(10)
        ]
        coin_flip = lambda: choice([0, 1])

        referers: List[str] = PARTNER_LINKS + ["https://yandex.ru/search/?q=купить+котика"]
        access_logs: List[LogRecord] = []
        expected_orders: List[CompletedOrder] = []

        for user in users:
            referer = choice(referers)
            available_products = range(randint(1, 10), randint(10, 100))
            user.open(referer) \
                .click(link="https://shop.com/")

            for product_id in available_products:  # user is looking for the particular product
                user.click(link=f"https://shop.com/products/?id={product_id}")

            if coin_flip():  # make a purchase or not
                product_page = user.last_page
                completed_at = datetime.utcnow() + timedelta(minutes=2)

                user.click(link="https://shop.com/cart") \
                    .click(link="https://shop.com/checkout", date=completed_at)

                expected_orders.append(CompletedOrder(
                    client_id=user.client_id,
                    product_page=product_page,
                    completed_at=completed_at,
                    cashback_referer_service=referer
                ))

            access_logs += user.access_logs

        self.save_access_logs(access_logs)

        completed_orders: List[CompletedOrder] = list(get_all_beneficial_orders())
        our_orders: List[CompletedOrder] = [
            o for o in expected_orders
            if is_ours_service(o['cashback_referer_service'])
        ]

        our_orders.sort(key=lambda o: sorted(o.items()))
        completed_orders.sort(key=lambda o: sorted(o.items()))

        assert our_orders == completed_orders


if __name__ == '__main__':
    unittest.main()
