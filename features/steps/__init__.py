from behave import then


@then("a {exception_class} error occurs")
def verify_exception_has_occured(context, exception_class):
    if context.current_exception is None:
        raise Exception("%s error expected, but it did not occur.")
    elif context.current_exception.__class__.__name__ != exception_class:
        raise context.current_exception
