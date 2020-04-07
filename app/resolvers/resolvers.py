# imports
import numpy as np
import sys
import boto3
import os
import pandas as pd

from dotenv import load_dotenv
import os
from io import StringIO # Python 3.x
# Load environment variables
load_dotenv()

# mappings

#readNumericCSVFromAmazonS3(bucket: BucketAsInput!): CSVOutput
def resolver_get_csv_from_s3_mapper(query):
    query.set_field("readNumericCSVFromAmazonS3", resolver_get_csv_from_s3)


# resolvers

def resolver_get_csv_from_s3(*_, bucket):
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    # setup S3 client

  
    s3 = boto3.client('s3',aws_access_key_id=access_key,aws_secret_access_key=secret)
    bucket_name = bucket['id']
    object_key = bucket['file']
	#read objects from bukcets
    csv_obj = s3.get_object(Bucket=bucket_name, Key=object_key)
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')
    data = pd.read_csv(StringIO(csv_string))

    #removes any fake lines
    data = data.dropna(how='all')
    data = data.reset_index(drop=True)

    columnsNamesArr = data.columns.values
    listOfColumnNames = list(columnsNamesArr)
    rows = []
    # each rows set of values

    for index, row in data.iterrows():
        rows.append(row)

    rowsToOutput = []
    for i in range(len(rows)):
        # gets the number for the id of the row
        #print(rows[i][0])
        values = []
        for j in range(len(listOfColumnNames)):

            if j != 0:
                value = {
                    "id": listOfColumnNames[j],
                    "value": rows[i][j]
                }
                values.append(value)
        row = {
            "id": rows[i][0],
            "values": values
        }
        rowsToOutput.append(row)

    return {
        "id": bucket['id'],
        "rows": rowsToOutput
    }



