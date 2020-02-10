from datetime import datetime
from itertools import groupby
from operator import itemgetter
from typing import List, Generator

import networkx as nx

import settings
from etl.types import (
    LogRecord,
    UniqueClient,
    UserActivityLogs,
    CompletedOrder,
    TransitionGraphNode,
    Checkout,
    Referer
)
from etl.utils import is_products_page, is_checkout_page, is_partner_link, is_ours_service


def unique_client_key(log: LogRecord) -> UniqueClient:
    """Unique client's key that combines both `client_id` and `User-Agent`"""
    return log['client_id'], log['User-Agent']


def group_logs_by_client(logs: List[LogRecord]) -> UserActivityLogs:
    """Grouping logs by `unique_client_key`"""
    logs.sort(key=lambda l: (unique_client_key(l)))

    grouped_logs: UserActivityLogs = {}
    for unique_client, transitions in groupby(logs, unique_client_key):
        client_id, user_agent = unique_client

        logs: List[LogRecord] = list(transitions)
        logs.sort(key=lambda l: datetime.strptime(l['date'], settings.DATETIME_FMT))
        grouped_logs[(client_id, user_agent)] = logs

    return grouped_logs


def get_completed_orders(users_activity: UserActivityLogs) -> Generator[CompletedOrder, None, None]:
    """Returns all completed orders made after redirect from Ours cashback service.

    Algorithm:
        1) Building directed graph of user's redirects on the Shop site.
        2) For each `TransitionGraphNode` with url `https://shop.com/checkout`
            find all possible paths from referers [Ours, Their1, Their2] to checkout page.
        3) Decide the winner (last redirect from cashback service will take the commission)
    """
    for unique_client, activity_logs in users_activity.items():
        client_id, _ = unique_client

        dg = nx.DiGraph()

        referers: List[Referer] = []
        checkouts: List[Checkout] = []

        for log_record in activity_logs:
            referer: TransitionGraphNode = TransitionGraphNode(
                client_id=log_record['client_id'],
                user_agent=log_record['User-Agent'],
                url=log_record['document.referer'],
            )

            if is_partner_link(referer['url']):
                referers.append(
                    Referer(
                        redirected_at=datetime.strptime(log_record['date'], settings.DATETIME_FMT),
                        referer_node=referer
                    )
                )

            location: TransitionGraphNode = TransitionGraphNode(
                client_id=log_record['client_id'],
                user_agent=log_record['User-Agent'],
                url=log_record['document.location'],
            )

            dg.add_node(referer)

            if is_checkout_page(location['url']):
                cart = referer
                neighbours = list(nx.all_neighbors(dg, cart))

                if neighbours:
                    product = neighbours[0]  # nearest neighbour must be a product page

                    if is_products_page(product['url']):
                        checkout = Checkout(
                            completed_at=datetime.strptime(log_record['date'], settings.DATETIME_FMT),
                            product_node=product,
                            checkout_node=location
                        )
                        checkouts.append(checkout)

            dg.add_node(location)
            dg.add_edge(referer, location)

        for checkout in checkouts:
            checkout_node = checkout['checkout_node']
            beneficial_referers = [
                referer for referer in referers
                if nx.has_path(dg, referer['referer_node'], checkout_node)
            ]

            if beneficial_referers:
                beneficial_referers.sort(key=itemgetter('redirected_at'), reverse=True)

                winner: TransitionGraphNode = beneficial_referers[0]['referer_node']

                if is_ours_service(winner['url']):
                    yield CompletedOrder(
                        client_id=winner['client_id'],
                        product_page=checkout['product_node']['url'],
                        completed_at=checkout['completed_at'],
                        cashback_referer_service=winner['url']
                    )
