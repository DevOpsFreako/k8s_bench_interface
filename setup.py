from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in k8s_bench_interface/__init__.py
from k8s_bench_interface import __version__ as version

setup(
	name="k8s_bench_interface",
	version=version,
	description="Frappe Framework API for k8s-bench",
	author="Castlecraft Ecommerce Pvt. Ltd.",
	author_email="support@castlecraft.in",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
