clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf build dist *.egg-info *.dist-info
	rm -rf download
	rm -rf report