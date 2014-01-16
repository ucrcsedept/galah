from setuptools import setup, find_packages

setup(
    name = "galah",
    version = "0.3.0-rc0",

    author = "Galah Group LLC",
    author_email = "john@galahgroup.com",
    description = ("An automated grading system geared towards processing"
        "computer programming assignments."),
    license = "GG-GPL",

    packages = ["galah.core", "galah.vmfactory"],

    include_package_data = True,
    zip_safe = False,

    entry_points = {
        "console_scripts": [
            "create_admin.py = utils.create_admin:main",
            "api_client.py = utils.api_client:main"
        ]
    },

    install_requires = [
        "Redis==2.9.0"
    ],

    package_data = {
        "web": ["*.html", "*.css"],
    },
)
