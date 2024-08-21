from app.commun.decorators import safe_execution


def test_normal_execution():
    @safe_execution
    def normal_function():
        return "Hello, World!"

    assert normal_function() == "Hello, World!"


def test_exception_handling():
    @safe_execution
    def failing_function():
        raise ValueError("This is a test exception")

    assert failing_function() is None


def test_with_arguments():
    @safe_execution
    def add(a, b):
        return a + b

    assert add(2, 3) == 5


def test_with_keyword_arguments():
    @safe_execution
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}!"

    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob", greeting="Hi") == "Hi, Bob!"


def test_nested_exception():
    @safe_execution
    def nested_exception():
        def inner():
            raise ValueError("Inner exception")

        inner()

    assert nested_exception() is None


def test_specific_exception():
    @safe_execution
    def specific_exception():
        raise ValueError("Specific exception")

    assert specific_exception() is None


def test_no_exception_with_none_return():
    @safe_execution
    def none_return():
        return None

    assert none_return() is None
