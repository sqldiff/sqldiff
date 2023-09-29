Run test:

```sh
sudo pip install pipenv
pipenv install --dev
pipenv run pytest -s
```

[May need to](https://github.com/pypa/pipenv/issues/4369) `pipenv --rm && pipenv install --dev` in certain cases.

Run linter:

```sh
pipenv run flake8 --statistics
```
