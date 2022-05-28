# Chapter 4
## Adding Admin Controls
Database migrations are typically used to control the structure of your database tables, rather than their content. Our initial migration added three products only to get us back to the same point we were at before, when our data was in dictionaries. If we want to continue adding products, we should build some way to do it within the application itself.

In order to achieve this, we will now create a separate section of our shop which will serve as an admin panel. We will gate this section behind a login system, as here users will be able to add / remove products from our shop, and change their prices. 

We will start by creating two new pages on our site - `/admin` for the admin section, and `/admin/login` for an admin user to log in.

Following the current conventions of our code, you may think that these routes would go in the `web_server.py` file, since that's where our other pages are held. However, as our application grows, this file will become much too big. As well as this, our admin URLs will always want to begin with `/admin/` to denote that they are separate from the main site, and will all want to be kept behind a login system. It would be rather easy to forget either of these things, and risk exposing admin capabilities to the public. 

Luckily, Flask provides a solution to both of these matters - Blueprints. A Flask Blueprint is a way of grouping together sections of a website under a common name. These sections can all contain a common URL prefix, and can have guards implemented before a request completes. We can use these two features to ensure that all of our admin functionality lives at `/admin/*` and is behind a login system.

Let's begin by creating a folder in the root of our project called `web`. This will serve as the store for all things related to the web interface for our shop. Inside this folder create two more - `views` and `blueprints`. Inside `blueprints` create an `__init__.py` file:

```python
from flask import Blueprint

site_blueprint = Blueprint("site", __name__)
admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")
```

We import the `Blueprints` class from `flask` and create two instances, `site_blueprint` and `admin_blueprint`. The first argument will be the name of the blueprint, which you will see used later when we use Flask's `url_for` helper. The second argument is `__name__` by convention. Our admin blueprint has a third argument, `url_prefix`. This is used to ensure that all URLs for this blueprint begin with `/admin/` automatically.

