from netflix_data_reader import NetflixReader


reader = NetflixReader()
reader.read_netflix_data(file_path="assign-1/data/netflix_data.csv")
reader.preprocess()
reader.write_netflix_data("assign-1/output_data")
