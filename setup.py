from setuptools import setup, find_packages 

with open('requirements.txt') as f: 
	requirements = f.readlines() 

with open("README.md", "r") as fh:
    long_description = fh.read()

setup( 
	package='src',	
	name='CAMIViz',  
	version='0.1',
	author="David Koslicki",
	author_email="dmk333@psu.edu",
	url="https://github.com/dkoslicki/CAMIProfilingVisualization",
	description="A collection of tools to visualize CAMI profiling outputs",
	long_description=long_description,
	long_description_content_type="text/markdown",
	license ='MIT', 
	packages = find_packages(), 
	entry_points ={ 
		'console_scripts': [ 
			'profile_to_plot = src.profile_to_plot:main'
		] 
	}, 
	classifiers =( 
		"Programming Language :: Python :: 3", 
		"License :: OSI Approved :: MIT License", 
		"Operating System :: OS Independent", 
	), 
	keywords ='profile_to_plot src python package', 
	install_requires = requirements, 
	zip_safe = False
) 


