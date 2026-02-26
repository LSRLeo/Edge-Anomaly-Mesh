
import time
import ast

class RedisReader:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.nodes = [] #list of nodes available in the system, will be populated by get-nodes response from redis
        self.subscriber = None
        self.publisher = None
        self.mldict = {} #machine learning dictionary
        self.rddict = {} #raw data dictionary
    def connect(self, subscriber, publisher):
        self.subscriber = subscriber #redis subscriber will be created in main dashboard loop and passed to this class
        self.publisher = publisher #redis publisher will be created in main dashboard loop and passed to this class
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

        self.publisher.publish(self.channel_name, "get-nodes") #publish get-nodes message to redis channel
        get_nodes_response = self.subscriber.get_message() #wait for get-nodes response from redis
        if get_nodes_response is not None and get_nodes_response['type'] == 'message':
            nodes_message = get_nodes_response['data']
            self.nodes = nodes_message.split(",") #assuming nodes are sent as a comma separated string
            for node in self.nodes: #parse each node as a dict and load into dataframe
                self.publisher.publish(self.channel_name, f"get-raw-data-{node}") #publish get-raw-data message to redis channel for each node
                get_raw_data_response = self.subscriber.get_message() #wait for get-raw-data response from redis
                if get_raw_data_response is not None and get_raw_data_response['type'] == 'message':
                    raw_data_message = get_raw_data_response['data']
                    raw_data_dict = ast.literal_eval(raw_data_message) #assuming raw data is sent as a string representation of a dictionary
                    self.rddict[node] = raw_data_dict #store raw data dict in raw data dictionary with node as key

                self.publisher.publish(self.channel_name, f"get-inference-output-{node}") #publish get-inference-output message to redis channel for each node
                get_inference_output_response = self.subscriber.get_message() #wait for get-inference-output response from redis
                if get_inference_output_response is not None and get_inference_output_response['type'] == 'message':
                    inference_output_message = get_inference_output_response['data']
                    inference_output_list = ast.literal_eval(inference_output_message) #assuming inference output is sent as a string representation of a list
                    self.mldict[node] = inference_output_list #store inference output list in machine learning dictionary with node as key

    def getMLDict(self): #returns the machine learning dictionary
        return self.mldict
    def getRDDict(self): #returns the raw data dictionary
        return self.rddict