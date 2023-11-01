import os
import weaviate
from typing import Any, Optional
from weaviate.exceptions import UnexpectedStatusCodeException
import json
from embedding import embed_text

from config import config,logger






class WeaviateEmail:
    def __init__(self):
        self._url = "https://contractdemo-naxwjbbo.weaviate.network"
        self._base_schema_path = "schema/weaviate_schema_email.json"
        
        self._key = "tsLs8ZTRodHsN5IrBD5X1agon7GXz9ZIbFLZ"
        self._client = self._create_client(self._url, self._key)
        self._base_schema = self._read_base_schema(self._base_schema_path)

    
    def _create_client(self, url: str, key: Optional[str] = None) -> weaviate.Client:
        """Create a Weaviate client object.

        Args:
            url: A string containing the URL of the Weaviate instance.
            key: (Optional) A string containing the API key to use for authentication.

        Returns:
            A `weaviate.Client` object if the connection is successful, otherwise `None`.

        """
        try:
            logger.info(f"Creating weaviate client with url: {url}")
            logger.info(f"Creating weaviate client with key: {key}")
            auth_config = weaviate.auth.AuthApiKey(api_key=key) if key else None
            client = weaviate.Client(
                url=url, auth_client_secret=auth_config, timeout_config=(5, 60)
            )
        except UnexpectedStatusCodeException as e:
            logger.error(f"Error connecting to Weaviate: {e}")
            raise e
        return client

    def _read_base_schema(self, base_schema_path: str) -> dict:
        """Read the common schema from a JSON file.

        Args:
            base_schema_path (str): path to JSON file.

        Returns:
            (dict): base schema.

        """
        try:
            if os.path.isfile(base_schema_path):
                with open(base_schema_path, "r", encoding="utf8") as file:
                    return json.load(file)
        except Exception as e:
            logger.error(f"Error reading schema file: {e}")
            raise e


    def list_class(self) -> list:
        """Get existing class names.
        """
        try:
            schemas = self._client.schema.get()
            return [x["class"] for x in schemas["classes"]]
        except Exception as e:
            logger.error(f"Error listing class: {e}")
            raise e
            

    def create_class(
        self,
        class_name: str,
        class_description: str,
    ) -> Any:
        """Create a new data object class.

        Args:
            class_name (str): The name of the class.
            class_description (str): The description of the class.
            
        Returns:
            None.

        """
        try:
            class_obj = self._base_schema
            class_obj["class"] = class_name
            class_obj["description"] = class_description
            self._client.schema.create_class(class_obj)
            logger.info(f"Created class with schema: {class_obj}")
            
        except Exception as e:
            logger.error(f"Error creating class: {e}")
            raise e

    def varify_class(self, class_name: str):
        """Check whether a class exists.

        Args:
            class_name (str): The class name to be verified.
            
        Returns:
            (bool): True if the class exists.
        
        """
        try:
            schema = self._client.schema.get()
            class_names = [x["class"] for x in schema["classes"]]
            if class_name in class_names:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error varifying class: {e}")
            raise e


    def delete_class(
        self,
        class_name: str,
    ) -> Any:
        """Delete a class.

        Args:
            class_name (str): The name of the class to be deleted.
            
        Returns:
            None

        """
        try:
            self._client.schema.delete_class(class_name)
            logger.info(f"Deleted class {class_name}")
        except Exception as e:
            logger.error(f"Error deleting class: {e}")
            raise e

    def ingest_data(self, class_name: str, chunk_list: list, vector_list: list) -> Any:
        """Save data to class.

        Args:
            class_name (str): The name of the class to save the data.
            chunk_list (list): A list of chunk objects (dict).
            vector_list (list): A list of chunk embeddings (list) corresponding to the chunk_list.

        Returns:
            None.

        """
        try:
            for idx, data_obj in enumerate(chunk_list):
                self._client.data_object.create(data_obj,class_name,vector=vector_list[idx])
        except Exception as e:
            logger.error(f"Error ingesting data: {e}")
            raise e

    def query_near_vector(
        self,
        input_string: str,
        class_name: str,
        properties: list,
        certainty: Optional[float] = 0.7,
        number_of_result_limit: Optional[int] = 5,
    ) -> json:
        """Find data objects in the vicinity of an input vector.

        Args:
            input_string (str): The input query.
            class_name (str): The class to query.
            properties (list): A list of properties to return.
            certainty (float, optional): Certainty threshold. Default is 0.7.
            number_of_result_limit (int, optional): Number of data objects to return. Default is 5.

        Returns:
            (json): The query output.

        """

        try:
            near_vector = embed_text([input_string])[0]

            content = {
                "vector": near_vector,
                "certainty": certainty,
            }


            result = (
                self._client.query.get(
                    class_name,
                    properties,
                )
                .with_near_vector(content)
                .with_limit(number_of_result_limit)
                .with_additional(["certainty"])
                .do()
            )

            return result
        except Exception as e:
            logger.error(f"Error querying near vector: {e}")
            return {}

    

