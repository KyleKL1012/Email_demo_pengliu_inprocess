import requests
import json

from config import config, logger

class Bam:
    def __init__(self):
        self.bam_key = 'pak-AwkYTgLft5uB85xVSeqWdZIHaMfWD-VlWnxWC_WU50g'

    def call_bam(
        self,
        input_str: str,
        task: str = "qa",
    ) -> dict:
        """Call bam RESTAPI.

        Args:
            input_str (str): The input text to the model.
            task (str): The task to perform, such as qa, summarization.
            
        Returns:
            (dict): The bam output.
            
        Raises:
            requests.RequestException: If there is an error making the API request.
            ValueError: If the url and bam_key are not provided.

        """
        try:
            url = 'https://bam-api.res.ibm.com/v1/generate'
        except:
            raise ValueError("url must be provided or set in config file.")
        try:
            bam_key = self.bam_key
        except:
            raise ValueError("BAM_KEY must be provided or set in ENV.")

        parameter = config["model"]["bam"][task]["param"]
        bam_input = {
            "model_id": parameter["model_id"],
            "inputs": [input_str],
            "parameters": {
                "decoding_method": parameter["decoding_method"],
                "temperature": parameter["temperature"],
                "top_p": parameter["top_p"],
                "top_k": parameter["top_k"],
                "repetition_penalty": parameter["repetition_penalty"],
                "min_new_tokens":parameter["min_new_tokens"],
                "max_new_tokens": parameter["max_new_tokens"]
            }
        }
        logger.info(f"BAM input: {json.dumps(bam_input)}")

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {bam_key}"
            }
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(bam_input)
            )
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred during API call of bam: {str(e)}")
            return {}
