# Chapter 5
## Adding Purchase Abilities

Now that we have the ability to create products to list on our shop, let's add the ability for a customer to purchase them. We'll create a Cart which the visitor can use to store items, then a Checkout page where they can enter an email address to complete their order.

### Creating a Cart

We can use Flask's `session` capabilities to give each user a Cart which will follow them around the site. The `session` is essentially just a regular python `dict` which will be stored as an encrypted cookie in the user's browser, and thus will be available in every request they make. This allows us to store data semi-permanently against each individual user. 

To use Flask's `session` we simply import it and start assigning values. We have seen this in action when creating our login system for the admin.

Let's now display our cart on the site. Open up `templates/base.html` and change the contents of the `<body>` tag to the following:

```html
    <body>
        <h1>Welcome to my shop!</h1>
        <hr>
        Items in Cart: <span id="cart-items">{{cart|length}}</span>

        <a href="/checkout">Checkout</a>
        <hr>

        {% block content %}
        {% endblock%}
    </body>
```

Now the number of items in our cart will display underneath our header. Let's create and pass a Cart through in our index page.

```python
from flask import ..., session

@site_blueprint.route("/")
def index():
    products = Product.select()
    if "cart" not in session:
        session["cart"] = "1"
        
    return render_template("index.html", products=products, cart=cart)
```

Reload your site's index page and you should see "Items in Cart: 1" at the top, as well as a link to a checkout page. Now try changing the `"1"` to `"123"` and you should see "Items in Cart: 3". 

Great, now we can keep track of the number of items in our Cart. However, if you load another page, you'll get an error from Jinja because `cart` is missing. To avoid having to remember to pass this variable in every single view, let's create a global template context for our site views, so we will always have our `cart`.

#### Global Jinja Context

Open up `views/site/__init__.py` and change it to this:

```python
from . import site
from web.blueprints import site_blueprint

@site_blueprint.context_processor
def inject_variables():
    from flask import session

    if "cart" not in session:
        session["cart"] = []

    return {"cart": session["cart"]}

```
Here we use the `context_processor` decorator to inject variables into all templates under the `site_blueprint`. This function grabs the `session` from Flask and adds an empty list named `"cart"` if it doesn't already exist. Then it returns a dictionary, which will be the default context for any templates using Flask's `render_template` function within this blueprint.

Save this and open a product page on your site. You should now still see your Cart items in the header. Now we can remove the Cart-related code from our `index` view again.

```python
@site_blueprint.route("/")
def index():
    products = Product.select()
    return render_template("index.html", products=products)
```

#### Adding To Cart

Now we have a Cart, let's get items added. Firstly, we'll need to clear the string-version of our session variable. If you know how, clear the cookies for `localhost` on your browser. If you don't, you can add the line `session["cart"] = []` to your `index` view, load the index page, then remove the line.

With that taken care of, open up `templates/products/view_product.html` and change your `content` block to the following:

```html
<h2>{{product.name}}</h2>

<p>This product costs £{{"%.2f"|format(product.price|float)}}</p>

<button onclick="addToCart({{product.id}})">Add to Cart</button>

<script>
    async function addToCart(productId) {
        var fd = new FormData();
        fd.set('product_id', productId);

        var response = await fetch(
            '{{url_for("site.add_product_to_cart")}}', 
            {
                method: 'POST', 
                body: fd,
            }
        );

        var res_json = await response.json();
        var cartItems = res_json.cart_items;
        document.getElementById("cart-items").innerText = cartItems;
    }
</script>
```
We're adding a button underneath our product's information which will add this product to our Cart. This is achieved using an `onClick` function called `addToCart` which will call some javascript to send a request to our backend. 

The `addToCart` function creates a `FormData` object to wrap up our chosen Product's ID and then POSTs it to a new endpoint called `add_product_to_cart` using `fetch`. The server's response is then parsed and we update the count of our Cart items using the value returned as `cart_items`. 

Let's create this new endpoint now. Open up `views/site/site.py` and add the following:

