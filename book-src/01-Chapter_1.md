# Chapter 1

## Flask Beginnings
With our development environment taken care of, let's dive right in to Flask. In this chapter we'll go over the basics of getting a Flask server up-and-running, then look into how to structure the web side of our project in a maintainable way.

### Hello Flask
In keeping with programming tradition, let's start with a "Hello Flask" implementation.

In your project folder, create a file called `web_server.py` and add the following:

```python
from flask import Flask

app = Flask(__name__)
app.secret_key = "very secret"

@app.route("/")
def hello_flask():
    return "Hello, Flask!"
    
if __name__ == "__main__":
    app.run(debug=True)
```

Save this file and run the webserver with `python3 web_server.py`. You should see a message telling you that the server is available on `http://127.0.0.1:5000/`. Visit this URL in a browser and you'll be presented with "Hello, Flask!".

> Note: Mac users may find that port 5000 is already in use. To get around this, add the `port=8080` argument to your `app.run` call, and visit `http://localhost:8080/`.

Not too much code went into making that, so let's go over it.

First we import `Flask` itself, and create an instance named "app". Passing the `__name__` argument is convention. 

Once we have our Flask instance, we need to set a secret key. This is used to encrypt session data, and so in a production environment should be a lot more secure than this simple string. We will come back to this later.

With our sessions secure, we now need to add some routes to our server. This is achieved by decorating a function with the `route` decorator, passing the URL as the argument, so "/" in this case. Inside this function we must return something which can be recognised by Flask as an HTTP response (typically a string, a dictionary, or a rendered template, which we will see shortly).

That's it, we now have a server with a URL set up. The `if __name__ == "__main__"` block allows us to run this file as a script to launch the server, while also allowing other files to import from it without also causing the server to run. We use the `run` function to start our server, and pass `debug=True` to enable the debugging interface.

To have a look at the debugging screen, add the line `1 / 0` above the `return` statement in your `hello_flask` method, then reload the page. You should see a `ZeroDivisionError` screen with a nice stack trace showing the problematic line.

### Rendering HTML
We know how to return plain text, but _real_ websites use HTML, so how do we do that? Flask comes with a popular templating library called `Jinja` supported by default, as well as a helper function to both compile the template contents and return it as an HTTP response. Let's turn our homepage into something a bit more realistic.

Create a `templates` folder in the root of your project, and then create an `index.html` file inside.

```html
<h1>Welcome to my shop!</h1>
<hr>
<table>
    <tr>
        <td>Toothpaste</td>
        <td>£2</td>
    </tr>
    <tr>
        <td>Toothbrush</td>
        <td>£1.50</td>
    </tr>
    <tr>
        <td>Floss</td>
        <td>£0.99</td>
    </tr>
</table>
```

(Note that this is not "fully-formed" HTML, but a browser should render it anyway. We will deal with this later).

Template created! Now we need to render it. Hop back over to your `web_server.py` file and edit your `hello_flask` function as follows:

```python
@app.route("/")
def index():
    return render_template("index.html")
```

We'll start by renaming the function to `index`, as it better describes the page we'll be rendering.

`render_template` is a helper function in Flask which will perform Jinja rendering and return your HTML as an HTTP response. We will need to import this though, so go up to the top of your file and import the library from flask

```python
form flask import Flask, render_template
```

Run your web server once more and reload the index page. You should see a beautiful table of prices.

Obviously it would be rather daft to have to edit HTML directly when your shop's stock changes - this information should be stored in a database and pulled out on the server side. We'll get to the database itself next chapter, but for now we can pretend, and learn about Jinja rendering along the way. 

#### Using variables in Jinja
In your `web_server.py` file, change the `index` function and add a dictionary of products to prices like so:

```python
@app.route("/")
def hello_flask():
    products = {"toothpaste": 2.00, "toothbrush": 1.50, "floss": 0.99}
    
    return render_template("index.html", products=products)
```

When using `render_template`, any arguments passed after the filename of the HTML file will be passed to the template to be used by Jinja. This is known as the "template context".

Change the content of your `templates/index.html` file to the following:

```html
<h1>Welcome to my shop!</h1>
<hr>
<table>
    {% for product_name, price in products.items() %}
    <tr>
        <td>{{product_name}}</td>
        <td>{{ "£%.2f"|format(price) }}</td>
    </tr>
    {% endfor %}
</table>
```

To use our variables in Jinja, we need to utilise two different sets of special syntax: the double-brace `{{` `}}` and the percent-brace `{%` `%}`. Percent-brace tags are used to insert logic, such as `for` loops and `if` statements. The double-brace is used to insert python variables as text inside the template.

