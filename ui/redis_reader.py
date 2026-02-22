import pandas as pd
class RedisReader:
    def __init__(self):
        self.subscriber = None
        self.publisher = None
        self.mldf = pd.DataFrame() #machine learning dataframe
        self.rddf = pd.DataFrame() #raw data dataframe
    def connect(self, subscriber, publisher):
        self.subscriber = subscriber #redis subscriber will be created in main dashboard loop and passed to this class
        self.publisher = publisher #redis publisher will be created in main dashboard loop and passed to this class
    def refresh(self): #refreshes the dataframes with new data from redis, thread for subscribing to redis will be created in main dashboard loop

        pass

    def getMLDF(self): #returns the machine learning dataframe
        return self.mldf
    def getRDDf(self): #returns the raw data dataframe
        return self.rddf