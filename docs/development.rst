Development
===========

The project is open-source.

Changes are managed through GitHub. Pull requests are particularly welcome.

All changes are automatically tested using GitHub Actions.

New release
-----------

Follow these steps to publish the new release:

* update changelog - use any text editor
* tag version - use ``git tag vX.Y.Z`` (versions are managed by ``setuptools-scm``)
* build package - use ``python -m build``
* upload release to PyPI - use ``twine upload dist/*``
* push changes to GitHub - ``git push origin && git push --tags``
