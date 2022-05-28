# Appendix 1 - Peewee
[(Back to Chapter 2)](#chapter-2)

In these appendices I will be covering some more complex parts of the mentioned libraries which I couldn't fit into our simple example, but still deem important to know. These can be read either before following the book's examples, or after finishing the project. 

As always, the official Peewee docs are going to be more accurate than what is written here.

These examples are correct for Peewee version **3.14.8**.

## Basics

### Selecting

Call the `.select` method on your model class:

```python
Book.select()
```
This is the equivalent of `SELECT * FROM book;`.

This function returns an `iterable` of instances of your Model class (`Book` in this example). To make use of them, you will then need to consume the iterable with either a `for` loop or list comprehension:

```python
books = Book.select()

for book in books:
    # `book` is now an instance of the `Book` model class. 
    print(book.title)
    
# OR:

books = Book.select()
all_books = [b for b in books]
```

#### Selecting specific fields

All examples in this book's project select all fields from our tables, as they are small. This can be a performance hit as tables grow larger.

To select only specific columns, pass the model name, a dot, and the attribute as arguments to your `.select` call. For example:

```
Book.select(Book.author, Book.title)
```
This query selects only the author and title columns.

### Conditions

To filter what you are selecting, pass regular python conditional statements to a `.where` call:

```python
Book.select().where(Book.title == "Flask by Example")

Book.select().where(Book.price >= 5.00)
```

To pass multiple conditions, wrap each in brackets and separate them with an ampersand `&` for `AND`, or a pipe `|` for OR.

For example:

```python
Book.select().where( (Book.price >= 5.00) & (Book.published == True) )
```
Is the equivalent of:

```sql
SELECT * FROM book WHERE book.price >= 5.00 AND book.published = true;
```

For an `OR` query:

```python
Book.select().where( (Book.title == "Flask By Example") | (Book.title == "Tkinter By Exmaple") )
```

Is the equivalent of:

```sql
SELECT * FROM book WHERE book.title = 'Flask By Example' OR book.title = 'Tkinter By Example';
```

You can combine both `AND` and `OR` using brackets, just like in regular SQL:

```python
Book.select().where(
    (
        (Book.date_published > "2020-01-01")
    ) | (
    	(Book.date_published < "2020-01-01") & (Book.revenue >= 100) 
    )
)
```

The above selects all books which are either newer than Jan 1st 2020, or both older than Jan 1st 2020 and have a revenue above 100. In SQL this would be:

```sql
SELECT * FROM book WHERE (book.date_published > '2020-01-01') OR (book.date_published < '2020-01-01' AND book.revenue >= 100);
```

### Getting a Single Instance

If there should only be a single instance of a row matching your condition, you can use the `.get` method to grab it directly. Arguments passed to this method are the same conditionals as would be passed to a `.where` call.

For example:

```python
flask_book = Book.get(Book.name == "Flask By Example")
```

Here your `flask_book` variable will be an instance of your `Book` model.

This will throw a `ModelNotFound` exception if the criteria do not match and no record could be found. 

If you aren't certain that there is a matching row in your database, you can instead use `.get_or_none`, which will return a `Model` instance if a match is found, or `None` if not.

```python
maybe_book = Book.get_or_none(Book.title == "Flask By Example")

if not maybe_book:
    print("No book with that name")
``` 

## Advanced

### Aliases

You can append `.alias` to an attribute inside a call to `.select` to alias the field. This is useful in situations where multiple tables have a column with the same name. For example:

```python
Book.select(Book.author, Book.title.alias("book_title"))
```
This selects a Book's author, and aliases its title to `book_title`.

### Joins

Join two tables by appending a call to  `.join` after a `.select`. The call to join takes two arguments - the Model class to join with, and a condition on which to perform the join, named `on`. To select fields from a joined table, simply pass the Model's name and attribute to `select` as normal.

 For example:

```python
Book.select(
    Book.title, Book.author, Author.date_of_birth
).join(
    Author, on=(Author.name == Book.author)
)
```
This example performs the query:

```sql
SELECT book.title, book.author, author.date_of_birth
FROM book
JOIN author ON author.name = book.author;
```

#### Join types

Join types are available as constants which can be imported from Peewee like so:

```python
from peewee import JOIN
```

These are then passed as the second argument to your `.join` call:

```python
from peewee import JOIN

Book.select(
    Book.title, Book.author, Author.date_of_birth
).join(
    Author, JOIN.INNER, on=(Author.name == Book.author)
)
```

See the Peewee documentation for an up-to-date list of available joins.


### Functions

Functions are found in a module named `fn`. If you know the name of the function you would like to use in regular SQL, it is probably called the same thing in the Peewee module.

For example, to use a `MAX` function:

```python
from peewee import fn

most_copies_sold = Book.select(fn.MAX(Book.copies_sold))
```

You can also alias these function calls:

```python
from peewee import fn

books = Book.select(fn.SUM(Book.revenue).alias("total_revenue"), Book.title).group_by(Book.title)
```

### Group By, Order By, Limit, Offset

These functionalities are all offered by functions of the same name. For example:

```python
books = Book.select(Book.title, fn.SUM(Book.revenue)).group_by(Book.title).order_by(Book.title.asc()).limit(5).offset(5)
```
As above, ordering is done by specifying the Model class and attibute, then appending `.asc()` or `.desc()` for ascending or descending. To alter where NULLs appear, pass `nulls="LAST"` or `nulls="FIRST"` to `.asc` or `.desc`.

