from flask_restful import Resource, reqparse
from flask_jwt import  jwt_required
#from models.item import ItemModel
import sqlite3


"""
The following resources contain endpoints that are protected by jwt,
one may need a valid access token, a valid fresh token or a valid token with authorized privilege 
to access each endpoint, details can be found in the README.md doc.  
"""


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                type=float,
                required=True, 
                help='This fiel cannot be left blank!'
        )
        
    @jwt_required()
    def get(self, name):
        item =self.find_by_name(name)
        if item:
            return item
        return {'message':'Item not found'}, 404
    
    @classmethod
    def find_by_name(cls,name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM items WHERE name=?"
        result= cursor.execute(query, (name,))
        row = result.fetchone()

        connection.close()

        if row:
            return{'item': {'name':row[0], 'price': row[1]}}
        
    
    def post(self, name):
        
        if self.find_by_name(name) :
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()
        
        item ={'name': name, 'price': data['price']}
        
        try:
            self.insert(item)
        except:
            return {"message": "An error occurred inserting the item"}, 500 #internal server error

        return item, 201
    
    def delete(self,name):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE NAME=?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()

        return {'message': 'item deleted'}
    @classmethod
    def insert(cls,item):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()


        query = "INSERT INTO items VALUES (?,?)"
        cursor.execute(query, (item['name'], item['price']))

        connection.commit()
        connection.close()

       


    def put(self, name):
        
        data = Item.parser.parse_args()
        
        item = self.find_by_name(name)
        updated_item = {'name': name, 'price': data['price']}

        if item is None:
            try:
                self.insert(updated_item)
            except:
                return {"Message": "An error ocurred inserting the item"}, 500
        else:
            try:
                self.update(updated_item)
            except:
                return {"message": "An error ocurred updating the item,"}, 500
        return item
    
    @classmethod
    def update(cls,item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()


        query = "UPDATE items SET PRICE=? WHERE name=?"
        cursor.execute(query, (item['price'], item['name']))

        connection.commit()
        connection.close()



class ItemList(Resource):
    def get(self):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()


        query = "SELECT * FROM items"
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({'name':row[0], 'price': row[1]})

        
        connection.close()

        return {'items': items}
