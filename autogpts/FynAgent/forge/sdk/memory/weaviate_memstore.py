import os
import uuid

# from .memstore import MemStore

import weaviate
# import hashlib


class WeaviateMemStore:
    """
    A class used to represent a Memory Store
    """

    def __init__(self, store_path: str):
        """
        Initialize the MemStore with a given store path.

        Args:
            store_path (str): The path to the store.
        """
        # self.client = chromadb.PersistentClient(
        #     path=store_path, settings=Settings(anonymized_telemetry=False)
        # )

        self.store_path = store_path

        self.class_name = "TaskDocument"
        self.default_attr_list = ["task_id", "document", "metadata", "timestamp"]
        # self.additional = "distance id vector"
        self.additional = "distance"

        # Weaviate instance API key
        auth_config = weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY"))

        # Instantiate the client with the auth config
        self.client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL"),
            auth_client_secret=auth_config,
            additional_headers={
                "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
            }
        )

    def delete_class(self):
        try:
            return self.client.schema.delete_class(self.class_name)
        except weaviate.exceptions.UnexpectedStatusCodeException as e:
            print(e)
            return e
        except Exception:
            raise

    def create_class(self):
        # https://weaviate.io/developers/weaviate/configuration/schema-configuration#property-definition
        class_obj = {
            'class': self.class_name,
            # https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-openai
            "vectorizer": "text2vec-openai",
            'properties': [
                {
                    'name': 'task_id',
                    'dataType': ['text'],
                },
                {
                    'name': 'document',
                    'dataType': ['text'],
                },
                {
                    'name': 'metadata',
                    'dataType': ['text'],
                },
                {
                    'name': 'timestamp',
                    'dataType': ['int'],
                },
            ],
        }
        return self.client.schema.create_class(class_obj)  # returns null on success

    def new_uuid(slef):
        return str(uuid.uuid4())

    def map_operator(self, operator):
        # Operators:
        # https://weaviate.io/developers/weaviate/api/graphql/filters#filter-structure
        if operator == "$and":
            return "And"
        if operator == "$or":
            return "Or"
        if operator == "$eq":
            return "Equal"
        if operator == "$neq":
            return "NotEqual"
        if operator == "$gt":
            return "GreaterThan"
        if operator == "$gte":
            return "GreaterThanEqual"
        if operator == "$lt":
            return "LessThan"
        if operator == "$lte":
            return "LessThanEqual"
        if operator == "$like":
            return "Like"
        if operator == "$wgr":
            return "WithinGeoRange"
        if operator == "$null":
            return "IsNull"
        if operator == "$in":
            return "ContainsAny"
        if operator == "$ca":
            return "ContainsAll"
        return None

    def add_task_id_filter(self, existing_filters, task_id):
        if existing_filters:
            filters = dict(existing_filters)
        else:
            filters = {}
        filters["task_id"] = {
            "$eq": task_id,
        }
        return filters

    def add_document_search_filter(self, existing_filters, document_search):
        if existing_filters:
            filters = dict(existing_filters)
        else:
            filters = {}
        if document_search:
            filters["document"] = {
                "$eq": document_search,
            }
        return filters

    def add_doc_ids_filter(self, existing_filters, doc_ids):
        if existing_filters:
            filters = dict(existing_filters)
        else:
            filters = {}
        if doc_ids:
            filters["id"] = {
                "$in": doc_ids,
            }
        return filters

    def get_filters(self, filters_raw):
        filters = {}
        if not filters_raw:
            return filters
        # Filters:
        # https://weaviate.io/developers/weaviate/search/filters
        operands = []
        for prop_name, prop_filter in filters_raw.items():
            for operator, value in prop_filter.items():
                operands.append({
                    "path": [prop_name],
                    "operator": self.map_operator(operator),
                    "valueText": value,
                })
        if len(operands) > 1:
            # Multiple operands:
            # https://weaviate.io/developers/weaviate/api/graphql/filters#multiple-operands
            filters = {
                "operator": "And",
                "operands": operands,
            }
        else:
            filters = dict(operands[0])

        print("")
        print(f"get_filters | filters_raw: {filters_raw}")
        print(f"RESULT filters: {filters}")
        print("")
        return filters

    def get_results(self, results_raw: list, class_name: str = None):
        if not class_name:
            class_name = self.class_name

        print("")
        print(f"get_results | class_name: {class_name} | results_raw: {results_raw}")
        print("")
        if "errors" in results_raw:
            results = [results_raw]
        else:
            results: list = []
            for result in results_raw["data"]["Get"][class_name]:
                results.append(result)
        return results

    def add(self, task_id: str, document: str, metadatas: dict) -> None:
        """
        Add a document to the MemStore.

        Args:
            task_id (str): The ID of the task.
            document (str): The document to be added.
            metadatas (dict): The metadata of the document.
        """
        doc_id = self.new_uuid()
        # doc_id = hashlib.sha256(document.encode()).hexdigest()[:20]
        # collection = self.client.get_or_create_collection(task_id)
        # collection.add(documents=[document], metadatas=[metadatas], ids=[doc_id])

        data_obj = dict(metadatas)
        data_obj["document"] = document
        data_obj["task_id"] = task_id

        print("")
        print(f'WeaviateMemStore.add | data_obj = {data_obj}')
        print("")
        print(f"doc_id: {doc_id}")
        print(f"task_id: {task_id}")
        print(f"document: {document}")
        print(f"metadatas: {metadatas}")
        print("")

        data_uuid = self.client.data_object.create(
            # An object with the property values of the new data object
            data_obj,
            # The class name as defined in the schema
            self.class_name,
            # optional; if not provided, one will be generated
            uuid=doc_id,
            # default QUORUM
            consistency_level=weaviate.data.replication.ConsistencyLevel.ALL,
        )
        return data_uuid

    def query(
        self,
        task_id: str,
        query: str,
        filters: dict = None,
        document_search: dict = None,
    ) -> dict:
        """
        Query the MemStore.

        Args:
            task_id (str): The ID of the task.
            query (str): The query string.
            filters (dict, optional): The filters to be applied. Defaults to None.
            search_string (str, optional): The search string. Defaults to None.

        Returns:
            dict: The query results.
        """
        # collection = self.client.get_or_create_collection(task_id)
        # kwargs = {
        #     "query_texts": [query],
        #     "n_results": 10,
        # }
        # if filters:
        #     kwargs["where"] = filters
        # if document_search:
        #     kwargs["where_document"] = document_search
        # return collection.query(**kwargs)

        # https://weaviate.io/developers/weaviate/tutorials/query#get-with-neartext
        nearText = {
            "concepts": [query],
            # prior to v1.14 use "certainty" instead of "distance"
            "distance": 0.6,
        }
        filters = self.add_task_id_filter(filters, task_id)
        filters = self.add_document_search_filter(filters, document_search)
        where_filter = self.get_filters(filters)
        results_raw = (
            self.client.query
            .get(self.class_name, self.default_attr_list)
            # note that certainty is only supported if distance==cosine
            .with_additional(self.additional)
            .with_near_text(nearText)
            .with_where(where_filter)
            .with_limit(10)
            .do()
        )
        results = self.get_results(results_raw)
        return results

    def get(self, task_id: str, doc_ids: list = None, filters: dict = None) -> dict:
        """
        Get documents from the MemStore.

        Args:
            task_id (str): The ID of the task.
            doc_ids (list, optional): The IDs of the documents to be retrieved.
            Defaults to None.
            filters (dict, optional): The filters to be applied. Defaults to None.

        Returns:
            dict: The retrieved documents.
        """
        # collection = self.client.get_or_create_collection(task_id)
        # kwargs = {}
        # if doc_ids:
        #     kwargs["ids"] = doc_ids
        # if filters:
        #     kwargs["where"] = filters
        # return collection.get(**kwargs)

        filters = self.add_task_id_filter(filters, task_id)
        filters = self.add_doc_ids_filter(filters, doc_ids)
        where_filter = self.get_filters(filters)
        results_raw = (
            self.client.query
            .get(self.class_name, self.default_attr_list)
            # note that certainty is only supported if distance==cosine
            # .with_additional("distance")
            .with_additional(self.additional)
            .with_where(where_filter)
            .do()
        )
        results = self.get_results(results_raw)
        # if doc_ids:
        #     for doc_id in doc_ids:
        #         # https://weaviate.io/developers/weaviate/search/basics
        #         nearObject = {
        #             "id": doc_ids
        #         }
        #         # or {"beacon": "weaviate://localhost/32d5a368-ace8-..."}

        #         result_raw = (
        #             self.client.query
        #             .get(self.class_name, self.default_attr_list)
        #             # note that certainty is only supported if distance==cosine
        #             .with_additional("distance")
        #             .with_where(where_filter)
        #             .do()
        #         )
        #         for result in result_raw["data"]["Get"][self.class_name]:
        #             results.append(result)
        return results

    def update(self, task_id: str, doc_ids: list, documents: list, metadatas: list):
        """
        Update documents in the MemStore.

        Args:
            task_id (str): The ID of the task.
            doc_ids (list): The IDs of the documents to be updated.
            documents (list): The updated documents.
            metadatas (list): The updated metadata.
        """
        # collection = self.client.get_or_create_collection(task_id)
        # collection.update(ids=doc_ids, documents=documents, metadatas=metadatas)

        print("")
        print('WeaviateMemStore.update')
        print("")
        print(f"task_id: {task_id}")
        print(f"doc_ids: {doc_ids}")
        print(f"documents: {documents}")
        print(f"metadatas: {metadatas}")
        print("")

        results = []
        # https://weaviate.io/developers/weaviate/api/rest/objects#update-a-data-object
        for index in range(len(doc_ids)):
            data_obj = dict(metadatas)
            data_obj["task_id"] = task_id
            data_obj["document"] = documents[index]

            print("")
            print('update one')
            print(f"uuid=doc_ids[index]: {doc_ids[index]}")
            print(f'data_obj = {data_obj}')
            print("")

            result = self.client.data_object.update(
                # An object with the property values of the new data object
                data_obj,
                # The class name as defined in the schema
                class_name=self.class_name,
                # optional; if not provided, one will be generated
                uuid=doc_ids[index],
                # default QUORUM
                consistency_level=weaviate.data.replication.ConsistencyLevel.ALL,
            )
            results.append(result)
        return results

    def delete(self, task_id: str, doc_id: str):
        """
        Delete a document from the MemStore.

        Args:
            task_id (str): The ID of the task.
            doc_id (str): The ID of the document to be deleted.
        """
        # collection = self.client.get_or_create_collection(task_id)
        # collection.delete(ids=[doc_id])

        print("")
        print(f'WeaviateMemStore.delete | doc_id = {doc_id}')
        print("")

        # https://weaviate.io/developers/weaviate/api/rest/objects#delete-a-data-object
        result = self.client.data_object.delete(
            doc_id,
            class_name=self.class_name,
            # default QUORUM
            consistency_level=weaviate.data.replication.ConsistencyLevel.ALL,
        )
        return result


