#!/usr/bin/env python

from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Collection, Disc, User

from flask import session as login_session
import random
import string
import httplib2
import json
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Disc Golf Disc Collections Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///discgolfcollections.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        flash("%s has been successfully logged out." %
              login_session['username'])
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        del login_session['gplus_id']
        del login_session['access_token']
        return redirect(url_for('showCollections'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Show all disc collections
@app.route('/')
@app.route('/discgolf/')
def showCollections():
    collections = session.query(Collection)
    return render_template('collections.html', collections=collections,
                           login_session=login_session)


# Create a new collection
@app.route('/discgolf/new/', methods=['GET', 'POST'])
def newCollection():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCollection = Collection(name=request.form['name'],
                                   user_id=login_session['user_id'])
        session.add(newCollection)
        session.commit()
        flash("New Collection: %s created." % newCollection.name)
        return redirect(url_for('showCollections'))
    else:
        return render_template('newCollection.html')


# Show a collection
@app.route('/discgolf/<int:collection_id>/')
@app.route('/discgolf/<int:collection_id>/collection/')
def showCollection(collection_id):
    discs = session.query(Disc).filter_by(collection_id=collection_id)
    collection = session.query(Collection).filter_by(id=collection_id).one()
    creator = getUserInfo(collection.user_id)
    discTypes = []
    for disc in discs:
        discTypes.append(disc.discType)
    return render_template('discCollection.html', discs=discs,
                           collection=collection, discTypes=discTypes,
                           creator=creator, login_session=login_session)


# Edit a collection
@app.route('/discgolf/<int:collection_id>/edit/', methods=['GET', 'POST'])
def editCollection(collection_id):
    editedCollection = session.query(Collection).filter_by(
        id=collection_id).one()
    output = ""
    if 'username' not in login_session:
        return redirect('/login')
    if editedCollection.user_id != login_session['user_id']:
        output += "<script>function myFunction() {alert("
        output += "'You are not authorized to edit this collection.'"
        output += ");}</script><body onload='myFunction()'>"
        return output
    if request.method == 'POST':
        if 'update' in request.form:
            editedCollection.name = request.form['newName']
            session.add(editedCollection)
            session.commit()
            flash("Collection name updated.")
            return redirect(url_for('showCollection',
                                    collection_id=collection_id))
    else:
        return render_template('editCollection.html',
                               collection=editedCollection)


# Delete a collection
@app.route('/discgolf/<int:collection_id>/delete/', methods=['GET', 'POST'])
def deleteCollection(collection_id):
    deletedCollection = session.query(Collection).filter_by(
        id=collection_id).one()
    deletedDiscs = session.query(Disc).filter_by(
        collection_id=collection_id).all()
    output = ""
    if 'username' not in login_session:
        return redirect('/login')
    if deletedCollection.user_id != login_session['user_id']:
        output += "<script>function myFunction() {alert("
        output += "'You are not authorized to delete this collection.'"
        output += ");}</script><body onload='myFunction()'>"
        return output
    if request.method == 'POST':
        session.delete(deletedCollection)
        session.commit()
        for disc in deletedDiscs:
            session.delete(disc)
            session.commit()
        flash("Collection '%s' deleted." % deletedCollection.name)
        return redirect(url_for('showCollections'))
    else:
        return render_template('deleteCollection.html',
                               collection=deletedCollection)


# Add a disc to a collection
@app.route('/discgolf/<int:collection_id>/collection/new/',
           methods=['GET', 'POST'])
def newDisc(collection_id):
    collection = session.query(Collection).filter_by(id=collection_id).one()
    output = ""
    if 'username' not in login_session:
        return redirect('/login')
    if collection.user_id != login_session['user_id']:
        output += "<script>function myFunction() {alert("
        output += "'You are not authorized to add a disc to this collection.'"
        output += ");}</script><body onload='myFunction()'>"
        return output
    if request.method == 'POST':
        newDisc = Disc(collection_id=collection_id,
                       discType=request.form['discType'],
                       mfr=request.form['mfr'],
                       name=request.form['name'],
                       plastic=request.form['plastic'],
                       color=request.form['color'],
                       weight=request.form['weight'],
                       user_id=login_session['user_id'])
        session.add(newDisc)
        session.commit()
        flash("Your new %s has been added to your collection." % newDisc.name)
        return redirect(url_for('showCollection',
                                collection_id=collection_id))
    else:
        return render_template('addDisc.html', collection=collection)


# Edit a disc in a collection
@app.route('/discgolf/<int:collection_id>/collection/<int:disc_id>/edit/',
           methods=['GET', 'POST'])
def editDisc(collection_id, disc_id):
    collection = session.query(Collection).filter_by(id=collection_id).one()
    editedDisc = session.query(Disc).filter_by(id=disc_id).one()
    output = ""
    if 'username' not in login_session:
        return redirect('/login')
    if editedDisc.user_id != login_session['user_id']:
        output += "<script>function myFunction() {alert("
        output += "'You are not authorized to edit a disc in this collection.'"
        output += ");}</script><body onload='myFunction()'>"
        return output
    if request.method == 'POST':
        if request.form['mfr']:
            editedDisc.mfr = request.form['mfr']
        elif request.form['name']:
            editedDisc.name = request.form['name']
        elif request.form['plastic']:
            editedDisc.plastic = request.form['plastic']
        elif request.form['color']:
            editedDisc.color = request.form['color']
        elif request.form['weight']:
            editedDisc.weight = request.form['weight']
        session.add(editedDisc)
        session.commit()
        flash("Your disc has been updated")
        return redirect(url_for('showCollection', collection_id=collection_id))
    else:
        return render_template('editDisc.html', collection=collection,
                               disc=editedDisc)


# Delete a disc in a collection
@app.route('/discgolf/<int:collection_id>/collection/<int:disc_id>/delete/',
           methods=['GET', 'POST'])
def deleteDisc(collection_id, disc_id):
    deletedDisc = session.query(Disc).filter_by(id=disc_id).one()
    output = ""
    if 'username' not in login_session:
        return redirect('/login')
    if deletedDisc.user_id != login_session['user_id']:
        output += "<script>function myFunction() {alert("
        output += "'You are not authorized to delete a disc from this "
        output += "collection.'"
        output += ");}</script><body onload='myFunction()'>"
        return output
    if request.method == 'POST':
        session.delete(deletedDisc)
        session.commit()
        flash("Your %s has been deleted from your collection." %
              deletedDisc.name)
        return redirect(url_for('showCollection', collection_id=collection_id))
    else:
        return render_template('deleteDisc.html', disc=deletedDisc,
                               collection_id=collection_id)


# API Requests

# returns a list of collections
@app.route('/discgolf/JSON/')
def collectionsJSON():
    collections = session.query(Collection).all()
    return jsonify(Collections=[c.serialize for c in collections])


# returns all discs in a collection
@app.route('/discgolf/<int:collection_id>/collection/JSON/')
def collectionJSON(collection_id):
    collection = session.query(Collection).filter_by(id=collection_id).one()
    discs = session.query(Disc).filter_by(collection_id=collection.id).all()
    return jsonify(Discs=[disc.serialize for disc in discs])


# returns a single disc
@app.route('/discgolf/<int:collection_id>/collection/<int:disc_id>/JSON/')
def discJSON(collection_id, disc_id):
    disc = session.query(Disc).filter_by(id=disc_id).one()
    return jsonify(Disc=[disc.serialize])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
