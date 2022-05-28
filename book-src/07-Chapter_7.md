# Chapter 7
## Background Tasks with Celery

Sometimes we may have tasks which do not necessarily need to run _before_ we provide feedback to the user. For example, a lot of online shops will not make customers sit and wait while their system sends the confirmation email. This allows developers to do potentially-slow data processing tasks without leaving the user staring at a "loading..." message. One way we achieve this with a Flask website is to make use of a python library named Celery.

Celery allows us to take advantage of separate "workers" running tasks independently of the web application but still using its data. These workers run in separate processes, meaning heavy processing tasks will not affect any web requests.

### Heavy Processing

Let's emulate a heavy processing task by adding a confirmation email to our Checkout endpoint. Create a folder in the root of your project called `tasks` and inside make a python file called `send_email.py`:

```python
import time

def send_confirmation_email(email: str):
    time.sleep(5)  # emulate processing
    print(f"sending email to {email}")
```
This function sleeps for 5 seconds to emulate a complex database query, then prints a message about emailing the provided `email`. Sending an email is complex, and therefore out of scope for the purposes of this book, so we'll make do with this `print` statement. 

Now open up `web/views/site/site.py` and add a call to this function in your `complete` view:

```python
from tasks.send_email import send_confirmation_email
...

def complete():
    ...
    send_confirmation_email(order.email)

    return render_template("complete.html", order=order)
```

Open up your shop's website and add some items to your Cart, then Checkout. You will notice your site hangs for a while before showing you the confirmation page. This is likely to be frustrating to users, who may leave the site, or refresh the page thinking something is wrong and accidentally place two orders. 

Let's now add Celery to our project so that we can remedy this potential issue.

### Adding Celery

In order to run background tasks Celery itself needs a way to manage a queue. For this example we will be using Redis since it is very easy to set up and use.

In a new terminal window, source your virtualenv with `source env/bin/activate` then run `poetry add celery celery[redis]` to install Celery and its dependencies.

While this is installing we can bring in Redis. Specific instructions for doing this depend on the Operating System you are using, so search the web for "Redis install `my_operating_system`" and find the official docs. On Linux, Redis is most likely available in your distro's repositories. MacOS can use `homebrew`, and Windows users can use the WSL terminal they are using to follow along with this book. 

With Redis installed, running the server is as easy as executing the command `redis-server`. You can leave this running while we set up Celery in our code. 

Stop your web server if you haven't already and open up `web_server.py` in your editor. Change the beginning of the file to look like so:

```python
from celery import Celery
from flask import Flask

app = Flask(__name__)
app.secret_key = "very secret"

celery = Celery("My Shop", broker="redis://localhost:6379/0")
from web.views import admin, site
...
```

Now open your `tasks/send_email.py` file and we can turn the `send_confirmation_email` function into a Celery task:

```python
import time

from web_server import celery


@celery.task
def send_confirmation_email(email: str):
    time.sleep(5)
    print(f"sending email to {email}")
```

Turning a synchronous function into an async one is as easy as importing `celery` and decorating the function with `@celery.task`. Now our Celery worker can see this task and will be able to process it independently of our web server.

To run a Celery worker we'll need an entry point to our application. Create a file called `run.py` in the root of the project:

```python
from web_server import celery
```

And now we are set up to run a Celery worker! Open up a new terminal and source your virtualenv. Now run the following command:

```
celery -A run worker -l info -E
```

This points Celery to our new `run.py` file, tells it to run a `worker`, sets the `loglevel` to `info` so that we can see what it's doing, and finally uses `-E` to tell the worker to log events about each job.

One last thing now - we need to tell our `complete` view to call this function asynchronously using the Celery worker. We do this by calling the `delay` function which has now been added by the `@celery.task` decorator. Open up `web/views/site/site.py` and change the line in  `complete`:

```python
    send_confirmation_email.delay(order.email)
```

Now our slow function will be executed by the Celery worker, meaning the customer will see the Complete page without waiting for their confirmation email to be sent.

