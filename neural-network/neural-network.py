# TensorFlow 2.0 Crash Course
# https://www.youtube.com/watch?v=6g4O5UOH304

import tensorflow as tf;
from tensorflow import keras;
import numpy as np;
import math;
import json;

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
        with open(path) as reader: return json.load(reader);
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
print('input_vector_size', input_vector_size);
layers = [keras.layers.InputLayer(input_shape=(input_vector_size,))];
for i in range(int(math.log(input_vector_size, 2) - 3)):
    layers.append(keras.layers.Dense(round(input_vector_size / (2 ** (i + 1))), activation="tanh"));
layers.append(keras.layers.Dense(6, activation="softmax"))
model = keras.Sequential(layers);
optimizer = keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, amsgrad=False);
model.compile(optimizer=optimizer, loss="sparse_categorical_crossentropy", metrics=['accuracy']);

# train the network
model.fit(train_data, train_labels, epochs=10);

# test the network
test_loss, test_acc = model.evaluate(test_data, test_labels);
print("Tested Acc:", test_acc);

# calculate error
prediction = model.predict(test_data);
within_x = list(map(lambda x: 0, range(6)));
for i in range(len(test_data)):
    for x in range(6):
        within_x[x] += 1 if abs(test_labels[i] - np.argmax(prediction[i])) <= x else 0;

output = '';
output += '--------------------------------' + '\n';
output += '\n'.join([f'within {x} stars = {within_x[x]} / {len(test_data)} = {100 * within_x[x] / len(test_data)}%' for x in range(6)]) + '\n';
output += '--------------------------------' + '\n';
print(output);
with open('../results.txt', 'w+') as writer:
    writer.write(output);
