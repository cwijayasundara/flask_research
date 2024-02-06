from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bucketlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)


# Create db model for bucket list items
class BucketListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    completion_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add a foreign key for the user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Add a foreign key for the bucket list group (collaboration feature)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)


# Create db model for users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)  # In a real app, you should hash passwords
    email = db.Column(db.String(100), nullable=False, unique=True)
    bucket_list_items = db.relationship('BucketListItem', backref='user', lazy=True)


# Create db model for bucket list groups (for collaboration feature)
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    bucket_list_items = db.relationship('BucketListItem', backref='group', lazy=True)


def create_app():
    with app.app_context():
        db.create_all()
    return app


# Index route
@app.route('/')
def index():
    if "user_id" not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    items = BucketListItem.query.filter_by(user_id=user_id).all()
    return render_template('index.html', items=items)


# Route for adding a new bucket list item
@app.route('/add', methods=['POST'])
def add_item():
    if "user_id" not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    item_name = request.form['name']
    item_description = request.form['description']
    # Format date from string to datetime object
    item_completion_date = datetime.strptime(request.form['completion_date'], '%Y-%m-%d') if request.form[
        'completion_date'] else None
    new_item = BucketListItem(name=item_name, description=item_description, completion_date=item_completion_date,
                              user_id=user_id)
    try:
        db.session.add(new_item)
        db.session.commit()
        flash('Bucket List item added successfully!', 'success')
        return redirect('/')
    except:
        flash('Error! There was a problem adding the item.', 'error')
        return redirect('/')


# Route for editing an existing bucket list item
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    if "user_id" not in session:
        return redirect(url_for('login'))
    item = BucketListItem.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.completion_date = datetime.strptime(request.form['completion_date'], '%Y-%m-%d') if request.form[
            'completion_date'] else None
        try:
            db.session.commit()
            flash('Bucket List item updated successfully!', 'success')
            return redirect('/')
        except:
            flash('Error! There was a problem updating the item.', 'error')
            return redirect('/')
    return render_template('edit.html', item=item)


# Route for deleting a bucket list item
@app.route('/delete/<int:id>')
def delete_item(id):
    if "user_id" not in session:
        return redirect(url_for('login'))
    item = BucketListItem.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Bucket List item deleted successfully!', 'success')
        return redirect('/')
    except:
        flash('Error! There was a problem deleting the item.', 'error')
        return redirect('/')


# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In a real app, you should hash passwords
        email = request.form['email']
        # Check if username or email already exists
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first() is not None
        if user_exists:
            flash('Username or email already exists!', 'error')
            return redirect('/register')
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully! You can now log in.', 'success')
        return redirect('/login')
    return render_template('register.html')


# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect('/')
        else:
            flash('Invalid username or password!', 'error')
    return render_template('login.html')


# Route for user logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect('/login')


if __name__ == '__main__':
    create_app().run(debug=True)
