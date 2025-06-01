
from package.models import User
from app import create_app, db

app = create_app()
app.app_context().push()

def test_user_creation():
    # Teste de criação de usuário
    user = User(username='testuser')
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.check_password('testpass')
    assert not user.check_password('wrongpass')

def test_user_relationships():
    # Teste de relacionamentos
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert len(user.posts) == 0
    assert len(user.likes) == 0

if __name__ == '__main__':
    test_user_creation()
    test_user_relationships()
    print("All user tests passed!")
