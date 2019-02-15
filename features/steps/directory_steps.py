from behave import given


@given("I created a Directory")
def create_directory(context):
    context.directory_manager.get_any_directory()