```python
@site_blueprint.route("/add-product-to-cart", methods=["POST"])
def add_product_to_cart():
    product_id = request.form.get("product_id", type=int)
    if not product_id:
        return {"success": False, "cart_items": len(session["cart"])}

    current_cart = session["cart"]
    current_cart.append(product_id)
    session["cart"] = current_cart

    return {"success": True, "cart_items": len(session["cart"])}
```

In this endpoint we check `request.form` for the `product_id` sent by our Javascript's `FormData` object and parse it as an integer using `type=int`. If it isn't found, we return an unsuccessful response which does not change the items in the Cart.

If the product _is_ found we can then add its ID to our Cart. We do this by copying the cart from our session into a `current_cart` temporary list, appending the Product's ID to it, then assigning this back to the session's Cart. 

We then return a successful response which includes the `cart_items` key which the Javascript can use to update the count in our header. 

With this new endpoint in place, go ahead and load a product page in your browser. Click the "Add to Cart" button a few times and see your "Items in Cart" heading increase. Navigate to another Product page and see your Cart's status follow you around.

Great! Now we have a working Cart, so let's add a way for a user to Checkout.

### Checking Out
When checking out, we will display all of the items in our user's Cart and sum up the total price. There will then be a place for the user to enter their email address and complete the purchase. 
In a _real_ online-shop this would be where the user makes an account and enters their payment information, but we've already learned about account creation, and taking payments is out of scope for this book.

We'll need a new database table for storing any completed orders, so let's go ahead and create that now. Make a file in your `migrations` folder called `V3__add_order_table.sql` containing the following:

```sql
create table "order" (id integer primary key autoincrement, timestamp_created string, email string, products string);
```
Here `"order"` is in double-quotes because it is a reserved word in SQL.

Run `flyway/flyway migrate` to create yourself a new table. Now we'll need the Peewee model, too. Make a file in your `models` folder called `order.py` and add this new class:

```python
from models import BaseModel
from playhouse.sqlite_ext import *


class Order(BaseModel):
    id = AutoField()
    timestamp_created = DateTimeField()
    email = TextField()
    products = JSONField()
```
We haven't seen `DateTimeField` or `JSONField` yet. These are used to tell Peewee that the string values in the database can be interpreted as `datetime` objects or `json` dicts, respectively. The data in SQLite will remain a regular string, however.

Now that we can store a record of our orders, we're in position to add the functionality to our shop. Let's create a new view in our `views/site/site.py` file for checking out:

```python
@site_blueprint.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items = []
    cart_products = {}
    total_price = 0
    for product_id in session["cart"]:
        p = Product.get_or_none(Product.id == product_id)
        if p.name not in cart_products:
            cart_products[p.name] = {"total": float(p.price), "quantity": 1}
        else:
            cart_products[p.name]["total"] += float(p.price)
            cart_products[p.name]["quantity"] += 1

    for name, price_info in cart_products.items():
        cart_items.append(
            {
                "name": name,
                "quantity": price_info["quantity"],
                "total_price": price_info["total"],
            }
        )
        total_price += price_info["total"]

    return render_template(
        "checkout.html", cart_items=cart_items, total_price=total_price
    )
```

There's quite a lot of logic here, but it's mostly just processing the Cart items into a user-readable format.

We create three variables called `cart_items`, `cart_products` and `total_price`. Next we loop through all of the Product IDs in our Cart and fetch the `Product` instance for each. 

If we haven't come across this Product before we create a `dict` inside of `cart_products` which pairs the Product's `name` to another `dict` of its `price` and a `quantity` of 1. If we already have this product in our `cart_products` we simply increase the total price by its unit cost and increase the quantity by one.

Once we've built up this mapping of Produt names to price info, we can loop through our `cart_products` and append a `dict` displaying the information to our `cart_items` list, as well as summing up the cost of each Product in our `total_price` variable.

With the data processed, we can then pass our `cart_items` and `total_price` variables to a new template. Speaking of which, let's create `templates/checkout.html` now:

