# ml-and-ai-course
Repository for all projects done during the course.

### IMPORTANT
Add **new configuration** in **PyCharm** to set the correct working directory.
Otherwise, the paths in `run_netflix_reader.py` need to be changed.

#### New paths should be as follows:

`run_netflix_reader.py`: <br>
...<br>
~~`reader.read_netflix_data(file_path="assign-1/data/netflix_data.csv")`~~ <br>
`reader.read_netflix_data(file_path="data/netflix_data.csv")` <br>
... <br>
~~`reader.write_netflix_data("assign-1/output_data")`~~ <br>
`reader.write_netflix_data("output_data")`

## Adding new configuration
### 1. Open config selector - click *Edit Configurations...*<br>
![img_1.png](readme-imgs/img_1.png)

### 2. Click on + or *Add new...*<br>
![img_2.png](readme-imgs/img_2.png)

### 3. Select *Python*<br>
![img_3.png](readme-imgs/img_3.png)

### 4. Pay attention to *Script path* and *Working directory*:<br>
![img_4.png](readme-imgs/img_4.png)