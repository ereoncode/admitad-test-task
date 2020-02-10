from typing import List, Generator

import settings
from etl.extract import extract_logs
from etl.transform import group_logs_by_client, get_completed_orders
from etl.types import LogRecord, CompletedOrder


def get_all_beneficial_orders() -> Generator[CompletedOrder, None, None]:
    """Returns list of completed orders made after redirect from Ours cashback service"""
    logs: List[LogRecord] = extract_logs()

    grouped_logs = group_logs_by_client(logs)

    yield from get_completed_orders(grouped_logs)


def main():
    """Search for customers who made a purchase after redirect from Ours cachback service"""
    message = (
        "Client {client_id} made a purchase after redirect from {cashback_referer_service} "
        "at {completed_at}. Product page {product_page}"
    )

    settings.LOG_FILE = 'default_shop_logs.json'

    for completed_order in get_all_beneficial_orders():
        print(message.format(**completed_order))


if __name__ == '__main__':
    main()
