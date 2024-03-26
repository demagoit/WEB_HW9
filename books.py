import configparser
import mongoengine
import json
import datetime

SRC = {
    'authors': 'authors.json',
    'quotes': 'quotes.json'
}

config = configparser.ConfigParser()
config.read('config.ini')

mongo = {
    'user': config.get('CLUSTER', 'USER'),
    'pwd': config.get('CLUSTER', 'PWD'),
    'domain': config.get('CLUSTER', 'DOMAIN'),
    'db_name': config.get('BOOKS', 'DB_NAME')
}

uri = f"mongodb+srv://{mongo['user']}:{mongo['pwd']}@{mongo['domain']}/{mongo['db_name']}?retryWrites=true&w=majority"
mongoengine.connect(host=uri, ssl=True)

class Author(mongoengine.fields.Document):
    born_date = mongoengine.fields.DateField()
    fullname = mongoengine.fields.StringField(required=True, unique_with='born_date')
    born_location = mongoengine.fields.StringField()
    description = mongoengine.fields.StringField()

class Tag(mongoengine.fields.EmbeddedDocument):
     tag = mongoengine.fields.StringField()

class Quote(mongoengine.fields.Document):
      tags = mongoengine.fields.ListField(mongoengine.fields.EmbeddedDocumentField(Tag))
      author  = mongoengine.fields.ReferenceField(Author, dbref=False, required=True)
      quote  = mongoengine.fields.StringField(required=True)

def fill_db():
    with open(SRC['authors'], 'r') as fh:
        auth_json = json.load(fh)

    with open(SRC['quotes'], 'r') as fh:
        qoutes_json = json.load(fh)


    for auth in auth_json:
        fullname = auth['fullname']
        born_date = datetime.datetime.strptime(auth['born_date'], "%B %d, %Y").date()
        born_location = auth['born_location']
        description = auth['description']
        try:
            Author(fullname=fullname, born_date=born_date, born_location=born_location, description=description).save()
        except mongoengine.queryset.NotUniqueError:
            # Author(fullname=fullname, born_date=born_date, born_location=born_location, description=description).update()
            pass

    for qt in qoutes_json:
        tags = [Tag(tag= i) for i in qt['tags']]
        try:
            author = Author.objects.get(fullname=qt['author']).id
        except mongoengine.queryset.DoesNotExist as err:
            print(qt['author'], err)
        except mongoengine.queryset.MultipleObjectsReturned as err:
            author = Author.objects.first(fullname=qt['author']).id

        quote = qt['quote']
        Quote(tags=tags, author=author, quote=quote).save()


def find_name(name) -> list:
    print('find_name function call')
    resp = []
    responce = Author.objects(fullname=name[0])

    if not responce:
        responce = Author.objects(fullname__iregex=f'{name[0]}')
        if not responce:
            resp.append({'Error': f'nothing was fond by name: {name[0]}'})

    auth = {item.id: item.fullname for item in responce}

    for auth_id, auth_name in auth.items():
        quotes = Quote.objects(author=auth_id)
        for item in quotes:
            resp.append({auth_name: item.quote})
    return resp

def find_tag(tag) -> list:
    print('find_tag function call')
    resp = []
    responce = Quote.objects(tags__tag=tag[0])
    
    if not responce:
        responce = Quote.objects(tags__tag__iregex=f'{tag[0]}')
        if not responce:
            resp.append({'Error': f'nothing was fond by tag: {tag[0]}'})
    for item in responce:
        resp.append({item.author.fullname: item.quote})
    return resp

def find_tags(tags) -> list:
    print('find_tags function call')
    resp = []
    responce = Quote.objects(tags__tag__in=tags)
    for item in responce:
        resp.append({item.author.fullname: item.quote})
    return resp

CMD = {
    'name': find_name,
    'tag': find_tag,
    'tags': find_tags
}

if __name__ == '__main__':
    fill_db()

    counter = 0

    while True:
        ui = input('Введить команду у форматі <команда>: <значення>: ')

        if ui.strip().lower() == 'exit':
            break
        
        try:
            com, params = ui.split(':')
            com = com.strip()
            params = params.split(',')
            params = tuple([i.strip() for i in params])
        except Exception as err:
            print(err)

        func = CMD[com]
        resp = func(params)

        for item in resp:
            for key, value in item.items():
                print(f'{key}: {value}')
