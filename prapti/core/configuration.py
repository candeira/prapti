"""
    The Configuration is a tree of dataclasses that are used to
    configure actions, responders, hooks, plugins, etc.
"""
from dataclasses import dataclass, field
import ast

class PluginsConfiguration:
    """contains a dynamic configuration entry for each loaded plugin"""
    pass

class EmptyPluginConfiguration:
    """used when the plugin provides no plugin-level configuration"""
    pass

class RespondersConfiguration:
    """contains a dynamic configuration entry for each instantiated responder"""
    pass

class EmptyResponderConfiguration:
    """used when the plugin provides no responder-level configuration"""
    pass

@dataclass
class RootConfiguration:
    """The root of the configuration tree"""
    config_root: bool = False # halt in-tree configuration file loading when true
    dry_run: bool = False # simulate LLM responses. disable side-effects (plugin specific)

    plugins: PluginsConfiguration = field(default_factory=PluginsConfiguration)

    responders: RespondersConfiguration = field(default_factory=RespondersConfiguration)
    responder_stack: list[str] = field(default_factory=list)

    # global/generic parameter aliases
    # if you set one of these in your markdown it will override the model-specific parameter that it aliases
    model: str = None
    temperature: float = None
    n: int = None # number of responses to generate

def assign_configuration_field(original_field_name: str, field_value: str, root_config: RootConfiguration) -> None:
    field_name = original_field_name
    target = root_config
    while '.' in field_name:
        source, field_name = field_name.split('.', maxsplit=1)
        if not hasattr(target, source):
            print(f"warning: unknown configuration field '{original_field_name}',  component '{source}' does not exist, skipping command")
            return
        target = getattr(target, source)

    if hasattr(target, field_name):
        try:
            parsed_value = ast.literal_eval(field_value)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"error parsing configuration value '{field_value}' as a Python literal: {e}") from e
        field_type = target.__annotations__.get(field_name)
        try:
            assigned_value = field_type(parsed_value)
        except Exception as e:
            raise ValueError(f"error coercing configuration value '{field_value}' to a '{field_type}'") from e
        setattr(target, field_name, assigned_value)
        print(f"setting configuration.{original_field_name} = {parsed_value}")
    else:
        print(f"warning: unknown configuration field '{original_field_name}', skipping command")
