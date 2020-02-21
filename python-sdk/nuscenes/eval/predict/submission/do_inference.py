# nuScenes dev-kit.
# Code written by Freddy Boulton, 2020.
"""Script for generating a submission to the nuscenes prediction challenge."""
import argparse
import json
import os
from typing import List

from nuscenes import NuScenes
from nuscenes.eval.common.config import config_factory
from nuscenes.eval.predict.config import PredictionConfig
from nuscenes.eval.predict.data_classes import Prediction
from nuscenes.eval.predict.splits import get_prediction_challenge_split
from nuscenes.predict import PredictHelper
from nuscenes.predict.models.physics import ConstantVelocityHeading


def load_model(helper: PredictHelper, config: PredictionConfig, path_to_model_weights: str):
    """
    Loads model with desired weights
    """
    return ConstantVelocityHeading(config.seconds, helper)


def do_inference_for_submission(helper: PredictHelper,
                                config: PredictionConfig,
                                path_to_model_weights: str,
                                dataset_tokens: List[str]) -> List[Prediction]:
    """
    Currently, this will make a submission with a constant velocity and heading model.
    Fill in all the code needed to run your model on the test set here. You do not need to worry
    about providing any of the parameters to this function since they are provided by the main function below.
    You can test if your script works by evaluating on the val set.
    :param helper: Instance of PredictHelper that wraps the nuScenes test set.
    :param config: Instance of PredictionConfig.
    :param path_to_model_weights: Path to model weights.
    :param dataset_tokens: Tokens of instance_sample pairs in the test set.
    :returns: List of predictions.
    """

    cv_heading = load_model(helper, config, path_to_model_weights)

    cv_preds = []
    for token in dataset_tokens:
        cv_preds.append(cv_heading(token))

    return cv_preds


def main(version: str, data_root: str, split_name: str, model_weights: str,
         output_dir: str, submission_name: str, config_name: str) \
        -> None:
    """
    Makes predictions for a submission to the nuScenes prediction challenge.
    :param version: NuScenes version.
    :param data_root: Directory storing NuScenes data.
    :param split_name: Data split to run inference on.
    :param model_weights: Path to model weights.
    :param output_dir: Directory to store the output file.
    :param submission_name: Name of the submission to use for the results file.
    :param config_name: Name of config file to use.
    """
    nusc = NuScenes(version=version, dataroot=data_root)
    helper = PredictHelper(nusc)
    dataset = get_prediction_challenge_split(split_name)
    config = config_factory(config_name)

    predictions = do_inference_for_submission(helper, config, model_weights, dataset)
    predictions = [prediction.serialize() for prediction in predictions]
    json.dump(predictions, open(os.path.join(output_dir, f"{submission_name}_inference.json"), "w"))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Perform Inference for submission.')
    parser.add_argument('--version', help='NuScenes version number.')
    parser.add_argument('--data_root', help='Root directory for NuScenes json files.')
    parser.add_argument('--split_name', help='Data split to run inference on.')
    parser.add_argument('--model_weights', help='Path to model weights')
    parser.add_argument('--output_dir', help='Directory to store output file.')
    parser.add_argument('--submission_name', help='Name of the submission to use for the results file.')
    parser.add_argument('--config_name', help='Name of the config file to use', default='predict_2020_icra')

    args = parser.parse_args()
    main(args.version, args.data_root, args.split_name, args.model_weights,
         args.output_dir, args.submission_name, args.config_name)