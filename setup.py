import os

from setuptools import find_packages, setup

from k8s_bench_interface import __version__ as version

requirements_file = os.environ.get("REQUIREMENTS_FILE", "requirements.txt")

with open(requirements_file) as f:
    install_requires = f.read().strip().split("\n")


setup(
    name="k8s_bench_interface",
    version=version,
    description="Frappe Framework API for k8s-bench",
    author="Castlecraft Ecommerce Pvt. Ltd.",
    author_email="support@castlecraft.in",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
