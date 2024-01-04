from transformers import pipeline

__sentimental_classifier = pipeline(
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", 
    return_all_scores=True
)

def sentimentally_negative_predicts(text: str) -> bool:
    """Predicts if a given text is sentimentally negative.

    Args:
        text (str): Input text.

    Returns:
        bool: Prediction.
    """
    return __sentimental_classifier(text)[0][2]['score'] >= 0.4