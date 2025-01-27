import pytest

from ssg import boolean_expression
from xml.dom import expatbuilder


class PlatformFunction(boolean_expression.Function):
    def as_cpe_lang_xml(self):
        return '<cpe-lang:logical-test negate="' + ('true' if self.is_not() else 'false') + \
               '" operator="' + ('OR' if self.is_or() else 'AND') + '">' + \
               ''.join([arg.as_cpe_lang_xml() for arg in self.args]) + "</cpe-lang:logical-test>"


class PlatformSymbol(boolean_expression.Symbol):
    def as_cpe_lang_xml(self):
        return '<cpe-lang:fact-ref name="cpe:/a:' + self.name + ':' + '"/>'


class PlatformAlgebra(boolean_expression.Algebra):
    def __init__(self):
        super(PlatformAlgebra, self).__init__(symbol_cls=PlatformSymbol, function_cls=PlatformFunction)

    @staticmethod
    def as_cpe_lang_xml(expr):
        s = '<cpe-lang:platform id="' + expr.as_id() + '">' + expr.as_cpe_lang_xml() + '</cpe-lang:platform>'
        # A primitive but simple way to pretty-print an XML string
        return expatbuilder.parseString(s, False).toprettyxml()


@pytest.fixture
def algebra():
    return PlatformAlgebra()


@pytest.fixture
def expression1(algebra):
    return algebra.parse(u'(oranges | banana) and not ~apple + !pie', simplify=True)


def test_id(expression1):
    assert str(expression1.as_id()) == 'apple_and_banana_or_oranges_or_not_pie'


def test_as_cpe_xml(algebra, expression1):
    xml = algebra.as_cpe_lang_xml(algebra.dnf(expression1))
    assert xml == """<?xml version="1.0" ?>
<cpe-lang:platform id="apple_and_banana_or_apple_and_oranges_or_not_pie">
\t<cpe-lang:logical-test negate="false" operator="OR">
\t\t<cpe-lang:logical-test negate="false" operator="AND">
\t\t\t<cpe-lang:fact-ref name="cpe:/a:apple:"/>
\t\t\t<cpe-lang:fact-ref name="cpe:/a:banana:"/>
\t\t</cpe-lang:logical-test>
\t\t<cpe-lang:logical-test negate="false" operator="AND">
\t\t\t<cpe-lang:fact-ref name="cpe:/a:apple:"/>
\t\t\t<cpe-lang:fact-ref name="cpe:/a:oranges:"/>
\t\t</cpe-lang:logical-test>
\t\t<cpe-lang:logical-test negate="true" operator="AND">
\t\t\t<cpe-lang:fact-ref name="cpe:/a:pie:"/>
\t\t</cpe-lang:logical-test>
\t</cpe-lang:logical-test>
</cpe-lang:platform>
"""


def test_expression_with_parameter(algebra):
    exp = algebra.parse(u'package[test] and os_release[rhel]')
    assert exp(**{"package[test]": True, "os_release[rhel]": True})


def test_as_id(algebra):
    exp1 = algebra.parse(u'package')
    exp2 = algebra.parse(u'package[test]')
    assert exp1.as_id() == "package"
    assert exp2.as_id() == "package_test"


def test_as_dict(algebra):
    exp1 = algebra.parse(u'package')
    exp1_dict = {
        "arg": "",
        "id": "package",
        "name": "package"
    }
    exp2 = algebra.parse(u'package[test]')
    exp2_dict = {
        "arg": "test",
        "id": "package_test",
        "name": "package"
    }
    assert exp1.as_dict() == exp1_dict
    assert exp2.as_dict() == exp2_dict
