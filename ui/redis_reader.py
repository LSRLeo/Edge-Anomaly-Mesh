
import json
import time
import ast

class RedisReader:
    def __init__(self, channel_name, publisher, subscriber):
        self.channel_name = channel_name
        self.nodes = [] #list of nodes available in the system, will be populated by get-nodes response from redis
        self.subscriber = subscriber
        self.publisher = publisher
        self.mldict = {} #machine learning dictionary
        self.rddict = {} #raw data dictionary
        self.message_counter = 1 #counter for m_id
    
    def refresh(self): #refreshes the dataframes with new data from redis, thread for subscribing to redis will be created in main dashboard loop

        """
        pull all available nodes
        put it into a list
        for each node pull most recent raw data and store it in the raw data dataframe
        parse the raw data into dictionary format for easy indexing
        for each node pull most recent inference output and store it in the machine learning dataframe
        """
        time.sleep(10) #sleep for 10 seconds to allow time for subscriber to connect and receive get-nodes response from redis (also acts as the periodic refresh interval)
        if self.subscriber is None or self.publisher is None:
            raise Exception("Subscriber and Publisher must be connected before refreshing dataframes")
        newmldict = {}
        newrddict = {}
        self.nodes = self.request_node_ids() #request list of node IDs from redis and update nodes list
        if self.nodes is not None:
            
            for node in self.nodes: #parse each node as a dict and load into dataframe
                get_raw_data_message = self.request_raw_node_data(node) #request raw data for node from redis
                if get_raw_data_message is not None:
                    raw_data_dict = get_raw_data_message.get("records", {})
                    newrddict[node] = raw_data_dict #store raw data dict in raw data dictionary with node as key

                get_inference_output_message = self.request_inference_output(node) #request inference output for node from redis
                if get_inference_output_message is not None:
                    inference_output_list = get_inference_output_message.get("records", []) 
                    newmldict[node] = inference_output_list #store inference output list in machine learning dictionary with node as key
        self.rddict = newrddict #update raw data dictionary with new data
        self.mldict = newmldict #update machine learning dictionary with new data
    def request_node_ids(self):
        """
        Request list of node IDs from Redis.
        """
        request = {
            'm_type': 'get-nodes', 
            'm_id': f'ui_{self.message_counter:05d}'}
        self.message_counter += 1
        self.publisher.publish(self.channel_name, json.dumps(request))
        start = time.monotonic() #start timer to prevent infinite blocking
        try:
            for msg in self.subscriber.listen():
                if time.monotonic() - start > 3: #timeout after 3 seconds
                    raise TimeoutError("Timeout waiting for node IDs")
                if msg['type'] == 'message':
                    data = json.loads(msg['data'])
                    if data.get('responding_to') == request['m_id']:
                        return data.get('nodes', [])
                if time.monotonic() - start > 5: #timeout after 5 seconds
                    print("Timeout waiting for node IDs")
                    return None
        except Exception as e:
            print(f"Error requesting node IDs: {e}")
            return None
    def request_raw_node_data(self, node_id):
        """
        Request raw data for a specific node from Redis.
        """
        request = {
            'm_type': 'get-recent-raw-data', 
            'm_id': f'ui_{self.message_counter:05d}',
            'node_id': node_id}
        self.message_counter += 1
        self.publisher.publish(self.channel_name, json.dumps(request))
        start = time.monotonic() #start timer to prevent infinite blocking
        try:
            for msg in self.subscriber.listen():
                if time.monotonic() - start > 3: #timeout after 3 seconds
                    raise TimeoutError(f"Timeout waiting for raw data for node {node_id}")
                if msg['type'] == 'message':
                    data = json.loads(msg['data'])
                    if data.get('responding_to') == request['m_id'] and data.get('node_id') == node_id:
                        return data.get('records', {})
                if time.monotonic() - start > 5: #timeout after 5 seconds
                    print(f"Timeout waiting for raw data for node {node_id}")
                    return None
        except Exception as e:
            print(f"Error requesting raw data for node {node_id}: {e}")
            return None

    def request_inference_output(self, node_id):
        """
        Request inference output for a specific node from Redis.
        """
        request = {
            'm_type': 'get-recent-inference', 
            'm_id': f'ui_{self.message_counter:05d}',
            'node_id': node_id
        }
        self.message_counter += 1
        self.publisher.publish(self.channel_name, json.dumps(request))
        start = time.monotonic() #start timer to prevent infinite blocking
        try:
            for msg in self.subscriber.listen():
                if time.monotonic() - start > 3: #timeout after 3 seconds
                    raise TimeoutError(f"Timeout waiting for inference output for node {node_id}")
                if msg['type'] == 'message':
                    data = json.loads(msg['data'])
                    if data.get('responding_to') == request['m_id'] and data.get('node_id') == node_id:
                        return data.get('inference_output', []) #assumes list of probabilities, might change depending on team discourse. (2/27/2026) -TE
                if time.monotonic() - start > 5: #timeout after 5 seconds
                    print(f"Timeout waiting for inference output for node {node_id}")
                    return None
        except Exception as e:
            print(f"Error requesting inference output for node {node_id}: {e}")
            return None
    def getMLDict(self): #returns the machine learning dictionary
        return self.mldict
    def getRDDict(self): #returns the raw data dictionary
        return self.rddict