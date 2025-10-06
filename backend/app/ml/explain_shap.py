# backend/app/ml/explain_shap.py
import shap
import joblib

rf = joblib.load("models/rf_model.pkl")
X_train = joblib.load("models/X_train.pkl")  # save X_train after preprocessing

explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_train)

# Save explainer
joblib.dump(explainer, "models/shap_explainer.pkl")
