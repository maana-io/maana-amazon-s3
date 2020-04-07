s3_types = """
type Query { 
  readNumericCSVFromAmazonS3(bucket: BucketAsInput!): CSVOutput
}

type Bucket {
  id: ID!
  name: String!
  path: String!
}

input BucketAsInput {
  id: ID!
  file: String!
}

type Row {
  id: ID!
  values: [Value]
}

type Value {
  id: ID!
  value: Float
}

type CSVOutput {
  id: ID!
  rows: [Row]
}

scalar Date

scalar DateTime

scalar Time



"""