class WeaviateContract:
    def __init__(self):
        self._url = "https://contractdemo-naxwjbbo.weaviate.network"
        self._base_schema_path = "schema/weaviate_schema_contract.json"
        
        self._key = "tsLs8ZTRodHsN5IrBD5X1agon7GXz9ZIbFLZ"
        self._client = self._create_client(self._url, self._key)
        self._base_schema = self._read_base_schema(self._base_schema_path)

    
    def _create_client(self, url: str, key: Optional[str] = None) -> weaviate.Client:
        """Create a Weaviate client object.

        Args:
            url: A string containing the URL of the Weaviate instance.
            key: (Optional) A string containing the API key to use for authentication.

        Returns:
            A `weaviate.Client` object if the connection is successful, otherwise `None`.

        """
        try:
            logger.info(f"Creating weaviate client with url: {url}")
            logger.info(f"Creating weaviate client with key: {key}")
            auth_config = weaviate.auth.AuthApiKey(api_key=key) if key else None
            client = weaviate.Client(
                url=url, auth_client_secret=auth_config, timeout_config=(5, 60)
            )
        except UnexpectedStatusCodeException as e:
            logger.error(f"Error connecting to Weaviate: {e}")
            raise e
        return client

    def _read_base_schema(self, base_schema_path: str) -> dict:
        """Read the common schema from a JSON file.

        Args:
            base_schema_path (str): path to JSON file.

        Returns:
            (dict): base schema.

        """
        try:
            if os.path.isfile(base_schema_path):
                with open(base_schema_path, "r", encoding="utf8") as file:
                    return json.load(file)
        except Exception as e:
            logger.error(f"Error reading schema file: {e}")
            raise e


    def list_class(self) -> list:
        """Get existing class names.
        """
        try:
            schemas = self._client.schema.get()
            return [x["class"] for x in schemas["classes"]]
        except Exception as e:
            logger.error(f"Error listing class: {e}")
            raise e
            

    def create_class(
        self,
        class_name: str,
        class_description: str,
    ) -> Any:
        """Create a new data object class.

        Args:
            class_name (str): The name of the class.
            class_description (str): The description of the class.
            
        Returns:
            None.

        """
        try:
            class_obj = self._base_schema
            class_obj["class"] = class_name
            class_obj["description"] = class_description
            self._client.schema.create_class(class_obj)
            logger.info(f"Created class with schema: {class_obj}")
            
        except Exception as e:
            logger.error(f"Error creating class: {e}")
            raise e

    def varify_class(self, class_name: str):
        """Check whether a class exists.

        Args:
            class_name (str): The class name to be verified.
            
        Returns:
            (bool): True if the class exists.
        
        """
        try:
            schema = self._client.schema.get()
            class_names = [x["class"] for x in schema["classes"]]
            if class_name in class_names:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error varifying class: {e}")
            raise e


    def delete_class(
        self,
        class_name: str,
    ) -> Any:
        """Delete a class.

        Args:
            class_name (str): The name of the class to be deleted.
            
        Returns:
            None

        """
        try:
            self._client.schema.delete_class(class_name)
            logger.info(f"Deleted class {class_name}")
        except Exception as e:
            logger.error(f"Error deleting class: {e}")
            raise e

    def ingest_data(self, class_name: str, chunk_list: list, vector_list: list) -> Any:
        """Save data to class.

        Args:
            class_name (str): The name of the class to save the data.
            chunk_list (list): A list of chunk objects (dict).
            vector_list (list): A list of chunk embeddings (list) corresponding to the chunk_list.

        Returns:
            None.

        """
        try:
            for idx, data_obj in enumerate(chunk_list):
                self._client.data_object.create(data_obj,class_name,vector=vector_list[idx])
        except Exception as e:
            logger.error(f"Error ingesting data: {e}")
            raise e

    def query_near_vector(
        self,
        input_string: str,
        class_name: str,
        properties: list,
        certainty: Optional[float] = 0.7,
        number_of_result_limit: Optional[int] = 5,
    ) -> json:
        """Find data objects in the vicinity of an input vector.

        Args:
            input_string (str): The input query.
            class_name (str): The class to query.
            properties (list): A list of properties to return.
            certainty (float, optional): Certainty threshold. Default is 0.7.
            number_of_result_limit (int, optional): Number of data objects to return. Default is 5.

        Returns:
            (json): The query output.

        """

        try:
            near_vector = embed_text([input_string])[0]

            content = {
                "vector": near_vector,
                "certainty": certainty,
            }


            result = (
                self._client.query.get(
                    class_name,
                    properties,
                )
                .with_near_vector(content)
                .with_limit(number_of_result_limit)
                .with_additional(["certainty"])
                .do()
            )

            return result
        except Exception as e:
            logger.error(f"Error querying near vector: {e}")
            return {}

    