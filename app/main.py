from ariadne import ObjectType, QueryType, MutationType, gql, make_executable_schema
from ariadne.asgi import GraphQL
from asgi_lifespan import Lifespan, LifespanMiddleware
from graphqlclient import GraphQLClient

# HTTP request library for access token call
import requests
# .env
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

#import the schema
from app.schema.schema import s3_types
# import resolvers
from app.resolvers.resolvers import resolver_get_csv_from_s3_mapper




def getAuthToken():
    authProvider = os.getenv('AUTH_PROVIDER')
    authDomain = os.getenv('AUTH_DOMAIN')
    authClientId = os.getenv('AUTH_CLIENT_ID')
    authSecret = os.getenv('AUTH_SECRET')
    authIdentifier = os.getenv('AUTH_IDENTIFIER')

    # Short-circuit for 'no-auth' scenario.
    if(authProvider == ''):
        print('Auth provider not set. Aborting token request...')
        return None

    url = ''
    if authProvider == 'keycloak':
        url = f'{authDomain}/auth/realms/{authIdentifier}/protocol/openid-connect/token'
    else:
        url = f'https://{authDomain}/oauth/token'

    payload = {
        'grant_type': 'client_credentials',
        'client_id': authClientId,
        'client_secret': authSecret,
        'audience': authIdentifier
    }

    headers = {'content-type': 'application/x-www-form-urlencoded'}

    r = requests.post(url, data=payload, headers=headers)
    response_data = r.json()
    print("Finished auth token request...")
    return response_data['access_token']


def getClient():

    graphqlClient = None

    # Build as closure to keep scope clean.

    def buildClient(client=graphqlClient):
        # Cached in regular use cases.
        if (client is None):
            print('Building graphql client...')
            token = getAuthToken()
            if (token is None):
                # Short-circuit for 'no-auth' scenario.
                print('Failed to get access token. Abandoning client setup...')
                return None
            url = os.getenv('MAANA_ENDPOINT_URL')
            client = GraphQLClient(url)
            client.inject_token('Bearer '+token)
        return client
    return buildClient()


type_defs = gql(s3_types)
# Map resolver functions to Query fields using QueryType
query = QueryType()

# Resolvers are simple python functions
resolver_get_csv_from_s3_mapper(query)



# Create executable GraphQL schema
schema = make_executable_schema(type_defs, [query])

# --- ASGI app

# Create an ASGI app using the schema, running in debug mode
# Set context with authenticated graphql client.
app = GraphQL(
    schema, debug=True)

# 'Lifespan' is a standalone ASGI app.
# It implements the lifespan protocol,
# and allows registering lifespan event handlers.
lifespan = Lifespan()


@lifespan.on_event("startup")
async def startup():
    print("Starting up...")
    print("... done!")


@lifespan.on_event("shutdown")
async def shutdown():
    print("Shutting down...")
    print("... done!")

# 'LifespanMiddleware' returns an ASGI app.
# It forwards lifespan requests to 'lifespan',
# and anything else goes to 'app'.
app = LifespanMiddleware(app, lifespan=lifespan)
