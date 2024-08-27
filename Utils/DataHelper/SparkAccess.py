import pyspark
import pyspark.pandas as ps
from pyspark.sql import SparkSession
import logging
import config


# -----------------------------------------------------------------------------------------------
# Spark
# -----------------------------------------------------------------------------------------------
class SparkAccess:
    spark = None

    config.PYSPARK_CONFIG  = (
        pyspark.SparkConf()
            .setAppName('CLS-SRL')
            .setMaster('local[*]')
            .set("spark.driver.memory", "4g")
    )

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SparkAccess, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    def initialize(self):
        ## Start Spark Session
        logging.info("Initializing Spark...")
        spark = SparkSession.builder.config(conf=config.PYSPARK_CONFIG).getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        logging.info("Spark session created successfully.")
        self.spark = spark

    def getSpark(self): return self.spark 
