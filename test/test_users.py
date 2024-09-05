from starlette import status

from routers.users import get_db, get_current_user
from test.utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/user/get-user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "admin1@email.com"
    assert response.json()["first_name"] == "John"
    assert response.json()["last_name"] == "Doe"
    assert response.json()["role"] == "admin"
    assert response.json()["phone_number"] == "+5555555555"


def test_change_password_success(test_user):
    response = client.put("/user/change-password/", json={"password": "testpassword",
                                                          "new_password": "testnewpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/change-password/", json={"password": "wrongpassword",
                                                          "new_password": "testnewpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid password"}


def test_update_phone_number(test_user):
    response = client.put("/user/update-phone-number?phone_number=1234567890")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(PrivateUsers).filter(PrivateUsers.id == 1).first()
    assert model.phone_number == "1234567890"
