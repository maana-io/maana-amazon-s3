
# usage

AWS keys need to be placed in the .env file in app folder to allow connection to S3.

bucket id = the bucket name
file: path to the file within the bucker 

# query
query{
  readNumericCSVFromAmazonS3(
    bucket: {
      id: "mikectestbucket2020"
      file: "testData.csv"
  
  }
  ){
    id
    rows {
      id
      values{
        id
        value
        
      }
     
      
    }
  }
}