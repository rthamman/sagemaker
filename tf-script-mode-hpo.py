import argparse
import numpy as np
import os
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense

tf.logging.set_verbosity(tf.logging.ERROR)

def parse_args():

    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script
    parser.add_argument('--epochs', type=int, default=1)
    parser.add_argument('--batch_size', type=int, default=64)

    # data directories
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--test', type=str, default=os.environ.get('SM_CHANNEL_TEST'))

    # model directory: we will use the default set by SageMaker, /opt/ml/model
    parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_MODEL_DIR'))

    return parser.parse_known_args()


def get_train_data(train_dir):

    x_train = np.load(os.path.join(train_dir, 'x_train.npy'))
    y_train = np.load(os.path.join(train_dir, 'y_train.npy'))
    print('x train', x_train.shape,'y train', y_train.shape)

    return x_train, y_train


def get_test_data(test_dir):

    x_test = np.load(os.path.join(test_dir, 'x_test.npy'))
    y_test = np.load(os.path.join(test_dir, 'y_test.npy'))
    print('x test', x_test.shape,'y test', y_test.shape)

    return x_test, y_test


def get_model():
    x = keras.Input(shape=(11,))
    y = keras.layers.Dense(units=6, kernel_initializer="uniform", activation='relu')(x)
    y = keras.layers.Dense(units=6, kernel_initializer='uniform', activation='relu')(y)
    y = keras.layers.Dense(units=1, kernel_initializer='uniform', activation='sigmoid')(y)
    return keras.Model(x, y)
    


if __name__ == "__main__":

    args, _ = parse_args()

    x_train, y_train = get_train_data(args.train)
    x_test, y_test = get_test_data(args.test)

    model = get_model()

    model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

    model.fit(x_train, y_train,
              batch_size=args.batch_size,
              epochs=args.epochs,
              validation_data=(x_test, y_test))

    # create a TensorFlow SavedModel for deployment to a SageMaker endpoint with TensorFlow Serving
    tf.contrib.saved_model.save_keras_model(model, args.model_dir)
