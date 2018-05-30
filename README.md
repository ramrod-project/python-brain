this is a static repo to serve the python compoent

issues/commits go to https://github.com/ramrod-project/database-brain




```
    cp -r ../database-brain/schema/* .

    <commit changes to this master>

    git tag ramrodbrain-0.X.x -m "Release Message"

    git push --tags origin master

    python3 setup.py sdist upload -r pypi
```
