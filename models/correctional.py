from sklearn.feature_extraction.text import TfidfVectorizer
import re
from nltk.stem import WordNetLemmatizer
from sklearn.tree import DecisionTreeClassifier
import pickle

# Load model
f = open("pickles/correctional_model.pickle", "rb")
model:DecisionTreeClassifier = pickle.loads(f.read())
f.close()

# Load vectorizer
f = open("pickles/vectorizer.pickle", "rb")
vectorizer:TfidfVectorizer = pickle.loads(f.read())
f.close()

lemmatizer = WordNetLemmatizer()

def __prepare_text(original: str):
    """Prepares a text for a model input by cutting, lemmatizing, then vectorizing.

    Args:
        original (str): Original text to be translated.

    Returns:
        spmatrix: Output matrix for prediction input.
    """
    text = original.lower()
    text = re.sub(r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", text)
    text = " ".join([lemmatizer.lemmatize(word) for word in text.split()])
    vectorized_text = vectorizer.transform([__prepare_text(text)])
    return vectorized_text

def correctional_predicts(text: str) -> bool:
    """Predicts if a given text is correctional.

    Args:
        text (str): Input text.

    Returns:
        bool: Prediction.
    """
    return not int(model.predict(__prepare_text(text))[0]) == 0