Let's create some placeholder routes for our admin section. We'll start with an index and a login page. Inside your `web/views` folder, create two more - `site` and `admin`. This is where our URL routes will lie (Flask calls them "views", but personally I think the term "routes" is clearer. I will stick with Flask's terminology for our project, however).

Inside both `site` and `admin` create a file named `__init__.py`. This is where our guards will live. The public site needs no guards, but the admin will need to make sure a user is logged in before displaying a page.

Inside your new `admin` folder create a file named `admin.py` containing the following:

```python
from web.blueprints import admin_blueprint


@admin_blueprint.route("/")
def admin_index():
    return "Welcome to the admin"


@admin_blueprint.route("/login", methods=["GET", "POST"])
def admin_login():
    return "please log in"
```

Here are our two placeholder views. As you can see, blueprints have routes added to them using the same decorator syntax as we have in our `web_server.py` file. We create a function named `admin_index` which serves as the entry-point to our admin section. The route `"/"` will combine with the `url_prefix` we specified on the Blueprint so that this page rests on `/admin`.  Similarly, our `admin_login` route will be `/admin/login`. 

Our login route has the `methods` argument passed to its decorator. This allows this route to be accessed by both GET and POST HTTP methods. When this argument is not provided, Flask assumes the route is meant only for GET requests, and any POST requests will be responded to with a 405 Method Not Allowed. 

Our admin views are now in place, but before we flesh them out, let's also pull our site routes out of `web_server.py` and into our new `site` folder.

Create a file at `web/views/site/site.py` and move over your views from `web_server.py`. Import `site_blueprint` at the top, and change the decorators from `@app` to `@site_blueprint`:

```python
from flask import abort, render_template

from models.product import Product
from web.blueprints import site_blueprint


@site_blueprint.route("/")
def index():
    products = Product.select()
    return render_template("index.html", products=products)


@site_blueprint.route("/<string:product_name>")
def view_product(product_name):
    product = Product.get_or_none(Product.name == product_name)

    if not product:
        return abort(404)

    return render_template(
        "products/view_product.html", price=product.price, product_name=product_name
    )
```

Great, now all of our views are in place. To avoid long chains of imports, let's consolidate our modules. Open up `web/views/site/__init__.py` and add this:

```python
from . import site
```

Now do the same in `web/views/admin/__init__.py`:

```python
from . import admin
```

Finally, create `web/views/__init__.py` and add this:

```python
from . import admin, site
```

Now our views are ready to be imported in `web_server.py`. Open that up and change it to the following:

```python
from flask import Flask

app = Flask(__name__)
app.secret_key = "very secret"

from web.views import admin, site
from web.blueprints import site_blueprint, admin_blueprint

app.register_blueprint(site_blueprint)
app.register_blueprint(admin_blueprint)


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
```
Now, after creating our `app` we pull in all of our views from both the `admin` and `site` sections. This causes our Blueprints to "fill up" with the required routes. Now we pull in said Blueprints and use `app.register_blueprint` to tell our main Flask app that they exist.

That's it, this file is now much cleaner, and our code has become modularised. We can now keep a nice separation between the public shop and the private admin section.

Speaking of which, let's go add that guard to our admin

### Route Guards in Flask
As well as `route`, Flask Blueprints have access to other decorators which can modify the lifecycle of a web request. One such example is `before_request`, which is used to perform logic before a web request is passed to our view. We can use this to check if a user is logged in when they try to access `/admin`, and redirect them to our login page if not.

Before we change our code, open up a browser and go to `localhost:5000/admin`. You should see our "Welcome to the admin" placeholder message. This means you have successfully navigated to our admin section without authenticating.

Now open up `web/views/admin/__init__.py` and add the following:

```python
from flask import request, session, redirect, url_for

from web.blueprints import admin_blueprint

from . import admin


@admin_blueprint.before_request
def admin_before_request():
    if request.endpoint != "admin.admin_login":
        if "logged_in" not in session:
            return redirect(url_for("admin.admin_login"))
```

We pull in a couple of helpers from Flask, as well as our `admin_blueprint`, then define a function under `@admin_blueprint.before_request`. This function checks Flask's `request` object to see if the `endpoint` attribute is anything other than `admin.admin_login`. If it is, and there is not a flag called `"logged_in"` in Flask's `session`, we force a redirect to the `admin.admin_login` endpoint. 

Don't worry about the endpoint naming, or Flask's `session`, just yet. We will cover them shortly.

Now save this file and try once again to get to `localhost:5000/admin`. You should hopefully be redirected to `/admin/login`, and see a different placeholder message. This means our admin section is protected against unauthenticated users!

### Adding an Admin
Now that our page is guarded, we need to get ourselves a user so that we can unlock it. To achieve this we'll need a new database table - `admin_users`. Create a new file in the `migrations` folder called `V2__add_admin_user_table.sql`:

```sql
CREATE TABLE admin_user (id integer primary key autoincrement, username text, password text);
```
Run the `flyway/flyway migrate` command in your project root folder and you will now have a second table. Time for our Peewee model. Create `models/admin_user.py`:

```python
from models import BaseModel
from playhouse.sqlite_ext import *


class AdminUser(BaseModel):
    id = AutoField()
    username = TextField()
    password = TextField()

    class Meta:
        table_name = "admin_user"
```

Much like our `Product` class, the `AdminUser` contains an `id` field and two `text` fields. 

Now we need an admin user, but as previously mentioned, it's best to just use migrations for table structure, and not data. So, let's use the Python interactive shell to make us our first admin user. Open a terminal in the root of your project, ensure your virtualenv is sourced, and run `python3`.

First we'll create an `AdminUser` and assign them a username. I will use "admin", but you can use whatever name you'd like.

```
Python 3.10.0 (default, Oct  4 2021, 00:00:00) [GCC 11.2.1 20210728 (Red Hat 11.2.1-1)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from models.admin_user import AdminUser
>>> user = AdminUser()
>>> user.username = "admin"
```

Now our user needs a password. Since it's bad security practise to store password in plain-text, we will store our password as a hash. Flask itself is built upon a library known as `werkzeug` which provides functions for securely hashing and checking passwords. For example, to hash the password "admin":

```
>>> from werkzeug.security import generate_password_hash
>>> generate_password_hash('admin')
'pbkdf2:sha256:260000$aOwDEpVMd5aO0oie$2916af44ac8b1e79d8a1ac74882f1602da2bae33fc690491c5014fe98f186ed4'
```

Pick a nice password for your admin user, and set the hash of this password as the `AdminUser`'s `password` attribute:

```
>>> user.password = generate_password_hash("admin")
```

Now we can write this row to our database with `save()`:

```
>>> user.save()
1
```

And we can confirm the record is now in our database:

```
>>> u = AdminUser.get()
>>> u.username
'admin'
>>> u.password
'pbkdf2:sha256:260000$O0eSD3qnpfXpqVYn$4ca214264ba24b66ffc01b5ec801d50314439f24e947df03d4f763d4a58e5704'
>>> 
```

#### Logging in

With an admin user created, we can now create a simple login screen and update our view accordingly. Create a folder named `admin` in your `templates` folder, then create two files inside of it - `login.html` and `index.html`.

Let's start with our login form, so open up `login.html`:

```html
<h1>Log in</h1>

{% for msg in get_flashed_messages() %}
    <h2 style="color:red">{{msg}}</h2>
{% endfor %}

<hr />

<form name="login_form" method="POST">
    <label for="username">Username</label>
    <input type="text" name="username" id="username">

    <br />
    <br />

    <label for="password">Password</label>
    <input type="password" name="password" id="password">

    <br />
    <br />

    <input type="submit" value="Log In">
</form>
```

This is mostly a standard HTML form. At the top you will notice a call to `get_flashed_messages`. Flash messages are simply a short message which should be viewed only once by the user. They are typically used to convey the success or failure of a single action. We use a `style` attribute to colour ours red, since it will only show when the login attempt is unsuccessful.

Now we have the template, let's get our view rendering it. Open up `web/views/admin/admin.py`:

```python
from flask import request, session, redirect, url_for, render_template, flash
from werkzeug.security import check_password_hash

from models.admin_user import AdminUser
from web.blueprints import admin_blueprint


@admin_blueprint.route("/")
def admin_index():
    return render_template("admin/index.html")


@admin_blueprint.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = AdminUser.get_or_none(AdminUser.username == username)
        if user:
            password_correct = check_password_hash(user.password, password)

            if password_correct:
                session["logged_in"] = True
                session["admin_user_id"] = user.id

                return redirect(url_for("admin.admin_index"))
            else:
                flash("Please try again!")
        else:
            flash("Please try again")



    return render_template("admin/login.html")
```

We add a couple of new imports from `flask`, our old friend `render_template` and the new `flash` function to display the aforementioned flash messages.

The `check_password_hash` function is brought in from `werkzeug` so that we can test the password hash from our new `AdminUser` instance. 

Our `admin_index` function is changed to render a template rather than returning a string.

The `admin_login` route is now fully fleshed-out. We begin by checking the `method` of our `request` object so that we can tell whether we are on the initial page-load (a GET request) or if we have the data from our form submitted (a POST request). If we have a POST request, we use the `form` attribute of our `request` object to extract the POSTed data. The `get` method acts like it does for a normal dict, it returns the value if present, or `None` if not.

To validate the credentials, we try and grab an `AdminUser` from our table by matching on the `username`. If we have a user with this username, we then use `check_password_hash`, passing the `AdminUser`'s stored password and the password supplied by the form. If the passwords match then the submitted details are both correct, and we can log the user in. We achieve this by setting the `"logged_in"` session variable, and also store the `AdminUser`'s ID, then redirect the user off to the index.

If the username was not found, or the passwords did not match, the `flash` function is used to display an error message, and the `login.html` template will be rendered once again.

Before we can test this, let's put a heading into `admin/index.html` so that we can see when we're logged in successfully:

```html
<h1>Welcome to the admin!</h1>

<p>You are logged in</p>
```

Re-run your `web_server.py` file and head over to `http://localhost:5000/admin`. You should get redirected to the login form.

First try entering incorrect details in to have a look at the `flash` message. Then put in your correct login details and see yourself sent back to the index page. Hooray!

#### Editing Data

Now that our admin page is guarded by the login system, we can start adding the functionality to create, read, update, and delete our database records. This is often referred to by the acronym CRUD.

Let's start with "read" by showing a list of `Product`s on the admin index. Change your view to the following:

```python
...

@admin_blueprint.route("/")
def admin_index():
    all_products = Product.select().order_by(Product.name.asc())

    return render_template("admin/index.html", all_products=all_products)

...
```

We are passing a generator of all products, ordered by their `name` attribute, to our template. Now let's display them on `admin/index.html`:

```html
<h1>Welcome to the admin!</h1>
<hr />
<h2>All Products</h2>
<br />

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
    {% for product in all_products %}
        <tr>
            <td>
                <a href="/admin/{{product.id}}">
                    {{product.name|title}}
                </a>
            </td>
            <td>
                £{{"%.2f"|format(product.price|float)}}
            </td>
            <td>
                <button onclick="deleteProduct({{product.id}})">Delete</button>
            </td>
        </li>
    {% endfor %}
    </tbody>
</table>

<script>
    function deleteProduct(productId) {
        console.log("deleting product", productId);
    }
</script>

```

After our welcome message we display a table of all available products, showing their name, price, and some actions. Clicking a product's name will take you to its update page (which we will create next), and each product has a "Delete" button which we can use later to remove a product from our database. 

For the moment, this button will just log the clicked product's ID to the javascript console. 

Reload your admin index and you should see your table with your three products listed.

Let's start by building the edit page, so we can click on those product names. Create a new template file `templates/admin/products/edit_product.html`:

```html
<h1>Edit {{product.name}}</h1>

<hr>

<form name="product_form" action="{{url_for('admin.save_product')}}" method="POST">
    <input type="hidden" name="product_id" value="{{product.id}}">

    <label for="name">Name:</label>
    <input type="text" name="name" id="name" value="{{product.name}}">

    <br/>
    <br/>

    <label for="price">Price:</label>
    <input type="text" name="price" id="price" value="{{product.price}}">

    <br/>
    <br/>

    <input type="submit" value="Save">
</form>

```

A basic HTML form with two text inputs, one for the product's name and one for its price. We also have a hidden input which will send this product's ID. 

We can't use this page yet, as the `admin.save_product` view doesn't exist yet, so hop back over to `views/admin/admin.py`:

```python

...

@admin_blueprint.route("/<int:product_id>")
def edit_product(product_id: int):
    product = Product.get_or_none(Product.id == product_id)
    if not product:
        flash("Product not found")

        return redirect(url_for("admin.admin_index"))

    return render_template("admin/products/edit_product.html", product=product)


@admin_blueprint.route("/save-product", methods=["POST"])
def save_product():
    product = Product()

    product_id = request.form.get("product_id")
    if product_id:
        product = Product.get_or_none(Product.id == product_id)
        if not product:
            return redirect(url_for("admin.admin_index"))

    name = request.form.get("name")
    price = request.form.get("price")

    product.name = name
    product.price = price
    product.save()

    return redirect(url_for("admin.edit_product", product_id=product.id))

```
First our `edit_product` view. This view takes a product ID from the URL and makes sure it is an integer. We then use Peewee to try and fetch a product with this ID from the database. If it's not found, we send the user back to the admin index, since we can't show its form. If we find it, we then render the `edit_form.html` template, passing the product as context.

The `save_product` view begins by creating a new `Product` instance. This will allow us to re-use this view later when we build the "create" functionality. If a `product_id` is passed in our POST data, then the blank product is replaced by the result of a `get_or_none` on the provided ID. If no product is found, we return the user to the admin index. 

Once we have our `Product` instance, we can get the POSTed data from the `request.form` object and assign the values to the instance's `name` and `price` attributes. We then call `save()` to write the changes to our database, before reloading the `edit_product` page.

Your site should be in working condition now, so go ahead and restart your `web_server.py` command and view `http://localhost:8080/admin` in your browser. After logging in, click a product's name and you'll see its edit form. Try changing the name and price and pressing Save. You should see your changes persist after saving, and back on the admin index page.

Groovy! Now let's add the "create" functionality. Put this very simple new view into `views/admin/admin.py`:

```python
@admin_blueprint.route("/create-product")
def create_product():
    return render_template("/admin/products/create_product.html")

```

And now create yourself a template at `templates/admin/products/create_product.html`:

```html
<h1>Create a Product</h1>

<hr>

<form name="product_form" action="{{url_for('admin.save_product')}}" method="POST">
    <label for="name">Name:</label>
    <input type="text" name="name" id="name">

    <br/>
    <br/>

    <label for="price">Price:</label>
    <input type="text" name="price" id="price">

    <br/>
    <br/>

    <input type="submit" value="Save">
</form>
```

This should look familiar, since it's mostly just the `edit_form` again, but without the hidden input or `value` attributes.

Now we need a link to this on our index, so open up `templates/admin/index.html` and add this below your table:

```html
...

<hr />

<a href="{{url_for('admin.create_product')}}">Create new Product</a>

```

Reload your admin index and try clicking on this link. You should be greeted with a blank form. Fill it in and create yourself a new product. After saving, your product should appear on the admin index amongst the others. Neat!

Just one step left now - "delete". Still in your admin index template, alter the `deleteProduct` javascript function at the bottom to the following:

```javascript
    async function deleteProduct(productId) {
        var fd = new FormData();
        fd.set('product_id', productId);

        var response = await fetch(
            '{{url_for("admin.delete_product")}}',
            {
                method: 'POST',
                body: fd,
            } 
        );

        var res_json = await response.json()
        alert(res_json.message);

        location.reload();
    }
```

This function uses the `fetch` syntax to send a POST request to the `admin.delete_product`  view containing form data with the selected product's ID. That view doesn't exist yet, so open up `views/admin/admin.py` for one final time and add the following:

```python
@admin_blueprint.route("/delete-product", methods=["POST"])
def delete_product():
    product_id = request.form.get("product_id")
    product = Product.get_or_none(Product.id == product_id)
    if not product:
        return {"success": False, "message": "Product not found"}, 400

    Product.delete().where(Product.id == product_id).execute()

    return {"success": True, "message": "Product Deleted"}
```

This view grabs the `product_id` from the POST data and uses it to fetch a matching `Product` instance. If not successful, an error response is returned (the `400` after the JSON is the HTTP status code of the request). If the product _was_ found Peewee's `delete().where().execute()` functionality is used to delete the product from our database.

Reload your `web_server` and site then give one of those delete buttons a whack. You should see a popup saying "Product Deleted" and the page should update with the product no longer in your table.

Great - that's all parts of the CRUD functionality completed! With this out of the way, we can now go on to the most important part of any shop - the ability to make sales.
