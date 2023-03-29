import os
import pandas as pd


class NetflixReader:
    def __init__(self):
        self.netflix_data_raw = pd.DataFrame()
        self.netflix_data = pd.DataFrame()
        self.train_data = pd.DataFrame()
        self.val_data = pd.DataFrame()
        self.test_data = pd.DataFrame()
        self._type_dict = {
            "index": "int",
            "id": "string",
            "title": "string",
            "type": "category",
            "release_year": "int",
            "runtime": "int",
            "genres": "string",
            "production_countries": "string",
            "imdb_id": "string",
            "imdb_score": "float",
            "imdb_votes": "int"
        }
        self._data_split_ratios = {"train": 0.8, "val": 0.2, "test": 0.0}
        self.data_leakage_warning = False

    def set_data_split_ratio(self, new_split_ratios: dict):
        pass

    def read_netflix_data(self, file_path: str):
        self.netflix_data_raw = pd.read_csv(file_path, delimiter=">")
        return self.netflix_data_raw

    def preprocess(self):
        self.netflix_data_raw.drop(columns="seasons", inplace=True)
        self.netflix_data_raw.drop(columns="age_certification", inplace=True)
        self._drop_missing_values()
        self._set_types()
        self.netflix_data.drop(columns="production_countries", inplace=True)
        self._convert_list_to_bool("genres")
        self.netflix_data.drop(columns="genres", inplace=True)
        self._split_data()
        # self.data_leakage_warning = self._is_data_leakage()

    def write_netflix_data(self, file_path: str):
        # Create directories for the train/val/test splits if they don't exist
        os.makedirs(os.path.join(file_path, "train"), exist_ok=True)
        os.makedirs(os.path.join(file_path, "val"), exist_ok=True)
        os.makedirs(os.path.join(file_path, "test"), exist_ok=True)

        # Write the train split as a .pickle file
        train_file = os.path.join(file_path, "train", "train_data.pickle")
        with open(train_file, "wb") as f:
            pd.to_pickle(self.train_data, f)

        # Write the val split as a .pickle file
        val_file = os.path.join(file_path, "val", "val_data.pickle")
        with open(val_file, "wb") as f:
            pd.to_pickle(self.val_data, f)

        # Write the test split as a .pickle file
        test_file = os.path.join(file_path, "test", "test_data.pickle")
        with open(test_file, "wb") as f:
            pd.to_pickle(self.test_data, f)

    def _drop_missing_values(self):
        self.netflix_data_raw.dropna(inplace=True)

    def _set_types(self):
        for col, dtype in self._type_dict.items():
            if col in self.netflix_data_raw.columns:
                self.netflix_data[col] = self.netflix_data_raw[col].astype(dtype)

    @staticmethod
    def _convert_string_to_list(str_list: str):
        return str_list.split(',')

    def _convert_list_to_bool(self, column_to_distribute: str):
        genres = self.netflix_data[column_to_distribute].str.strip("[]").str.replace("'", "").str.split(", ")
        for genre in set(genre for genres_list in genres for genre in genres_list):
            self.netflix_data[f"{genre.lower().replace(' ', '_')}"] = genres.apply(lambda x: genre in x)

    def _split_data(self):
        self.train_data = self.netflix_data.sample(frac=self._data_split_ratios["train"])
        self.val_data = self.netflix_data.sample(frac=self._data_split_ratios["val"])
        self.test_data = self.netflix_data.sample(frac=self._data_split_ratios["test"])

    def _is_data_leakage(self):
        pass
