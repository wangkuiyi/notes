import tensorflow_transform as tft
import tensorflow_transform.beam.impl as tft_beam


def main():
    def preprocessing_fn(inputs):
        return {
            'x_centered': x - tft.mean(inputs['x']),
            'y_normalized': tft.scale_to_0_1(inputs['y']),
            's_integerized': tft.compute_and_apply_vocabulary(inputs['s'])
        }

    ...
    with tft_beam.Context(temp_dir=tempfile.mkdtemp()):
        transformed_dataset, transform_fn = (
            (raw_data, raw_data_metadata)
            | tft_beam.AnalyzeAndTransformDataset(preprocessing_fn))

    transformed_data, transformed_metadata = transformed_dataset
