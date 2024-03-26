from typing import Any, List, Optional, Text

from langchain_core.tools import StructuredTool
from loguru import logger

from langflow.custom import CustomComponent
from langflow.field_typing import Tool
from langflow.graph.graph.base import Graph
from langflow.helpers.flow import build_function_and_schema
from langflow.schema.dotdict import dotdict


class FlowToolComponent(CustomComponent):
    display_name = "Flow as Tool"
    description = "Construct a Tool from a function that runs the loaded Flow."
    field_order = ["flow_name", "name", "description", "return_direct"]

    def get_flow_names(self) -> List[str]:
        flow_records = self.list_flows()
        return [flow_record.data["name"] for flow_record in flow_records]

    def get_flow(self, flow_name: str) -> Optional[Text]:
        """
        Retrieves a flow by its name.

        Args:
            flow_name (str): The name of the flow to retrieve.

        Returns:
            Optional[Text]: The flow record if found, None otherwise.
        """
        flow_records = self.list_flows()
        for flow_record in flow_records:
            if flow_record.data["name"] == flow_name:
                return flow_record
        return None

    def update_build_config(self, build_config: dotdict, field_value: Any, field_name: str | None = None):
        logger.debug(f"Updating build config with field value {field_value} and field name {field_name}")
        if field_name == "flow_name":
            build_config["flow_name"]["options"] = self.get_flow_names()

        return build_config

    def build_config(self):
        return {
            "flow_name": {
                "display_name": "Flow Name",
                "info": "The name of the flow to run.",
                "options": [],
                "real_time_refresh": True,
                "refresh_button": True,
            },
            "name": {
                "display_name": "Name",
                "description": "The name of the tool.",
            },
            "description": {
                "display_name": "Description",
                "description": "The description of the tool.",
            },
            "return_direct": {
                "display_name": "Return Direct",
                "description": "Return the result directly from the Tool.",
                "advanced": True,
            },
        }

    async def build(self, flow_name: str, name: str, description: str, return_direct: bool = False) -> Tool:
        flow_record = self.get_flow(flow_name)
        if not flow_record:
            raise ValueError("Flow not found.")
        graph = Graph.from_payload(flow_record.data["data"])
        dynamic_flow_function, schema = build_function_and_schema(flow_record, graph)
        tool = StructuredTool.from_function(
            coroutine=dynamic_flow_function,
            name=name,
            description=description,
            return_direct=return_direct,
            args_schema=schema,
        )
        description_repr = repr(tool.description).strip("'")
        args_str = "\n".join([f"- {arg_name}: {arg_data['description']}" for arg_name, arg_data in tool.args.items()])
        self.status = f"{description_repr}\nArguments:\n{args_str}"
        return tool