Start up your web server with `python3 web_server.py` and buy some products on your website. You should notice the Complete page does not hang any more. Open the terminal running your `celery` command and you should see a message similar to this:

```
[2022-05-02 07:31:27,561: WARNING/ForkPoolWorker-8] sending email to test@example.com
```

Congratulations, you have successfully run a background task from your website!

### Adjusting the Tests

Since we should not have to run Redis in order to test our application, we'll need to stop our server from trying to connect during tests. We can detect if we are testing using this line:

```python
if "pytest" in sys.modules:
```

Open up `factory.py` and change the creation of the `celery` instance to the following:

```python
import sys
...

if "pytest" in sys.modules:
    celery = Celery("My Shop", broker="memory://")
else:
    celery = Celery("My Shop", broker="redis://localhost:6379/0")
```

This will tell Celery to use an in-memory queue during unit tests. This does not work when actually trying to use Celery in practise, which is why we had to install Redis.

With Celery taken care of, our tests should now run successfully. However, we can actually now check that the confirmation email task is called when an order completes.

#### Mocking Celery's Delay
In a new terminal window, source your virtualenv and run `poetry add --dev pytest-mock`. This will allow us to use Mocking to test if a function has been called during the execution of another.

First, we'll create a mock of the `delay` function in our `tests/helpers.py` file:

```python
...
__all__ = [
    ...
    "mock_send_confirmation_email_delay",
    "with_test_db",
]
...

def mock_send_confirmation_email_delay(mocker):
    from tasks.send_email import send_confirmation_email

    mocker.patch.object(send_confirmation_email, "delay", autospec=True)
```

We use the `mocker` fixture (which will be passed to this function) to `patch` the `delay` function with a mock. This will then allow us to inspect whether the function was called during the test.

Now open up `tests/site/test_site.py` and change your `test_checkout_post` function to the following:

```python
@with_test_db((Order, Product))
def test_checkout_post(mocker):
    mock_send_confirmation_email_delay(mocker)
    p = create_test_product("Floss", "1.50")
    p2 = create_test_product("Toothbrush", "2.99")

    assert Order.select().count() == 0

    with testing_app.session_transaction() as s:
        s.clear()
        s["cart"] = [p.id, p.id, p2.id]

    res = testing_app.post(
        "/checkout", data={"email": "a@a.com"}, follow_redirects=True
    )
    res_data = res.get_data()

    assert b"Floss" in res_data
    assert b"Toothbrush" in res_data
    assert b"3.00" in res_data
    assert b"2.99" in res_data
    assert b"sent to a@a.com" in res_data

    assert Order.select().count() == 1

    o = Order.get()
    assert o.email == "a@a.com"
    assert o.products == {
        "Floss": {"total": 3.0, "quantity": 2},
        "Toothbrush": {"total": 2.99, "quantity": 1},
    }

    from tasks.send_email import send_confirmation_email

    send_confirmation_email.delay.assert_called_once()
    assert send_confirmation_email.delay.call_args[0][0] == "a@a.com"
```

The test now takes an argument called `mocker`, which will be injected by the `pytest-mock` library we installed. This is passed to the `mock_send_confirmation_email_delay` helper function to carry out the mocking. 

Once we have asserted that the contents of the page are as expected, we have two new asserts at the end of our test. We first use `assert_called_once` to check that our `send_confirmation_email` function was sent to the Celery worker. Then we can use its `call_args` attribute to check that the argument passed to this function was the email address we entered. The `[0][0]` is used to get the first call to this function, then the first argument of that call. Since there is only one call, and only one argument, this is all we need to check.

Fantastic, we've now got a way of running background tasks outside of a web request to avoid slowing down the user's page load, and we have an automated test to ensure they are called with the correct arguments!

With that, our project is now complete! We have ourselves a website split into two sections - an admin protected by a login, and a public-facing shop. We can process and store customer orders in a database, and process the data within outside of a web request context using Celery. Our whole application has a suite of automated tests which ensure that the critical functionality is behaving as it should. 
