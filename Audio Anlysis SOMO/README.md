This folder contains:

+ `SOMO.ipynb` is responsible for:
    + Denoising the audio
    + Optinal plot in time and frequency domains
    + Rudimental feature extraction (to be refined and improved)
    + Creation of a csv file containing the alarms event

Note: it's possible to tune the parameters for alarm events' extraction inside the function `get_alarms_and_features_and_plot_spectrograms()`.

+ `Hear_and_label.py` is a rudimental GUI based script that reproduce the audio corresponding to an alarm event and allows the user to label the audio.