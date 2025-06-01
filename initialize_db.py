
from app import create_app
from package.models import db, User, Post, Like

app = create_app()

with app.app_context():
    
    db.create_all()

    
    if not User.query.first():
        test_user = User(username='test')
        test_user.set_password('test')
        db.session.add(test_user)
        db.session.commit()
        print("Database initialized with test user!")
    else:
        print("Database already initialized")
