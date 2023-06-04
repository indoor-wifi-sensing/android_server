# android_server


# Flask Server for Location Estimation

This repository contains a Flask server that estimates the location based on the sensing data received from an Android app.

## Purpose

The purpose of this repository is to provide an algorithm that uses various sensing data collected by an Android app to estimate the user's location. The server utilizes a pre-collected database and applies an algorithm to determine the estimated location and provide guidance to the desired destination.

## How It Works

The functionality of the server can be described as follows:

1. **Location Estimation Approach**: The Android app sends Wi-Fi MAC addresses and signal strength to the server. The server's pre-existing database contains information such as location, MAC addresses, and RSS (Received Signal Strength). By comparing the data received from the app with the database, the server estimates the current location. It calculates the accuracy of the estimation based on the collected data. The estimation process continues up to a maximum of 100 iterations or until the accuracy is deemed satisfactory. If the estimation is accurate, the server returns the estimated location. Otherwise, it returns a message stating that the location could not be found.

## Included Files

This repository includes the following files:

- `model.pkl`: A decision tree model used to determine the accuracy of the location estimation.
- `app.py`: The main code that implements the server's algorithm and maps the API endpoints.
- `data` directory: Contains CSV files with pre-collected data for location estimation.
