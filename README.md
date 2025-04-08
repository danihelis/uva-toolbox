# UVa toolbox

This is an interactive program to compile and submit solutions to [UVa Online Judge](https://onlinejudge.org/), a website with
hundreds of programming problems. It is integrated with Felix Halim's [uHunt API](https://uhunt.onlinejudge.org/),
so you can check your submissions and other statistics from the terminal.

I use this tool to create and submit [my own solutions](https://github.com/danihelis/uva-solutions).


## How to use it

First you must install the requirements using pip:

```bash
pip install -r requirements.txt
```

Then you can run the program with:

```bash
python utb.py
```
To exit the interactive shell, just type `CTRL+C`.


## How to configure it

You can override the default options in a local file named `utb.yaml`. All available options are definied in
`utb/setting.py`. When overriding the command line for an external tool (like a text editor), be sure to type
`{}` in the command line, as it will contain the expected argument. For example, you could define:

```yaml
editor: gvim -o {}
```

## How to setup an account

You must have a valid account at  [UVa Online Judge](https://onlinejudge.org/). 
Once it is created, run the interactive program and type the command 

```
# user {username}
```

where `{username}` is your account. No password will be requested. It will be asked only when you submit a solution 
for the first time, and then it will be stored in a local file (usually `.data/account.json`). The password is not
stored as an encrypted string. If you are concerned about security, delete this file afterwards.
