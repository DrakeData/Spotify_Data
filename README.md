![spotify_logo](images/spotify_logo3.png)

# Sportify Data API Webscrape
This project is to use Spotify API endpoints to pull back personal user data.

## Table of Contents (Coming Soon)

## Description
"Spotify is a digital music, podcast, and video streaming service that gives you access to millions of songs and other content from artists all over the world." - [Spotify](https://support.spotify.com/us/using_spotify/getting_started/what-is-spotify/)

As an avid user of Spotify for over 10 year and a proud premium subscriber, I though it would be interesting to see my music taste/trends with the data that Spotify has on their back end. This project will be pulling my personal data from Spotify's API Endpoints and perform analysis on it. The project will also provide instruction on how you can pull your own Spotify data.

## Project Goal and High-Level Overview
This project will pull your most recently played tracks and your top 50 tracks from the past 6 months. The script will gather the data using Spotify's API and export the results in an excel file.

## Project Discovery & Project Decision to Support the Project Goals
Coming soon
## Tech/Framework Used

### Coding Language
- Python v3.7

### Programs
- [Jupyter Notebook](https://jupyter.org/) - Markdown
- [PyCharm](https://www.jetbrains.com/pycharm/) - Integrated Development Environment (IDE)

## Main Files in Repository
- README.md - Markdown of projects
- config.py - Contains Spotify API credentials
- Spotify_Data_Scrape.ipynb - Jupyter Notebook for automated code.
- requirements.txt - version of python libraries used.

## Getting Access
You will need:
1. Your Client ID
2. Your Client Secret
3. Your personal username
3. Register a Redirect URI
4. Your auth_token

### How to get access to Spotify API
See [this documentation](https://docs.google.com/document/d/1jyA7lVMDGPY58dkp6uqyZzQIvDeGvZ6be5VlswqpvPg/edit?usp=sharing) on how to get access to Spotify's API.

## FAQ
**Q. What should I do when client script errors?**
<br/>
A. The Spotify API could be potentially down; wait 1 hour and try again.
<br/>
<br/>
**Q. What happens if Spotify notifies me that API endpoints are changing?**
<br/>
A. This will require repointing and testing.
All API points are covered in this documentation.
Updating of the endpoints and the retesting of the script will need to take place.
<br/>
<br/>
**Q. What happens if I were to delete the python script?**
<br/>
A. The script is centrally managed via GitHub, in which it tracks version control and can be referenced to restore any scripts used for the project.

## Helpful Links
- [Spotify Web API - Authorization Guide](https://developer.spotify.com/documentation/general/guides/authorization-guide/): Details on gaining access to the API.
- [Spotify API References](https://developer.spotify.com/documentation/web-api/reference/object-model/): A full list of the objects returned by the endpoints of the Spotify Web API.

## Repository Information
Created Date: 08/03/2020 <br/>
Created By: [Nick Drake](mailto:nick@drakedata.io) <br/>
