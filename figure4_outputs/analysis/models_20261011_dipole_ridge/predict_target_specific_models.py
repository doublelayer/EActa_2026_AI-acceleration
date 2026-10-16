"""Prediction from exported target-specific model states and clean-site inputs."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".model_dependencies"))
import numpy as np
import joblib

from current_site_descriptors import compute
from extended_physical_descriptors import compute as extended_compute


def site_features(source, site):
    return {**compute(source, site), **extended_compute(source, site)}


def load_models(directory=None):
    directory = Path(directory) if directory else HERE / "target_specific_best_models"
    models = {}
    import json
    parameters = json.loads((directory / "model_parameters.json").read_text(encoding="utf-8"))
    for target, model in parameters.items():
        model["state"] = joblib.load(directory / model["state_file"])
        models[target] = model
    return models


def predict(features, model):
    state = model["state"]
    prep, spec, estimator = state["preprocessing"], state["specification"], state["estimator"]
    x = np.asarray([features[f] for f in model["descriptor_keys"]], dtype=float)
    x = np.where(np.isfinite(x), x, prep["median"])
    z = ((x-prep["mean"])/prep["scale"])[None,:]
    if spec["family"] == "ridge":
        normalized = float(z[0] @ estimator["coefficient"])
    elif spec["family"] in ("rbf_ridge", "linear_rbf_ridge"):
        parameters = spec["parameters"]
        support = estimator["support"]
        kernel = np.exp(-np.sum((support-z)**2,axis=1)/(2*parameters["length"]**2))
        kernel += parameters["linear_weight"]*(support@z[0])/z.shape[1]
        normalized = float(kernel @ estimator["dual_coefficient"])
    elif spec["family"] == "shared_kernel_gaussian_process":
        normalized = float(estimator.predict(z)[0,model["target_index"]])
    else:
        normalized = float(np.asarray(estimator.predict(z)).reshape(-1)[0])
    return float(prep["y_mean"] + prep["y_scale"]*normalized)
