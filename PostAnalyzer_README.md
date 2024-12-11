Post Analyzer
================

### Overview

This Python script is designed to analyze posts from a social network and calculate a sentiment score for each town based on the posts. The script utilizes the NLTK library for sentiment analysis and Apache Spark for data processing.

### Requirements

* Python 3.8+
* NLTK
* pyspark
* statistics
* pathlib
* csv
* re
* sys

### Usage

1. Install required libraries: `pip install -r requirements.txt`
2. Download the NLTK VADER lexicon: `python -m nltk.downloader vader_lexicon`
3. Prepare the input data:
	* `neighborhoods.csv`: a CSV file containing neighborhood metadata (neighborhood, town, state)
	* `posts.csv`: a CSV file containing post data (post_text, likes, comments)
4. Run the script: `python post_analyzer.py neighborhoods.csv posts.csv output_dir`

### Parameters

* `neighborhoods.csv`: Path to the CSV file containing neighborhood metadata
* `posts.csv`: Path to the CSV file containing post data
* `output_dir`: Directory for output files

### Output

The script generates two output files:

* `town_scores_temp.csv`: a temporary CSV file containing town scores
* `town_resident_satisfaction_scores.csv`: a CSV file containing resident satisfaction scores for each town

### Notes

* The script uses a custom emoji sentiment mapping to replace emojis in post text with sentiment labels.
* The script uses the NLTK VADER sentiment analyzer to calculate sentiment scores for each post.
* The script uses Apache Spark to process large datasets efficiently.
* The script normalizes sentiment scores to a range of 0-5 for easier interpretation.

### Future Development

* Improve the custom emoji sentiment mapping to include more emojis and nuances.
* Integrate with other data sources or APIs to enrich the analysis.
* Develop a more sophisticated sentiment analysis model to capture subtle variations in sentiment.