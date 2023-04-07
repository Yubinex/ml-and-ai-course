import os
import pandas as pd
from typing import Tuple, Optional


# pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


class NetflixReader:
    def __init__(self) -> None:
        # Create empty pandas DataFrames to hold the
        # Netflix dataset, train data, validation data, and test data
        self.netflix_data_raw: pd.DataFrame = pd.DataFrame()
        self.netflix_data: pd.DataFrame = pd.DataFrame()
        self.train_data: pd.DataFrame = pd.DataFrame()
        self.val_data: pd.DataFrame = pd.DataFrame()
        self.test_data: pd.DataFrame = pd.DataFrame()
        # Create a dictionary that maps column names to
        # data types for the Netflix dataset
        self._type_dict: dict = {
            "index": int,
            "id": "string",
            "title": "string",
            "type": "category",
            "release_year": int,
            "runtime": int,
            "genres": "string",
            "production_countries": "string",
            "imdb_id": "string",
            "imdb_score": "float",
            "imdb_votes": int
        }
        # Create a dictionary containing the ratios for the train,
        # validation, and test splits
        self._data_split_ratios: dict = {"train": 0.8, "val": 0.2, "test": 0.0}
        self.data_leakage_warning: Tuple[bool, Optional[pd.DataFrame]] = (False, None)

    def set_data_split_ratio(self, new_split_ratio: dict) -> None:
        # Check that the input is a dictionary
        if not isinstance(new_split_ratio, dict):
            raise TypeError('Input must be a dictionary.')

        # Check that the dictionary keys match the expected keys
        expected_keys: set = {"train", "val", "test"}
        if not set(new_split_ratio.keys()) == expected_keys:  # cast dict keys to set for comparison with another set
            raise ValueError(f'Input dictionary must have the keys {expected_keys}.')

        # Check that the values in the dictionary are between 0 and 1 and add up to 1
        if not all(0 <= value <= 1 for value in new_split_ratio.values()):
            raise ValueError('Values in the input dictionary must be between 0 and 1.')
        if not sum(new_split_ratio.values()) == 1:
            raise ValueError('Values in the input dictionary must add up to 1.')

    def read_netflix_data(self, file_path: str) -> None:
        # Reads the Netflix data from the specified file_path using pandas' read_csv method,
        # and saves it to the netflix_data_raw attribute of the NetflixData class.
        # The delimiter is set to ">" because that is the delimiter used in the data file.
        self.netflix_data_raw = pd.read_csv(file_path, delimiter=">")

    def preprocess(self) -> None:
        self.netflix_data_raw.drop(columns="seasons", inplace=True)
        self.netflix_data_raw.drop(columns="age_certification", inplace=True)
        self._drop_missing_values()
        self._set_types()
        self.netflix_data.drop(columns="production_countries", inplace=True)
        self._convert_list_to_bool("genres")
        self.netflix_data.drop(columns="genres", inplace=True)
        self._split_data()
        self.data_leakage_warning = self._is_data_leakage()
        if self.data_leakage_warning[0]:
            print(f"{__class__.__name__}:")
            print(f"Warning: there is data leakage between datasets.")
            print(f"Intersecting data:")
            print(self.data_leakage_warning[1])
        else:
            print(f"{__class__.__name__}: No data leakage found.")

    def write_netflix_data(self, file_path: str) -> None:
        # Create directories for the train/val/test splits if they don't exist
        os.makedirs(os.path.abspath(file_path), exist_ok=True)

        # Write the train split as a .pickle file
        # join root directory with file name to enure that the file is written to the correct location
        train_file: str = os.path.join(file_path, "train.pickle")
        with open(train_file, "wb") as f:
            pd.to_pickle(self.train_data, f)

        # Write the val split as a .pickle file
        val_file: str = os.path.join(file_path, "val.pickle")
        with open(val_file, "wb") as f:
            pd.to_pickle(self.val_data, f)

        # Write the test split as a .pickle file
        test_file: str = os.path.join(file_path, "test.pickle")
        with open(test_file, "wb") as f:
            pd.to_pickle(self.test_data, f)

    def _drop_missing_values(self) -> None:
        # Drop rows with missing values (i.e., NaN values)
        self.netflix_data_raw.dropna(inplace=True)

    def _set_types(self):
        # Loop through the columns and their corresponding data types
        for col, dtype in self._type_dict.items():
            # Check if the column exists in the raw data
            if col in self.netflix_data_raw.columns:
                # If the column exists, convert its data type and save it to the processed data
                self.netflix_data[col] = self.netflix_data_raw[col].astype(dtype)

    # Method not needed. Implemented in next method.
    @staticmethod
    def _convert_string_to_list(str_list: str) -> list:
        pass

    def _convert_list_to_bool(self, column_to_distribute: str) -> None:
        # Extract the list of genres from the specified column,
        # remove unwanted characters, and split them into separate strings
        genres: pd.Series = self.netflix_data[column_to_distribute].str.strip("[]").str.replace("'", "").str.split(", ")
        # Loop over each genre in the list of genres
        for genre in set(genre for genres_list in genres for genre in genres_list if genre):  # => `if genre` to check if string not empty
            # Column name = lowercase version of current genre with spaces replaced by '_'
            # For each row in the DataFrame, check if the current genre is in the list of genres for that row,
            # and store the result as a boolean value in the new column
            self.netflix_data[f"{genre.lower().replace(' ', '_')}"] = genres.apply(lambda x: genre in x)  # .apply() -> applies a funciton along a given axis

    def _split_data(self) -> None:
        # Create a copy of the Netflix dataset
        netflix_data_copy: pd.DataFrame = self.netflix_data.copy()

        # Shuffle the data randomly
        netflix_data_copy = netflix_data_copy.sample(frac=1)

        # Split the shuffled data into three portions - train, validation, and test - using the specified ratios
        self.train_data = netflix_data_copy[:int(len(netflix_data_copy)*self._data_split_ratios["train"])]
        self.val_data = netflix_data_copy[int(len(netflix_data_copy)*self._data_split_ratios["train"]):int(len(netflix_data_copy)*(self._data_split_ratios["train"]+self._data_split_ratios["val"]))]
        self.test_data = netflix_data_copy[int(len(netflix_data_copy)*(self._data_split_ratios["train"]+self._data_split_ratios["val"])):]

    def _is_data_leakage(self) -> Tuple[bool, Optional[pd.DataFrame]]:
        # Check for intersections between train and validation datasets
        train_val_intersection: pd.DataFrame = self.train_data.merge(self.val_data, how='inner')  # 'inner' => merge should only include the common rows/intersections
        if not train_val_intersection.empty:
            # Return a tuple with a boolean value of True to indicate data leakage
            # and the dataframe with the intersection
            return (True, train_val_intersection)

        # Check for intersections between train and test datasets
        train_test_intersection: pd.DataFrame = self.train_data.merge(self.test_data, how='inner')
        if not train_test_intersection.empty:
            # Return a tuple with a boolean value of True to indicate data leakage
            # and the dataframe with the intersection
            return (True, train_test_intersection)

        # Check for intersections between val and test datasets
        val_test_intersection: pd.DataFrame = self.val_data.merge(self.test_data, how='inner')
        if not val_test_intersection.empty:
            # Return a tuple with a boolean value of True to indicate data leakage
            # and the dataframe with the intersection
            return (True, val_test_intersection)

        # If there are no intersections, return a tuple with a boolean value of False
        # and None to indicate no data leakage
        return (False, None)
