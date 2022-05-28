# Chapter 0

## Introduction

Welcome to this e-book teaching how to create web applications using primarily Flask, Peewee, and Pytest. 

Throughout this book we will be setting up a digital shop site which will have a distinct public front-end and a gated back-end. Your shop will have a persistent database, a comprehensive suite of automated tests, and the ability to process data separately from the main web server.

Each chapter will introduce the relevant library in a hands-on approach, rather than dumping a heap of documentation upon the reader. If you're someone who would prefer to broaden your knowledge of a library before getting stuck-in with it, I have included appendices at the end which go over the syntax of each library in greater detail. As I am not the author of any of these libraries, there's always a chance that the information becomes outdated, so pay attention to the version numbers at the top of each appendix.

### Coverage and Assumptions

We will be covering python and the titular libraries specifically. The front-end of the site will be written using normal Javascript and Flask's Jinja template - no fancy frameworks or webpack here.

As I use Linux on my computers, the commands will be written assuming a unix-like operating system with a `bash` shell. If you are on Windows, I would recommend using the Windows Subsystem for Linux (WSL) to follow along. Setting this up is outside the scope of this book, so search online for something like "WSL Install Windows 10" to get started. Familiarity with using a terminal is required, as we will need to run various elements of the web server via the command line.

I will also not be teaching the Python language itself - you will need to be familiar with the language to follow along properly. For the best experience, a reader should have a grasp of functions, classes, and importing modules. Decorators are also used a lot in Flask, so a brief understanding of those is also recommended.

With that out of the way, let's begin with some basics.

## Installing Pyenv and Poetry

While there are many ways to install Python itself, and manage its dependencies, we will be using a tool called `pyenv` to install a specific version of the Python language, and a tool called `poetry` (along with in-built virtualenvs) to install dependencies.

If you already know what you are doing, already have a python installation, or you prefer to use other tools to manage installations, feel free to skip the rest of this section.

For this book, we will be using Python 3.10.

### Installing Python via Pyenv

The `pyenv` tool is available over on Github, and comes with a very easy install script.

> Please note, I am not the author of this tool, and so have no control over the contents nor the hosting. This means the links below may disappear at some point. 

Before installation, follow the instructions for getting the necessary dependencies for your operating system from this URL:

> https://github.com/pyenv/pyenv/wiki#suggested-build-environment

Once you have the dependencies taken care of, installing pyenv is as simple as cloning the repo and running a script.


```bash
git clone https://github.com/pyenv/pyenv-installer

cd pyenv-installer

bin/pyenv-installer

```
The installer will use `git` to grab the necessary repos for you, and set up a `.pyenv` folder in your home directory to contain both pyenv itself and any installed python versions.

With `pyenv` taken care of, it's time to install python 3.10:

```bash
.pyenv/bin/pyenv install 3.10.1
```

This command will take some time to run. If you missed any of the pre-requisite dependencies you may see some errors here. Refer back to the wiki to sort those out.

Once your install is successful, we're done with pyenv!

### Installing dependencies with poetry

Now that we have the correct version of Python installed, it's time to grab the titular libraries. We will be using a tool called `poetry` to achieve this, which is easily installed using Python's built-in `pip` module.

#### Setting up a project directory

We'll need to make a folder to store our project. This can be anywhere on your system, and can be moved at any time, so there's no need to worry too much.

When you've chosen where to store your project, create a new directory called `flask-peewee-pytest` and `cd` into it.

#### Creating a Virtualenv

The first step is to create a virtual environment using the pyenv-provided version of Python.

```bash
~/.pyenv/versions/3.10.1/bin/python3 -m venv env

source env/bin/activate
```

Now that we have the virtual environment, we can install `poetry` into it.

```bash
pip install --upgrade pip

pip install poetry
```

Before we can begin installing with poetry, we need a `pyproject.toml` file. Don't worry if you don't know what this is, because `poetry` can generate one for us!

```bash
poetry init
```

Simply follow the prompts, choosing `n` to skip setting dependencies interactively - we will do this via the command line shortly.

Once this command finishes you will have a nice new `pyproject.toml` file.

#### Installing dependencies

To add dependencies via poetry, simply use `poetry add`. To specify development-only dependencies, it's `poetry add --dev`.

Let's install the titular dependencies to our virtual environment. Since our unit tests will not be running in production, we add `pytest` as a development dependency:

```bash
poetry add flask peewee

poetry add --dev pytest
```

That's it, we've now got our three main dependencies installed, and are ready to begin writing our web-app. Get your editor / IDE of choice ready for the next chapter!
