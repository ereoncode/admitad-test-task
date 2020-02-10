from collections import UserDict
from datetime import datetime
from typing import TypedDict, Tuple, List, Dict, Optional

LogRecord = TypedDict('LogRecord', {
    'client_id': str,
    'User-Agent': str,
    'document.location': str,
    'document.referer': str,
    'date': str
})


class TransitionGraphNode(UserDict):
    client_id: str
    user_agent: str
    url: str

    def __hash__(self):
        return hash(frozenset(self))

    def __str__(self):
        return self['url']


Checkout = TypedDict('Checkout', {
    'date': datetime,
    'product_node': TransitionGraphNode,
    'checkout_node': TransitionGraphNode
})

Referer = TypedDict('Referer', {
    'redirected_at': datetime,
    'referer_node': TransitionGraphNode
})

UniqueClient = Tuple[str, str]

CompletedOrder = TypedDict('CompletedOrder', {
    'client_id': str,
    'product_page': str,
    'completed_at': datetime,
    'cashback_referer_service': str
})

UserActivityLogs = Dict[UniqueClient, List[LogRecord]]
