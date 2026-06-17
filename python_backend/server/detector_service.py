from predict import predict_image


def detect_tiger(image_path):
    result, confidence = predict_image(image_path)

    return {
        "result": result,
        "confidence": float(confidence),
        "is_tiger": result == "Tiger"
    }