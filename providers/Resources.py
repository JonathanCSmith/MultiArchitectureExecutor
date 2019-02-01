class ResourceProvider:
    def acquire_resource(self, ticket):
        pass

    def return_resource(self, ticket):
        pass

    def valid(self):
        pass

    def supports_array(self):
        return False


class Resource:
    def execute(self, engine, execution_wrapper, script_arguments, ticket):
        pass