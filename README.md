Tsuru Shell
-----------
Mini shell for tsuru

##What is tsuru?

tsuru is an open source polyglot cloud application platform (PaaS). With tsuru, you don’t need to think about servers at all. You can write apps in the programming language of your choice, back it with add-on resources such as SQL and NoSQL databases, memcached, redis, and many others. You manage your app using the tsuru command-line tool and you deploy code using the Git revision control system, all running on the tsuru infrastructure.

(From: [https://github.com/tsuru/tsuru](https://github.com/tsuru/tsuru))

Dependencies
------------
* python3

Instalation
-----------
```
tsuru plugin-install shell https://raw.githubusercontent.com/wpjunior/tsuru-shell/master/tsuru-shell.py
```

Usage
-----------
```
tsuru shell -a <APP_NAME>
```
