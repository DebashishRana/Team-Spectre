import os
from pathlib import Path
from typing import Dict

import cv2
import joblib
import numpy as np
from skimage.feature import hog

from config import settings


class DocumentClassifier:
    def __init__(self) -> None:
        self._model = None
        self._scaler = None
        self._pca = None
        self._loaded = False

    def _artifact_dirs(self) -> list[Path]:
        candidates = []
        if settings.AADHAAR_MODEL_DIR:
            candidates.append(Path(settings.AADHAAR_MODEL_DIR))

        base_dir = Path(__file__).resolve().parent
        candidates.extend(
            [
                base_dir / "models",
                base_dir / "app" / "models",
                Path(r"D:\Python\Infosys\main\backend\app\models"),
            ]
        )

        return candidates

    def _load(self) -> None:
        if self._loaded:
            return

        for model_dir in self._artifact_dirs():
            ensemble_path = model_dir / "document_classifier_ensemble.pk"
            scaler_path = model_dir / "scaler.joblib"
            pca_path = model_dir / "pca.joblib"

            if ensemble_path.exists() and scaler_path.exists() and pca_path.exists():
                self._model = joblib.load(ensemble_path)
                self._scaler = joblib.load(scaler_path)
                self._pca = joblib.load(pca_path)
                self._loaded = True
                return

        raise FileNotFoundError(
            "Model artifacts not found. Set AADHAAR_MODEL_DIR or place artifacts in backend/models or backend/app/models."
        )

    def classify_image_path(self, image_path: str) -> Dict:
        self._load()

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not read uploaded image")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (128, 128))

        features = hog(
            resized,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            visualize=False,
        ).reshape(1, -1)

        features_scaled = self._scaler.transform(features)
        features_pca = self._pca.transform(features_scaled)

        probabilities = self._model.predict_proba(features_pca)[0]
        label_index = int(np.argmax(probabilities))
        confidence = float(probabilities[label_index])

        label = "Aadhar" if label_index == 1 else "Non-Aadhar"

        return {
            "label": label,
            "confidence": confidence,
            "passed": label == "Aadhar" and confidence >= settings.AADHAAR_CLASSIFIER_THRESHOLD,
            "threshold": settings.AADHAAR_CLASSIFIER_THRESHOLD,
        }
