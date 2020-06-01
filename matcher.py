#! /usr/bin/env python3

from dataclasses import dataclass
from typing import *

Event = str

class Asset:
    pass

@dataclass(frozen=True)
class DisjunctionAsset(Asset):
    terms: FrozenSet[Event]

@dataclass(frozen=True)
class NegationAsset(Asset):
    event: Event

@dataclass(frozen=True)
class Order:
    asset: Asset
    bid: float
    # Quantity is always 1

def max_negations_by_event(negations: Iterable[Order]):
    book = {} # Event -> Order
    for order in negations:
        book[order.asset.event] = max(
            book.setdefault(order.asset.event, Order(order.asset, 0)),
            order,
            key=lambda o: o.bid,
        )
    return book

def find_match(events: Set[Event], orders: Set[Order]) -> Optional[Set[Order]]:
    disjunctions = filter(lambda o: isinstance(o.asset, DisjunctionAsset), orders)
    negations = filter(lambda o: isinstance(o.asset, NegationAsset), orders)
    maxneg = max_negations_by_event(negations)

    for disjunction in disjunctions:
        sum_q_i = 0
        q_orders = []

        for negation_event in disjunction.asset.terms:
            if negation_event not in maxneg:
                continue

            q_orders.append(maxneg[negation_event])
            sum_q_i += maxneg[negation_event].bid
            if sum_q_i > len(events):
                return set([disjunction] + q_orders)
    
    return None

A='A'
B='B'
EVENTS={A,B}

print(find_match(EVENTS, {
    Order(DisjunctionAsset(frozenset({A,B})), .5),
    Order(NegationAsset(A), .05),
    Order(NegationAsset(A), .2),
    Order(NegationAsset(B), .4),
}))
assert find_match(EVENTS, {
    Order(DisjunctionAsset(frozenset({A,B})), .5),
    Order(NegationAsset(A), .05),
    Order(NegationAsset(A), .2),
    Order(NegationAsset(B), .4),
}) == {
    Order(NegationAsset(A), .2),
    Order(NegationAsset(B), .4),
    Order(DisjunctionAsset(frozenset({A,B})), .5),
}