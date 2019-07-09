Development
===========

The project is open-source.

Changes are managed through GitHub. Pull requests are particularly welcome.

All changes are automatically tested using TravisCI.

New release
-----------

Follow these steps to publish the new release:

* update changelog - use any text editor
* bump version - use ```bumpversion {major,minor,patch}```
* build package - use ```python setup.py sdist bdist_wheel --universal```
* upload release to PyPI - use ```twine upload dist/*```
* push changes to GitHub - ```git push origin && git push --tags```
