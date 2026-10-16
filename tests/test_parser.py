import pytest

from bot.parser import ParseError, parse_html, to_float


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("1299", 1299.0),
        ("1 299,00 ₽", 1299.0),
        ("1,299.50", 1299.5),
        ("1.299,50", 1299.5),
        ("19,99", 19.99),
        ("1,299", 1299.0),
    ],
)
def test_to_float(raw, expected):
    assert to_float(raw) == expected


def test_jsonld():
    html = """
    <html><head><script type="application/ld+json">
    {"@type": "Product", "name": "Чайник", "offers": {"price": "2 490,00"}}
    </script></head></html>
    """
    assert parse_html(html) == ("Чайник", 2490.0)


def test_meta_fallback():
    html = """
    <html><head><title>Кофемашина</title>
    <meta property="product:price:amount" content="15990">
    </head></html>
    """
    assert parse_html(html) == ("Кофемашина", 15990.0)


def test_no_price():
    with pytest.raises(ParseError):
        parse_html("<html><body>nothing here</body></html>")
