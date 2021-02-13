from .paginator import Paginator


def test_paginator():

    items = range(1, 491)
    p = Paginator(items, page=1, per_page=20)

    assert p.page == 1
    assert not p.has_prev
    assert p.has_next
    assert p.total_items == 490
    assert p.total_pages == 25
    assert p.next_page_number == 2
    assert list(p.pages) == [1, 2, 3, 4, None, 24, 25]
    assert p.pages_range == (0, 19)

    p.page = 10
    assert p.page == 10
    assert p.has_prev
    assert list(p.pages) == [1, 2, None, 7, 8, 9, 10, 11, 12, 13, None, 24, 25]
    assert list(p) == list(range(181, 201))

    assert Paginator(range(5))
