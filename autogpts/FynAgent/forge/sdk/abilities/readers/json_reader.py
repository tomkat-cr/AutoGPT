from __future__ import annotations
import json
from langchain.document_loaders.json_loader import JSONLoader

from ..utilities import log_debug
from .vector_index import VectorEntry

from ..registry import ability


def get_json_files(json_files: list) -> list:
    all_pages = []
    for json_file in json_files:
        log_debug(f"json_file: {json_file}")
        output_file_spec = f"./downloads/{json_file.name}"
        if not json_file.name.endswith(".json"):
            continue
        with open(output_file_spec, 'wb') as output_file:
            json_content = json_file.getvalue()
            # json_dict = {
            #     'content': json.loads(json_content)
            # }
            # json_dict[attr_name] = get_page_content_attr(json_file.name)
            json_dict = {}
            json_dict['content'] = json.loads(json_content)
            # The attribute 'page_content' must be a string,
            # so the json content must be serialized
            page_content = json.dumps(json_dict['content'])
            json_dict['page_content'] = page_content
            json_content = bytes(json.dumps(json_dict), 'UTF8')
            log_debug(f"json_content: {json_content}")
            output_file.write(json_content)
        # Load JSON file content
        loader = JSONLoader(
            output_file_spec,
            # jq_schema=f'.[].{attr_name}'
            jq_schema='.page_content'
        )
        json_pages = loader.load()
        # Add some context for the JSON file
        metadata = {
            'source': output_file_spec,
            'file_path': output_file_spec,
            'file_name': json_file.name,
            'file_type': '.json',
            "comments": ",".join([
                "this is the context and content of the:",
                "supplied json file",
                "loaded json file"
                "supplied json",
                "loaded json",
            ])
        }
        json_pages.append(
            VectorEntry(
                page_content=f"The loaded JSON filename is {json_file.name}",
                metadata=metadata
            )
        )
        all_pages += json_pages

    return all_pages


@ability(
    name="json_load",
    description="Read all JSON files content",
    parameters=[
        {
            "name": "json_files",
            "description": "List of JSON files to load",
            "type": "list[str]",
            "required": True,
        },
    ],
    output_type="list[str]",
)
async def json_load(agent, task_id: str, json_files: list[str]) -> str:
    """Return all JSON files content

    Args:
        json_files (lst[str]): List of JSON files to load.

    Returns:
        str: content of all JSON files.
    """
    results = json.dumps(
        get_json_files(json_files),
        ensure_ascii=False,
        indent=4
    )
    return results
