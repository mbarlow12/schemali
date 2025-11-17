from collections.abc import Sequence
from typing import Any, Literal, NamedTuple

from pydantic import BaseModel
from pydantic.json_schema import (
    DEFAULT_REF_TEMPLATE,
    GenerateJsonSchema,
    JsonSchemaMode,
    JsonSchemaValue,
    models_json_schema,
)
from pydantic_core import CoreSchema, Url

from schemali.generator import SchemaliGenerateJsonSchema


class ModelArg(NamedTuple):
    model: type[BaseModel]
    mode: JsonSchemaMode = "validation"
    schema_id: str = "schema"


DEFAULT_URL: Url = Url("https://example.com")


def models_json_schema_(
    models: Sequence[tuple[type[BaseModel], JsonSchemaMode]],
    *,
    base_uri: Url = DEFAULT_URL,
    by_alias: bool = True,
    title: str | None = None,
    description: str | None = None,
    ref_template: str = DEFAULT_REF_TEMPLATE,
    union_format: Literal["any_of", "primitive_type_array"] = "any_of",
    schema_generator: type[GenerateJsonSchema] = SchemaliGenerateJsonSchema,
) -> tuple[dict[tuple[type[BaseModel], JsonSchemaMode], JsonSchemaValue], JsonSchemaValue]:
    """Utility function to generate a JSON Schema for multiple models.

    Args:
        models: A sequence of tuples of the form (model, mode).
        by_alias: Whether field aliases should be used as keys in the generated JSON Schema.
        title: The title of the generated JSON Schema.
        description: The description of the generated JSON Schema.
        ref_template: The reference template to use for generating JSON Schema references.
        union_format: The format to use when combining schemas from unions together. Can be one of:

            - `'any_of'`: Use the [`anyOf`](https://json-schema.org/understanding-json-schema/reference/combining#anyOf)
              keyword to combine schemas (the default).
            - `'primitive_type_array'`: Use the [`type`](https://json-schema.org/understanding-json-schema/reference/type)
              keyword as an array of strings, containing each type of the combination. If any of the schemas is not a primitive
              type (`string`, `boolean`, `null`, `integer` or `number`) or contains constraints/metadata, falls back to
              `any_of`.
        schema_generator: The schema generator to use for generating the JSON Schema.

    Returns:
        A tuple where:
            - The first element is a dictionary whose keys are tuples of JSON schema key type and JSON mode, and
                whose values are the JSON schema corresponding to that pair of inputs. (These schemas may have
                JsonRef references to definitions that are defined in the second returned element.)
            - The second element is a JSON schema containing all definitions referenced in the first returned
                    element, along with the optional title and description keys.
    """

    instance = schema_generator(
        by_alias=by_alias, ref_template=ref_template, union_format=union_format
    )
    inputs: list[tuple[type[BaseModel], JsonSchemaMode, CoreSchema]] = [
        (m, mode, m.__pydantic_core_schema__) for m, mode in models
    ]
    json_schemas_map, definitions = instance.generate_definitions(inputs)

    json_schema: dict[str, Any] = {
        "$schema": instance.schema_dialect,
        "$id": str(base_uri),
    }
    if definitions:
        json_schema["$defs"] = definitions
    if title:
        json_schema["title"] = title
    if description:
        json_schema["description"] = description

    return json_schemas_map, json_schema


def geterate_json_dict(*model_args: Sequence[ModelArg]):
    schema_map, schema = models_json_schema([(ml, md) for ml, md, _ in model_args])
    defs = schema["$defs"]
