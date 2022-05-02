from datetime import datetime
from functools import wraps
from playhouse.sqlite_ext import SqliteExtDatabase
from models.admin_user import AdminUser
from models.order import Order
from models.product import Product

__all__ = [
    "create_test_product",
    "create_test_admin_user",
    "create_test_order",
    "mock_send_confirmation_email_delay",
    "with_test_db",
]


def with_test_db(dbs: tuple):
    def decorator(func):
        @wraps(func)
        def test_db_closure(*args, **kwargs):
            test_db = SqliteExtDatabase(":memory:")
            with test_db.bind_ctx(dbs):
                test_db.create_tables(dbs)
                try:
                    func(*args, **kwargs)
                finally:
                    test_db.drop_tables(dbs)
                    test_db.close()

        return test_db_closure

    return decorator


def create_test_product(name: str, price: str):
    p = Product()
    p.name = name
    p.price = price
    p.save()

    return p


def create_test_admin_user(username: str, password: str):
    from werkzeug.security import generate_password_hash

    u = AdminUser()
    u.username = username
    u.password = generate_password_hash(password)
    u.save()

    return u


def create_test_order(email: str, products: dict):
    o = Order()
    o.email = email
    o.timestamp_created = datetime.now().format("%Y-%m-%d %H:%M:%S")
    o.products = products
    o.save()

    return o


def mock_send_confirmation_email_delay(mocker):
    from tasks.send_email import send_confirmation_email

    mocker.patch.object(send_confirmation_email, "delay", autospec=True)
