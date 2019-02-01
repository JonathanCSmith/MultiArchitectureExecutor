import os

import sys


class Runtime:
    _engine = None
    _is_cluster = False
    _vm_properties = None
    _resource_provider = None

    def __init__(self, engine):
        self._engine = engine
        engine.set_runtime(self)

    def set_runtime_provider(self, provider, file_system):
        self._engine.info("Setting the runtime type to: " + provider)

        # Evaluate the provider
        if not provider or not os.path.exists(provider):
            new_provider = os.path.join(file_system.get_working_directory(), "provider.py")
            if not os.path.exists(new_provider):
                self._engine.error("No valid path to a resource provider. Looked for: " + provider + " and " + new_provider)
                return False

        self._engine.info("Attempting to load the provider into the classpath")
        try:
            version = sys.version_info
            if version >= (3, 5):
                import importlib.util
                spec = importlib.util.spec_from_file_location("provider", provider)
                provider_instance = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(provider_instance)

            elif version >= (3, 3):
                from importlib.machinery import SourceFileLoader
                provider_instance = SourceFileLoader("provider", provider).load_module()

            else:
                self._engine.error("Python 2 is currently not supported")
                return False

            self._resource_provider = provider_instance.build_provider(file_system)
            if self._resource_provider is None or not self._resource_provider or not self._resource_provider.valid():
                return False

        except Exception as ex:
            self._engine.error("Caught an exception when binding the resource provider.")
            self._engine.exception(ex)
            return False

        return True

    def is_cloud(self):
        return not self._is_cluster

    def is_cluster(self):
        return self._is_cluster

    def acquire_resource(self, ticket):
        return self._resource_provider.acquire_resource(ticket)

    def free_resource(self, ticket):
        self._resource_provider.return_resource(ticket)

    def supports_array(self):
        return self._resource_provider.supports_array();
