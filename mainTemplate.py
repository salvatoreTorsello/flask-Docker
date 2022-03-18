from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import pymysql 
import credentials

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(credentials.dbuser, credentials.dbpass, credentials.dbhost, credentials.dbname)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CHESOGNO'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SQLALCHEMY_DATABASE_URI'] = conn
db = SQLAlchemy(app)

class Product(db.Model):
	_PN 			= db.Column("PN" ,db.String(15), primary_key=True)
	lastHWRevision 	= db.Column("Last HW Revision", db.DateTime)
	lastSWRevision 	= db.Column("Last SW Revision", db.DateTime)
	linkHWFiles		= db.Column("Link HW Files", db.String(200))
	linkSWFiles		= db.Column("Link SW Files", db.String(200))

	def __init__(self, lastHWRevision, lastSWRevision, linkHWFiles, linkSWFiles):
		self.lastHWRevision = lastHWRevision
		self.lastSWRevision = lastSWRevision
		self.linkHWFiles 	= linkHWFiles
		self.linkSWFiles 	= linkSWFiles
	
	def to_dict(self):
		return {
            '_PN'			: self._PN,
            'lastHWRevision': self.lastHWRevision,
            'lastSWRevision': self.lastSWRevision,
            'linkHWFiles'	: self.linkHWFiles,
            'linkSWFiles'	: self.linkSWFiles
        }

class Component(db.Model):
	_PN 			= db.Column("PN" ,db.String(15), primary_key=True)
	manufacturer	= db.Column("Manufacturer", db.String(15))
	seller 			= db.Column("Seller", db.String(15))
	link 			= db.Column("Link", db.String(200))
	store 			= db.Column("Store", db.Integer)
	lastOrder 		= db.Column("Last Order", db.DateTime)

	def __init__(self, manufacturer, seller, link, store, lastBuy):
		self.manufacturer 	= manufacturer
		self.seller 		= seller
		self.link 			= link	
		self.store			= store
		self.lastBuy 		= lastBuy

class Operation(db.Model):
	_id 			= db.Column("ID" ,db.String(15), primary_key=True)
	type			= db.Column("Type", db.String(15))
	date 			= db.Column("Date", db.DateTime)
	user 			= db.Column("User", db.String(200))
	def __init__(self, type, date, user):
		self.type	= type
		self.date 	= date
		self.user 	= user


@app.route("/")
def home():
	return render_template("starter.html")

@app.route("/products")
def products():
	return render_template("view_products.html", title="Products List")

@app.route('/api/data')
def data():
    query = Product.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Product._PN.like(f'%{search}%'),
            Product.lastHWRevision.like(f'%{search}%'),
			Product.lastSWRevision.like(f'%{search}%')
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['_PN', 'lastHWRevision', 'lastSWRevision']:
            col_name = '_PN'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Product, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Product.query.count(),
        'draw': request.args.get('draw', type=int),
    }


if __name__ == "__main__":	
	db.create_all()
	app.debug = True
	app.run(host="0.0.0.0")