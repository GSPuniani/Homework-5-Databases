from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

plants_collection = mongo.db.plants
harvests_collection = mongo.db.harvests

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""

    # Database call to retrieve *all* plants from the Mongo database's `plants` collection.
    plants_data = plants_collection.find({})

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        # Store the new plant's name, variety, photo, & date planted in the object below.
        new_plant = {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted')
        }
        # Make an `insert_one` database call to insert the object into the database's `plants` collection
        created_plant = plants_collection.insert_one(new_plant)

        # Pass the inserted id into the redirect call below.
        return redirect(url_for('detail', plant_id=created_plant.inserted_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    # Database call to retrieve *one* plant from the database, whose id matches the id passed in via the URL.
    plant_to_show = plants_collection.find_one({'_id': ObjectId(plant_id)})

    # Find all harvests for the plant's id.
    harvests = harvests_collection.find({'_id': ObjectId(plant_id)})

    context = {
        'plant': plant_to_show,
        'harvests': harvests
    }

    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    # Create a new harvest object by passing in the form data from the detail page form.
    new_harvest = {
        'quantity': request.form.get('harvested_amount'), 
        'date': request.form.get('date_planted'),
        'plant_id': plant_id
    }

    # Insert the object into the `harvests` collection of the database.
    harvests_collection.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        # Make an `update_one` database call to update the plant with the given id
        plants_collection.update_one({
            '_id': ObjectId(plant_id)
        }, 
        {'$set': {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted')
        }})

        
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        # Make a `find_one` database call to get the plant object with the passed-in _id.
        plant_to_show = plants_collection.find_one({'_id': ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    # Make a `delete_one` database call to delete the plant with the given id.
    plants_collection.delete_one({'_id': ObjectId(plant_id)})

    # Make a `delete_many` database call to delete all harvests with the given plant id.
    harvests_collection.delete_many({'plant_id': plant_id})

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)

