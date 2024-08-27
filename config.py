import pyspark
import os


NLP_API_ENDPOINT = os.getenv('NLP_API_ENDPOINT', 'http://183.91.3.60:4388/ie/nlp')
PATH_SPECIAL_VERBS = os.getenv('PATH_SPECIAL_VERBS', '/home/huydn74/Documents/legal-information-extraction-main/support_data/danhsachdongtudacbiet.xlsx')

PYSPARK_CONFIG  = (
    pyspark.SparkConf()
    .setAppName('CLS-SRL')
    .setMaster('local[3]')
    .set('spark.driver.memory', '3g')
    .set('spark.executor.memory', '3g')
    .set('spark.sql.execution.arrow.pyspark.enabled', 'true')
)