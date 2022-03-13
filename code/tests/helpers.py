from functools import wraps
from playhouse.sqlite_ext import SqliteExtDatabase
from models.product import Product

__all__ = ["create_test_product", "with_test_db"]


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
