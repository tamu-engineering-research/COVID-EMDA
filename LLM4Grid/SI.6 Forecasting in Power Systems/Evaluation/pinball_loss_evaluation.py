import numpy as np
import pandas as pd


def pinball_loss(y_true, y_pred, quantile):
    """
    Calculate the Pinball Loss for a single quantile.

    :param y_true: The true value.
    :param y_pred: The predicted value.
    :param quantile: The quantile tau, a value between 0 and 1.
    :return: Pinball Loss for the quantile.
    """
    if y_true >= y_pred:
        error = (y_true - y_pred) * quantile
    else:
        error = (y_pred-y_true) * (1-quantile)
    return error


def pinball_loss_over_quantiles(y_true, y_preds, quantiles,n_timesteps,n_quantiles):
    """
    Calculate the averaged Pinball Loss over multiple quantiles.

    :param y_true: Array of true values (n_timesteps,).
    :param y_preds: Array of predicted values (n_timesteps, n_quantiles).
    :param quantiles: List or array of quantile values.
    :return: Averaged Pinball Loss over all quantiles and timesteps.
    """

    pl = 0
    for t in range(n_timesteps):
        for q in range(n_quantiles):
            pl += pinball_loss(y_true[t], y_preds[t], quantiles[q])

    return pl / (n_timesteps * n_quantiles)


csv_file_path = '../Test_results/GEF_2014_forecast_result.csv'
# Example usage
n_quantiles = 99  # Replace with your actual number of quantiles

data_array = np.genfromtxt(csv_file_path, delimiter=',')
# Example true values and predictions
y_true = data_array[78937:,2]
y_preds = data_array[78937:,4]
  # Replace with actual true values

n_timesteps = y_true.shape[0]  # Replace with your actual number of timesteps
# Replace with actual predictions

# Quantiles from 0.01 to 0.99
quantiles = np.linspace(0.01, 0.99, n_quantiles)

# Calculate the averaged Pinball Loss
average_pl = pinball_loss_over_quantiles(y_true, y_preds, quantiles,n_timesteps,n_quantiles)
print("Averaged Pinball Loss:", average_pl)