```html
{% extends "base.html" %}

{% block content %}
    <h1>Checkout</h1>
    <hr>

    <table>
        <tr>
            <th>Product</th>
            <th>Quantity</th>
            <th>Total</th>
        </tr>
        {% for item in cart_items %}
            <tr>
                <td>{{item.name}}</td>
                <td>{{item.quantity}}</td>
                <td>£{{"%.2f"|format(item.total_price)}}</td>
            </tr>
        {% endfor %}
        <tr>
            <td>-</td>
            <td>-</td>
            <td>-</td>
        </tr>
        <tr>
            <td><b>Total</b></td>
            <td></td>
            <td><b>£{{"%.2f"|format(total_price)}}</b></td>
        </tr>
    </table>
{% endblock %}
```

In this template we can loop through our `cart_items` and display them neatly in a table. At the bottom of the table, we add a row full of dashes as a separator, then the total price in bold.

If you want to make the table look a bit nicer, you can add the following styles above your `h1` heading:

```html
    <style>
        table {
            border-collapse: collapse;
        }
        table tr td {
            border: 1px solid black;
            text-align: center;
            padding: 8px;
        }
    </style>
```

Load up your shop and add some items to your Cart, then click the "Checkout" link in the header. You should see a nice breakdown of all items in your Cart, and a total price at the bottom. 

Now we need a way for the purchase to complete, so add the following underneath your table:

```html
    <br>
    <hr>

    <h2>Complete your Purchase</h2>

    <form name="checkout-form" method="POST">
        <label for="email">Email Address</label>
        <input type="email" name="email">

        <br>
        <br>

        <input type="submit" value="Checkout">
    </form>
```

This will add a form which takes the user's email address. We'll now need to process this on the server, so head back to `views/site/site.py` and add the following lines just above your `return` statement:

```python
    if request.method == "POST":
        user_email = request.form.get("email")
        order = Order()
        order.email = user_email
        order.products = cart_products
        order.timestamp_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order.save()

        session["recent_order_id"] = order.id

        return redirect(url_for("site.complete"))
```

Then add an import at the top of the file:

```python
from datetime import datetime
```

On a POST request, generated by a user submitting the form, we grab the provided `email` from `request.form` and create an instance of our `Order` class. This order is populated with the email address, our `cart_products` `dict`, and the current date and time.

The ID assigned to the order is then saved to the `session` and we redirect to the `site.complete` endpoint, which we can write now:

```python
@site_blueprint.route("/complete")
def complete():
    if "recent_order_id" not in session:
        return redirect(url_for("site.index"))

    order = Order.get_or_none(Order.id == session["recent_order_id"])

    session.pop("recent_order_id")
    session["cart"] = []

    return render_template("complete.html", order=order)
```
If there's no recent order we just redirect the user back to the index, as there's no use for this page. Otherwise, we fetch the order details from our database using the ID we saved in the `session`, then remove the `recent_order_id` using `pop` and clear out the user's Cart. 

Our `templates/complete.html` template will be as follows:

```html
{% extends "base.html" %}

{% block content %}
    <h1>Order Complete!</h1>
    <hr>
    <h2>Thanks for your order!</h2>
    <br>
    <h3>Confirmation will be sent to {{order.email}}</h3>
    <hr>

    <table>
        <tr>
            <th>Product</th>
            <th>Quantity</th>
            <th>Price</th>
        </tr>
        {% for name, price_info in order.products.items() %}
            <tr>
                <td>{{name}}</td>
                <td>{{price_info["quantity"]}}</td>
                <td>£{{"%.2f"|format(price_info["total"])}}</td>
            </tr>
        {% endfor %}
    </table>

    <hr>

    <a href="/">Continue Shopping</a>
{% endblock %}
```
The `complete.html` template simply thanks the user for their order, notifies them about incoming email confirmation, and renders the same table of their purchased products as the Checkout page.

Load up your shop in your browser and visit the Checkout page again. Enter something into the email input at the bottom and press the "Checkout" buton. You should see the confirmation of your purchase.

That's it for our online shop! We've now got a Cart which follows the user around between page-loads, and a checkout system which collects and stores orders along with the customer's email address. 

The next chapter will focus on writing some more automated tests for this new functionality to ensure it always works as expected.
