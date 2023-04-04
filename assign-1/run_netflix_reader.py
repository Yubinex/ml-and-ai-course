from netflix_data_reader import NetflixReader


# Add new run configuration to set the correct working directory in order to use these file paths
# Script Path -> path to run_netflix_reader.py
# Working Directory -> ml-and-ai-course
reader = NetflixReader()
reader.read_netflix_data(file_path="assign-1/data/netflix_data.csv")
reader.preprocess()
reader.write_netflix_data("assign-1/output_data")