if __name__ == "__main__":
    print("#############################################")

    # Initialize MemStore
    print("")
    print("** Initialize MemStore:")
    mem = WeaviateMemStore(".agent_mem_store")

    # Delete class
    print("")
    print("** Delete class:")
    mem.delete_class()

    # Create class
    print("")
    print("** Create class")
    mem.create_class()

    # Test add function
    task_id = "test_task"
    document = "This is a another new test document."
    metadatas = {"metadata": "test_metadata"}
    mem.add(task_id, document, metadatas)

    task_id = "test_task"
    document = "The quick brown fox jumps over the lazy dog."
    metadatas = {"metadata": "test_metadata"}
    mem.add(task_id, document, metadatas)

    task_id = "test_task"
    document = "AI is a new technology that will change the world."
    metadatas = {"timestamp": 1623936000}
    doc_id = mem.add(task_id, document, metadatas)

    # doc_id = hashlib.sha256(document.encode()).hexdigest()[:20]
    # doc_id = mem.new_uuid()

    # Test query function
    query = "test"
    filters = {"metadata": {"$eq": "test"}}
    search_string = {"$contains": "test"}
    doc_ids = [doc_id]
    documents = ["This is an updated test document."]
    updated_metadatas = {"metadata": "updated_test_metadata"}

    print("")
    print("** Query:")
    print(mem.query(task_id, query))

    # Test get function
    print("")
    print("** Get:")
    print(mem.get(task_id))

    # Test update function
    print("")
    print("** Update:")
    print(mem.update(task_id, doc_ids, documents, updated_metadatas))

    print("")
    print("** Delete:")
    # Test delete function
    print(mem.delete(task_id, doc_ids[0]))

    print("")
