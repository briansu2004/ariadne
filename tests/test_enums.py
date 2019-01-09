import pytest

from graphql import graphql_sync, build_schema

from ariadne import Enum, ResolverMap, make_executable_schema

enum_definition = """
    enum Episode {
        NEWHOPE
        EMPIRE
        JEDI
    }
"""

enum_field = """
    type Query {
        testEnum: Episode!
    }
"""

TEST_VALUE = "NEWHOPE"
INVALID_VALUE = "LUKE"


def test_succesfull_enum_typed_field():
    query = ResolverMap("Query")
    query.field("testEnum")(lambda *_: TEST_VALUE)

    schema = make_executable_schema([enum_definition, enum_field], query)
    result = graphql_sync(schema, "{ testEnum }")
    assert result.errors is None


def test_unsuccesfull_invalid_enum_value_evaluation():
    query = ResolverMap("Query")
    query.field("testEnum")(lambda *_: INVALID_VALUE)

    schema = make_executable_schema([enum_definition, enum_field], query)
    result = graphql_sync(schema, "{ testEnum }")
    assert result.errors is not None


enum_param = """
    type Query {
        testEnum(value: Episode!): Boolean!
    }
"""


def test_successfull_enum_value_passed_as_argument():
    query = ResolverMap("Query")
    query.field("testEnum")(lambda *_, value: True)

    schema = make_executable_schema([enum_definition, enum_param], query)
    result = graphql_sync(schema, "{ testEnum(value: %s) }" % TEST_VALUE)
    assert result.errors is None, result.errors


def test_unsuccessfull_invalid_enum_value_passed_as_argument():
    query = ResolverMap("Query")
    query.field("testEnum")(lambda *_, value: True)

    schema = make_executable_schema([enum_definition, enum_param], query)
    result = graphql_sync(schema, "{ testEnum(value: %s) }" % INVALID_VALUE)
    assert result.errors is not None


@pytest.fixture
def schema_with_enum():
    return build_schema("\n\n".join((enum_definition, enum_field)))


def test_attempt_bind_custom_enum_to_undefined_type_raises_error(schema_with_enum):
    enum = Enum("Undefined", {})
    with pytest.raises(ValueError):
        enum.bind_to_schema(schema_with_enum)


def test_attempt_bind_custom_enum_to_wrong_schema_type_raises_error(schema_with_enum):
    enum = Enum("Query", {})
    with pytest.raises(ValueError):
        enum.bind_to_schema(schema_with_enum)


def test_attempt_bind_custom_enum_to_schema_enum_missing_value_raises_error(
    schema_with_enum
):
    enum = Enum("Episode", {"JARJAR": 1999})
    with pytest.raises(ValueError):
        enum.bind_to_schema(schema_with_enum)


custom_enum = Enum("Episode", {"NEWHOPE": 1977, "EMPIRE": 1980, "JEDI": 1983})

TEST_INTERNAL_VALUE = 1977


def test_enum_is_resolved_from_internal_value():
    query = ResolverMap("Query")
    query.field("testEnum")(lambda *_: TEST_INTERNAL_VALUE)

    schema = make_executable_schema([enum_definition, enum_field], [query, custom_enum])
    result = graphql_sync(schema, "{ testEnum }")
    assert result.data["testEnum"] == TEST_VALUE


def test_enum_arg_is_transformed_to_internal_value():
    query = ResolverMap("Query")
    query.field("testEnum")(lambda *_, value: value == TEST_INTERNAL_VALUE)

    schema = make_executable_schema([enum_definition, enum_param], [query, custom_enum])
    result = graphql_sync(schema, "{ testEnum(value: %s) }" % TEST_VALUE)
    assert result.data["testEnum"] is True
