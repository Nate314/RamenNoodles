# TensorFlow 2.0 Crash Course
# https://www.youtube.com/watch?v=6g4O5UOH304

import tensorflow as tf;
from tensorflow import keras;
import numpy as np;
import matplotlib.pyplot as plt;
import functools;

# type of input from ramen-ratings.json
class RamenRecord:
    ReviewNum: int
    Brand: str
    Variety: str
    Style: str
    Country: str
    Stars: float
    TopTen: int
    def __init__(self, dictionary):
        self.ReviewNum = dictionary['ReviewNum'];
        self.Brand = dictionary['Brand'];
        self.Variety = dictionary['Variety'];
        self.Style = dictionary['Style'];
        self.Country = dictionary['Country'];
        self.Stars = dictionary['Stars'];
        self.TopTen = dictionary['TopTen'];

# type of input from ramen-info.json
class RamenInfo:
    CommonWords: [str]
    Brands: [str]
    Styles: [str]
    def __init__(self, dictionary):
        self.CommonWords = dictionary['CommonWords'];
        self.Brands = dictionary['Brands'];
        self.Styles = dictionary['Styles'];

# reads in data from json files and converts to vectors for training and testing input/output
def load_data(train_data_percentage):
    def read_json(path):
        data = None;
        with open(path) as reader:
            data = eval(reader.read().replace('null', 'None'));
        return data;
    ramen_info: RamenInfo = RamenInfo(read_json('../ramen-info.json'));
    def map_json_to_input_vector(data: RamenRecord) -> [int]:
        result = [];
        result.extend([1 if word in data.Variety.split(' ') else 0 for word in ramen_info.CommonWords]);
        result.extend([1 if brand == data.Brand else 0 for brand in ramen_info.Brands]);
        result.extend([1 if style in data.Style else 0 for style in ramen_info.Styles]);
        return result;
    data: [RamenRecord] = list(map(lambda x: RamenRecord(x), read_json('../ramen-ratings.json')));
    split_index: int = round((1 - train_data_percentage) * len(data));
    train_data = data[0:split_index];
    train_labels = list(map(lambda x: round(x.Stars), train_data));
    test_data = data[split_index:];
    test_labels = list(map(lambda x: round(x.Stars), test_data));
    train_data = list(map(lambda x: map_json_to_input_vector(x), train_data));
    test_data = list(map(lambda x: map_json_to_input_vector(x), test_data));
    return (train_data, train_labels), (test_data, test_labels);

# read in training and testing data                  # save 100 inputs for testing
(train_data, train_labels), (test_data, test_labels) = load_data(100 / 2580);

# set up network
input_vector_size = len(train_data[0]);
model = keras.Sequential([
    keras.layers.InputLayer(input_shape=(input_vector_size,)),
    keras.layers.Dense(input_vector_size, activation="sigmoid"),
    keras.layers.Dense(round(input_vector_size / 2), activation="sigmoid"),
    keras.layers.Dense(round(input_vector_size / 4), activation="sigmoid"),
    keras.layers.Dense(round(input_vector_size / 8), activation="sigmoid"),
    keras.layers.Dense(6, activation="softmax")
]);
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]);

# train the network
model.fit(train_data, train_labels, epochs=20);

# test the network
test_loss, test_acc = model.evaluate(test_data, test_labels);
print("Tested Acc:", test_acc);

# calculate error
prediction = model.predict(test_data);
within_0 = 0;
within_1 = 0;
within_2 = 0;
within_3 = 0;
within_4 = 0;
within_5 = 0;
for i in range(len(test_data)):
    within_0 += 1 if abs(test_labels[i] - np.argmax(prediction[i])) <= 0 else 0;
    within_1 += 1 if abs(test_labels[i] - np.argmax(prediction[i])) <= 1 else 0;
    within_2 += 1 if abs(test_labels[i] - np.argmax(prediction[i])) <= 2 else 0;
    within_3 += 1 if abs(test_labels[i] - np.argmax(prediction[i])) <= 3 else 0;
    within_4 += 1 if abs(test_labels[i] - np.argmax(prediction[i])) <= 4 else 0;
    within_5 += 1 if abs(test_labels[i] - np.argmax(prediction[i])) <= 5 else 0;

output = '';
output += '--------------------------------' + '\n';
output += f'within 0 stars = {within_0} / {len(test_data)} = {100 * within_0 / len(test_data)}%' + '\n';
output += f'within 1 stars = {within_1} / {len(test_data)} = {100 * within_1 / len(test_data)}%' + '\n';
output += f'within 2 stars = {within_2} / {len(test_data)} = {100 * within_2 / len(test_data)}%' + '\n';
output += f'within 3 stars = {within_3} / {len(test_data)} = {100 * within_3 / len(test_data)}%' + '\n';
output += f'within 4 stars = {within_4} / {len(test_data)} = {100 * within_4 / len(test_data)}%' + '\n';
output += f'within 5 stars = {within_5} / {len(test_data)} = {100 * within_5 / len(test_data)}%' + '\n';
output += '--------------------------------' + '\n';
print(output);
with open('../results.txt', 'w+') as writer:
    writer.write(output);