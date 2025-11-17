from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode, JsonSchemaValue
from pydantic_core import CoreSchema


class SchemaliGenerateJsonSchema(GenerateJsonSchema):
    def generate(self, schema: CoreSchema, mode: JsonSchemaMode = "validation") -> JsonSchemaValue:
        json_schema = super().generate(schema, mode=mode)
        json_schema["title"] = "Customize title"
        json_schema["$schema"] = self.schema_dialect
        return json_schema