In the above example, we use the percent-brace syntax to initiate a `for` loop, iterating over our `products` variable and unpacking the keys and values into two python variables - `product_name` and `price`. We then place the product names as text into our HTML by using the double-brace syntax. We do the same for the price, but use a pipe into a format string to get the correct currency display.

The pipe character is Jinja's own syntax (rather than python's) which passes the variable into a function exposed by Jinja to the templates. You can think of these as reversing the order of a normal function from `my_func(variable)` to `variable|my_func`. 

We now have a single page listing all of our products, so let's add individual pages for each one. Again, it's not manageable to create a specific route for each product, so we'll need to make use of the database's information in Flask.

### Using variables in Flask routes
Underneath your `index` function, add the following:

```python
@app.route("/<string:product_name>")
def view_product(product_name):
    products = {"toothpaste": 2.00, "toothbrush": 1.50, "floss": 0.99}

    price = None
    if product_name in products:
        price = products[product_name]
    else:
        abort(404)

    return render_template(
        "products/view_product.html", price=price, product_name=product_name
    )

```

We now have a route which can take a variable from the URL, as you can see from the `route` decorator. This `product_name` variable is then passed into our `view_product` function automatically. We have annotated this variable as a `string`, so that we can guarantee the type of the python variable passed.

The rest of this function searches our `products` dictionary for the provided string, and if found sets the value of `price`. If the product is not in the dictionary, we use a flask helper to return an HTTP 404 response.

Adjust your import statement at the top of the file to include this function:

```python
from flask import Flask, render_template, abort
```

To make our server run we'll need to make that new template. Go ahead and create a folder inside your `templates` folder called `products`, then create an HTML file inside called `view_product.html` containing the following:

```html
<h1>Welcome to my shop</h1>
<hr>

<h2>{{product_name}}</h2>

<p>This product costs £{{"%.2f"|format(price)}}</p>

<p>Out of Stock</p>
```

After you save this file, your server should be able to run again, so start it up with `python3 web_server.py` and head on over to `localhost:5000`. You should see your index page.

Add the name of a product to the end of your URL, for example `/toothpaste`, and you should see your new template render. You can also try using a product which doesn't exist, such as `/water`, to see the 404 error page.

Now we have two templates which both share the same header at the top of the page. It would be a hassle to keep copy-pasting that into each new file, and we haven't got the proper HTML declarations in our templates either. We'll sort that out now by looking at template inheritance.

### Template Inheritance
Jinja allows templates to inherit from others using two main tags:

- `{% extends %}`
- `{% block %}`

Let's see these in action by creating a base template. Add a file called `base.html` in your `templates` folder:

```html
<!DOCTYPE html>
<html>
    <head>
        <title>My Shop</title>
    </head>

    <body>
        <h1>Welcome to my shop!</h1>
        <hr>
        {% block content %}
        {% endblock %}
    </body>

</html> 
```

We use a `block` tag to assign a name and location to a piece of inheritable content. Since we have created a `block` named `content` inside our `body` tags, any template inheriting our base can include a `{% block content %}` tag to insert its contents into the page `body`.

Let's alter our `index.html` and `view_product.html` templates to inherit from the base.

`index.html`:

```html
{% extends "base.html" %}
{% block content %}
<table>
    {% for product_name, price in products.items() %}
    <tr>
        <td><a href="/{{product_name}}">{{product_name}}</a></td>
        <td>{{ "£%.2f"|format(price) }}</td>
    </tr>
    {% endfor %}
</table>
{% endblock %}
```

---

`view_product.html`:

```html
{% extends "base.html" %}
{% block content %}
<h2>{{product_name}}</h2>

<p>This product costs £{{"%.2f"|format(price)}}</p>

<p>Out of Stock</p>
{% endblock %}
```

Save and re-run your webserver and visit both the homepage and a product page (you may notice we added `a` tags so that you can visit a product page by clicking on the product's name). They should both look just like before, but now have fully-formed HTML and are sharing the heading. Use the "Inspect Element" or "View Source" capabilities of your web browser to have a look at the generated HTML and see this for yourself.

The `extends` tag takes the name of the base template in quotes, then exposes all blocks defined in that template to the current file (although you do not need to add content to _all_ blocks defined in the base). The content which is wrapped in `{% block content %}` in our child templates is then inserted into the base template where its own `{% block content%}` tags lie.

This covers the basics of flask. We now have a working web server, which we can add routes to using the `@app.route` decorator. We know how to pass variables to these routes using `/<string:variable>`, and how to get python variables into Jinja templates.

To continue with our website, we will now look at replacing those hard-coded `products` dictionaries with data from an actual database, as we dive into the `Peewee` libarary. 
