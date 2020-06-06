import pandas as pd
import string
from nltk.corpus import stopwords
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import mean_squared_error
from numpy import array
from numpy import argmax
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Embedding, SimpleRNN, Dense, LSTM
import matplotlib.pyplot as plt
from math import sqrt


# Data Preprocess
def text_process(mess):
    nopunc = [char for char in mess if char not in string.punctuation]
    nopunc = ''.join(nopunc)

    return [word for word in nopunc.split() if word.lower() not in stopwords.words('english')]


def movie_id_process(mess):
    values = array(mess)
    str_values = [str(int_value) for int_value in values]
    label_encoder = preprocessing.LabelEncoder()
    integer_encoded = label_encoder.fit_transform(str_values)
    movieid_encoded = to_categorical(integer_encoded)

    return movieid_encoded


class LSTM_model():
    '''
    build LSTM model
    '''

    def __init__(self):
        self.model = Sequential()


    def build(self,
              embedding_feature,
              output_dim,
              hidden_dim):

        self.model.add(Embedding(max_features, embedding_feature))
        self.model.add(LSTM(hidden_dim))
        self.model.add(Dense(output_dim, activation='softmax'))
        self.model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['acc'])
        return self.model


    def train(self, x, y, batch_size, epochs, split=0.2, plot=False):

        model_train = self.model.fit(x, y, batch_size, epochs, validation_split=split, verbose=0)
        plt.plot(model_train.history['loss'], label='train')
        plt.plot(model_train.history['val_loss'], label='test')
        plt.legend()
        plt.show()


    def predict(self, x_test, y_true):
        y_test = self.model.predict(x_test)
        rmse = sqrt(mean_squared_error(y_true, y_test))
        print('Test RMSE: %.3f' % rmse)

        return y_test


if __name__ == '__main__':
    df = pd.read_csv('movie_review_info.csv')
    len_del_1 = len("[<div class=\"text show-more__control\">")
    len_del_2 = len("</div>]")
    for i in range(df.shape[0]):
        df['userReview'][i] = df['userReview'][i][len_del_1:-len_del_2]

    bow_transformer = CountVectorizer(analyzer=text_process).fit(df['userReview'])
    max_features = len(bow_transformer.vocabulary_)

    movieid_encoded = movie_id_process(df['movieId'])

    review_train, review_test, label_train, label_test = train_test_split(df['userReview'], movieid_encoded,
                                                                          test_size=0.2)

    review_train_bow = bow_transformer.transform(review_train)
    review_test_bow = bow_transformer.transform(review_test)

    model = LSTM_model()
    model.build(embedding_feature=32, output_dim=5, hidden_dim=32)
    model.train(review_train_bow, label_train, epochs=10, batch_size=128, split=0.2)

    predictions = model.predict(review_test_bow, label_test)
