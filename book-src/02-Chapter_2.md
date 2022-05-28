# Chapter 2
## Using Peewee with a Database
Peewee is a library often referred to as an Object Relational Mapper (ORM). It abstracts connections to a database into regular Python objects to make querying integrate seamlessly with the rest of your backend logic.

If you'd like a detailed look into Peewee _before_ diving in, check out [Appendix 1](#appendix-1---peewee).

### Making a database
We're going to be using SQLite in this book, because it doesn't require any installation or set-up. As Peewee is an abstraction layer, code from this book should work fine with a more dedicated solution, such as MySQL or Postgres. 


Let's begin by creating a folder in the root directory called `models`, and inside add two files - `__init__.py` and `product.py`.

`__init__.py`:

```python
from peewee import Model
from playhouse.sqlite_ext import SqliteExtDatabase


class BaseModel(Model):
    class Meta:
        database = SqliteExtDatabase("database.db")
``` 
---
`product.py`:

```python
from models import BaseModel
from playhouse.sqlite_ext import *


class Product(BaseModel):
    id = AutoField()
    name = TextField()
    price = TextField()

    class Meta:
        table_name = "product"
```

In our init file we import Peewee's own `Model` class and its class for connecting to a Sqlite database. Using these we can define a `BaseModel` class which will act as a parent class for each of our models. Inside this class, we include another named `Meta` which is used by Peewee to point the models to their database. As we are using Sqlite for this book, we can simply point this to a file named `database.db`. 

Our `Product` model imports our new `BaseModel` class and inherits from it. The column datatypes from Peewee's Sqlite extension are also brought in. 

Models are linked to their database columns by providing class attribues which are instances of Peewee's column types. Here we have an `AutoField` - used to denote a primary key - and two `TextField`s to store each product's name and price. 

Another `Meta` subclass is used on our `Product` model to indicate its table name in the Sqlite database.

Speaking of which, let's get this prepared now.

#### Database Migrations

Create a new folder in the root of your project called `migrations`. Create a file in here called `V1__create_product_table.sql`. 

```sql
create table product (id integer primary key autoincrement, name text, price text);

insert into product values (1, "Toothpaste", "2.0"), (2, "Toothbrush", "1.50"), (3, "Floss", "0.99");
```

Great, now we have our first database migration! You may be wondering about that file name, so I shall explain. This naming schema is used by a product named FlywayDB, an open source generic database migration tool. By naming our migrations as such, we have the option to use this tool to handle our database if we want. Since Flyway uses plain SQL files to handle its migrations, it is possible to run our migrations manually if you would prefer not to set this tool up. 

##### Setting up Flyway

Search the web for FlywayDB's download page and grab the relevant version for your operating system. Make sure to extract the folder inside your project's root directory. Rename the extracted folder, which should be `flyway-x.y.z` to just `flyway` for simplicity.

Inside the `flyway` folder you should have another named `conf`, containing a file `flyway.conf`. Open up this file and remove the default contents, then enter the following:

```
flyway.url=jdbc:sqlite:database.db
flyway.user=
flyway.password=
flyway.locations=migrations
```

Just one more thing before we can start using `flyway` - the first migration it finds is expected to be the "baseline" of the table, which means its initial state before any flyway migrations. If we run flyway now, it will assume this is V1 and not create our table, so we need to create an empry file inside the `migrations` folder called `V0__baseline.sql`.

We are now ready! Make sure you are in the project root and run the following command:

```bash
flyway/flyway migrate
```

If successful, you should see some confirmation output like the following:

```
Flyway is up to date
Flyway Community Edition 8.5.2 by Redgate
See what's new here: https://flywaydb.org/documentation/learnmore/releaseNotes#8.5.2

Database: jdbc:sqlite:database.db (SQLite 3.34)
Successfully validated 2 migrations (execution time 00:00.006s)
Creating Schema History table "main"."flyway_schema_history" ...
Current version of schema "main": << Empty Schema >>
Migrating schema "main" to version "0 - baseline"
Migrating schema "main" to version "1 - create product table"
Successfully applied 2 migrations to schema "main", now at version v1 (execution time 00:00.014s)
```

Congratulations, you now have a database!

##### Skipping Flyway and Running Migrations Manually
If you'd prefer to skip setting up Flyway, you can run the sqlite migrations from the command line directly.

First execute the `sqlite3 database.db` command to drop into a sqlite shell for your database. Then run each file like so:

```sqlite
.read migrations/Vx__name_of_file.sql
```

If you receive an error about the `sqlite3` command not being found, you may need to install it on your computer first.

### Using our Database
Now that our database exists, and has contents, we can begin using our Peewee models in our Flask endpoints.

Open up `web_server.py` and change your two routes to the following:

```python
@app.route("/")
def index():
    products = Product.select()
    return render_template("index.html", products=products)


@app.route("/<string:product_name>")
def view_product(product_name):
    product = Product.get_or_none(Product.name == product_name)

    if not product:
        return abort(404)

    return render_template(
        "products/view_product.html", price=product.price, product_name=product_name
    )
```

We'll also need to import our `Product` model at the top:

```python
from models.product import Product
```

If you are familiar with SQL syntax, Peewee's methods should feel familiar. We use `Product.select()` to grab all product records from our database - the equivalent of `SELECT * FROM product`. This returns an `iterable` of objects representing our database rows, with each class attribute we defined in `models/product.py` containing the data from our row.

In our `view_product` endpoint we need to fetch a specific row, so we use Peewee's `get_or_none` function. This function needs to be supplied with any conditions on which to select the correct product. Since we have the product's name as our `product_name` variable, we pass this as a condition to Peewee with `Product.name == product_name`. This tells Peewee's query to find a row with a `name` record matching what's in our `product_name` variable. This is the equivalent of `SELECT * from product WHERE name = product_name` (and "product_name" is actually the contents of the variable). 

Since the `get_or_none` method returns `None` if no matching record is found, we can use this to return our `abort(404)` if a non-existing product name is passed.

The arguments to `render_template` update to pass the `product` variable's `price` attribute to the `price` context.

Our templates won't quite render yet, since they are expecting `dict`s for the product information. Let's start with `index.html`, change the contents of your `table` to the following:

```html
<table>
    {% for product in products %}
    <tr>
        <td><a href="/{{product.name}}">{{product.name}}</a></td>
        <td>{{ "£%.2f"|format(product.price|float) }}</td>
    </tr>
    {% endfor %}
</table>
```
We are now iterating over python objects representing our database rows, rather than `dict`s, so we no longer need `.items()`, and can use the dot syntax to access attributes.

Since `price` is a String in our database, it must be passed to the `float` filter before it can be formatted via the `format` filter.

And now in `view_product.html`:

```html
<h2>{{product_name}}</h2>

<p>This product costs £{{"%.2f"|format(price|float)}}</p>

<p>Out of Stock</p>
```

Just the `price` to be converted to a `float` once again in this file.

With all of those changes in place, you can now run your webserver with `python3 web_server.py` and visit your shop once again. It should work exactly as before.

That's all it takes to get a database into our site! Before we start adding functionality, we should first go over  way to ensure our site will always work as intended. This leads us nicely to our last titular module - Pytest.
