import boto3, json
from .models import Note, User
# from dotenv import load_dotenv
import os

# comment before pushing
# load_dotenv()
access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

dynamodb = boto3.resource('dynamodb',
                region_name=os.getenv("AWS_DEFAULT_REGION"),
                aws_access_key_id = access_key_id,
                aws_secret_access_key = secret_access_key,
)

client = boto3.client('dynamodb',
                    region_name=os.getenv("AWS_DEFAULT_REGION"),
                    aws_access_key_id = access_key_id,
                    aws_secret_access_key = secret_access_key,
)

s3 = boto3.client('s3',
                region_name=os.getenv("AWS_DEFAULT_REGION"),
                aws_access_key_id = access_key_id,
                aws_secret_access_key = secret_access_key,
)

lambda_client = boto3.client('lambda',
                region_name=os.getenv("AWS_DEFAULT_REGION"),
                aws_access_key_id = access_key_id,
                aws_secret_access_key = secret_access_key,
)


def create_users_table(dynamodb=None):
    # creating table if it doesn't exist
    try:
        client.describe_table(TableName='Users')  
    except client.exceptions.ResourceNotFoundException:

        if not dynamodb:
            dynamodb = boto3.resource('dynamodb',
                        aws_access_key_id = access_key_id,
                        aws_secret_access_key = secret_access_key,
            )        

        table = dynamodb.create_table(
            TableName='Users',
            KeySchema=[
                {
                    'AttributeName': 'email', 
                    'KeyType': 'HASH' # Partition key (primary key)
                } 
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }                                       
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        return table


def create_user_item(email, first_name, password):
    table = dynamodb.Table('Users')
    table.put_item(
        Item = {
            'email': email,
            'firstName': first_name,
            'password': password,
            'notes': {}, # map of notes (maps)
            'images': {} # map of img details (maps)
        }
    )


# lambda function
def create_user_note(email, data, visibility):

    function_name = "create-user-note"
    payload = {
        "email": email,
        "visibility": visibility,
        "data": data
    }
    result = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload)
    )


# lambda function
def create_user_image(email, file_name, visibility):
    
    function_name = "create-user-image"
    payload = {
        "email": email,
        "visibility": visibility,
        "file_name": file_name
    }
    result = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload)
    )


def get_user(email):
    try:
        key = {
            'email':email
        }
        table = dynamodb.Table('Users')
        usr = table.get_item(
            Key = key
        )
        usr = usr['Item']
        # email, password, first_name, notes, images
        user_obj = User(usr['email'], usr['password'], usr['firstName'], usr['notes'], usr['images'])
        return user_obj
    except KeyError:
        return None


def get_all_users():
    table = dynamodb.Table('Users')
    response = table.scan()
    data = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    
    return data


def get_note(email, id):
    user_data = get_user(email)
    notes = user_data.notes
    note = notes[id]
    obj = Note(id, email, user_data.first_name, note['date'], note['data'], note['visibility'])
    return obj

# lambda function
def get_all_notes():

    function_name = "get-all-notes"
    payload = {}
    result = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload)
    )

    notes_list = result['Payload'].read()    
    notes_list = json.loads(notes_list.decode('utf-8')) 
    return notes_list


def delete_user_note(email, note_id):
    key = {
        'email':email
    }
    table = dynamodb.Table('Users')
    query = "REMOVE notes.note" + note_id
    table.update_item(
        TableName = "Users",
        Key = key,
        UpdateExpression = query
    )


# lambda function
def delete_user_image(email, file_name):

    function_name = "delete-s3-image"
    payload = {
        'fileName': file_name
    }
    result = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event',                                      
                Payload=json.dumps(payload)
    )

    key = {
        'email':email
    }
    table = dynamodb.Table('Users')
    name = file_name.split('.')
    name = name[0] + "_" + name[1]
    query = "REMOVE images." + name
    table.update_item(
        TableName = "Users",
        Key = key,
        UpdateExpression = query
    )


def get_url(file_name):
    url = "https://d6ondcb9w3k82.cloudfront.net/" + file_name
    return url


def get_image(email, id):
    user_data = get_user(email)
    images = user_data.images
    file_name = id.split('.')
    file_name = file_name[0] + "_" + file_name[1]
    img = images[file_name]
    img["email"] = email
    img["fileName"] = id
    img["name"] = user_data.first_name
    url = get_url(id)
    img["url"] = url
    return img


# lambda function
def get_all_images():

    function_name = "get-all-images"
    payload = {}
    result = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload)
    )

    image_list = result['Payload'].read()    
    image_list = json.loads(image_list.decode('utf-8')) 
    return image_list

