import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
from pyspark.sql.functions import col
from pyspark.sql import SparkSession
from datetime import timedelta
from datetime import datetime
from statistics import mean
from pathlib import Path
import sys
import csv
import re

# Define the emoji sentiment mapping
emoji_sentiments = {
    "😊": "positive",
    "🤤": "positive",
    "😝": "positive",
    "😀": "positive",
    "😄": "positive",
    "😏": "positive",
    "😉": "positive",
    "🤣": "positive",
    "😂": "positive",
    "😁": "positive",
    "🤓": "positive",
    "🙂": "positive",
    "🥰": "positive",
    "😍": "positive",
    "🧐": "positive",
    "🤗": "positive",
    "😎": "positive",
    "🥳": "positive",
    "😄": "positive",
    "😉": "positive",
    "😃": "positive",
    "😇": "positive",
    "🤡": "positive",
    "😢": "negative",
    "😭": "negative",
    "😞": "negative",
    "😔": "negative",
    "😤": "negative",
    "🤬": "negative",
    "🥶": "negative",
    "🥺": "negative",
    "🤢": "negative",
    "😡": "negative",
    "🤮": "negative",
    "😫": "negative",
    "😩": "negative",
    "😐": "neutral",
    "😳": "neutral",
    "😬": "neutral",
    "😮": "neutral",
    "🥴": "neutral",
    "😵": "neutral",
    "😪": "neutral",
    "🤔": "neutral",
    "🤨": "neutral",
    "🙄": "neutral",
    "👋": "positive",
    "👏🏾": "positive",
    "🐕": "neutral",
    "😸": "positive",
    "💓": "positive",
    "❤️": "positive",
    "💙": "positive",
    "❣️": "positive",
    "💖": "positive",
    "♥️": "positive",
    "🧡": "positive",
    "💙": "positive",
    "💚": "positive",
    "💕": "positive",
    "💗": "positive",
    "💜": "positive",
    "💔": "negative",
    "⭐️": "positive",
    "🙏": "neutral",
    "🙏🏾": "neutral",
    "🎊": "positive",
    "👩🏿‍🦰": "neutral",
    "🎉": "positive",
    "👻": "positive",
    "🎃": "positive",
    "💀": "neutral",
    "😿": "negative",
    "🍬": "positive",
    "🍫": "positive",
    "🍭": "positive",
    "👩🏼‍🏫": "neutral",
    "👨🏽‍🏫": "neutral",
    "🎒": "neutral",
    "📓": "neutral",
    "✏️": "neutral",
    "⚠️": "neutral",
    "🧹": "neutral",
    "🧼": "neutral",
    "🧺": "neutral",
    "🧽": "neutral",
    "🏡": "neutral",
    "🧽": "neutral",
    "🧺": "neutral",
    "🧼": "neutral",
    "👍": "positive",
    "✌️": "positive",
    "🙌🏽": "positive",
    "🤱": "positive",
    "👍🏼": "positive",
    "✌🏼": "positive",
    "👇": "neutral",
    "🙅": "negative",
    "🤷": "neutral",
    "🤷🏼‍♀️": "neutral",
    "🙋‍♀️": "neutral",
    "🤦": "negative",
    "🤦": "negative",
    "🍺": "neutral",
    "🍻": "neutral",
    "🚗": "neutral",
    "🚕": "neutral",
    "🐒": "neutral",
    "⭐": "positive",
    "💲": "positive",
    "🍪": "positive",
    "👩🏼‍🎓": "neutral",
    "👨🏾‍🎓": "neutral",
    "🤰🏽": "neutral",
    "☀️": "neutral",
    "👊🏽": "neutral",
    "✅": "neutral",
    "💫": "neutral",
    "👀": "neutral",
    "☎️": "neutral",
    "💦": "neutral",
    "💥": "neutral",
    "🐣": "neutral",
    "🐇": "neutral",
    "🐓": "neutral",
    "🔥": "neutral",
    "🐈‍⬛": "neutral",
    "⛱️": "neutral",
    "🌊": "neutral",
    "🍔": "neutral",
    "🐕‍🦺": "neutral",
    "🚜": "neutral",
    "🐛": "neutral",
    "🦟": "neutral",
    "🌳": "neutral",
    "🍂": "neutral",
    "🌾": "neutral",
    "🌻": "neutral",
    "💭": "neutral",
    "💡": "neutral",
    "✨": "neutral",
    "🌍": "neutral",
    "💉": "neutral",
    "⛄️": "neutral",
    "☃️": "neutral",
    "❄️": "neutral",
    "🎄": "neutral",
    "🌲": "neutral",
    "💐": "neutral",
    "🐔": "neutral",
    "🐾": "neutral",
    "🌸": "neutral",
    "📍": "neutral",
    "🛌": "neutral",
    "📐": "neutral",
    "📱": "neutral",
    "📧": "neutral",
    "🖥️": "neutral",
    "🎨": "neutral",
    "👑": "neutral",
    "🧼": "neutral",
    "💪": "neutral",
    "🍁": "neutral",
    "🌾": "neutral",
    "🌳": "neutral",
    "🏡": "neutral",
    "🎁": "positive",
    "🚨": "neutral",
    "🔴": "neutral",
    "🍀": "neutral",
    "⚡️": "neutral",
    "🩺": "neutral",
    "⚕️": "neutral",
    "💊": "neutral",
    "🔹": "neutral",
    "✈️": "neutral",
    "🔨": "neutral",
    "⏳": "neutral",
    "🌿": "neutral",
    "💃🏻": "neutral",
    "🍓": "neutral",
    "🐶": "neutral",
    "🃏": "neutral",
    "📿": "neutral",
    "🌧️": "neutral",
    "🕯️": "neutral",
    "🍂": "neutral",
    "🗞": "neutral",
    "🍅": "neutral",
    "🎶": "neutral",
    "🐻": "neutral",
    "👇🏼": "neutral",
    "🌺": "neutral",
    "🩸": "neutral",
    "❌": "neutral",
    "🌹": "neutral",
    "🌠": "neutral",
    "🤯": "neutral",
    "😱": "neutral",
    "👗": "neutral",
    "🍗": "neutral",
    "🥗": "neutral",
    "✍️": "neutral"
}
sid = SentimentIntensityAnalyzer()
spark = SparkSession.builder.appName("post_analyzer").getOrCreate()

# Define the preprocess function to replace emojis with sentiment labels
def preprocess(text):
    for emoji, sentiment in emoji_sentiments.items():
        text = re.sub(emoji, sentiment, text)
    return text

def analyze(posts_df):
    posts_pandas = posts_df.toPandas()
    scores_list = []
    for index, row in posts_pandas.iterrows():
        post_text = row["post_text"]
        if post_text != None:
            processed = preprocess(post_text)
            try:
                score = sid.polarity_scores(processed)['compound']
            except Exception as e:
                print(str(e))
                print(row)
                quit(1)
            bonus = 0.01*int(row["likes"].replace(",","")) + 0.03*int(row["comments"].replace(",",""))

            if score > 0: score += bonus
            else: score -= bonus 
            scores_list.append(score)

    return mean(scores_list)

def load_data(path_to_data_file:str):
    return spark.read.csv(path_to_data_file, header=True, inferSchema=True)

def normalize(scores_dict, desired_range):
    shift_by = min(scores_dict.values())
    if -1*max(scores_dict.values()) < shift_by: shift_by = -1*max(scores_dict.values())
    shifted_dict = {key: val - shift_by for key, val in scores_dict.items()}
    values = shifted_dict.values()
    max_val = max(values)
    min_val = min(values)
    d_range = max_val - min_val
    
    normalized_dict = {key: ((val - min_val) / d_range * desired_range + min_val) for key, val in shifted_dict.items()}
    return normalized_dict

def analyze_posts(neighborhood_file, posts_file, output_dir):
    output_file = output_dir+"/town_scores_temp.csv"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    neighborhoods = load_data(neighborhood_file)
    posts = load_data(posts_file)

    towns = neighborhoods.drop_duplicates(["town"]).select("town").toPandas()
    town_posts = neighborhoods.join(posts, neighborhoods.neighborhood == posts.neighborhood, "inner")\
        .select(neighborhoods.town, posts.post_text, posts.likes, posts.comments)

    with open(output_file, "a", newline='') as t:
        writer = csv.writer(t)
        writer.writerow(["town","score","number_of_posts"])

    for index, row in towns.iterrows():
        town = row["town"]
        try:
            posts_df = town_posts.filter(col("town") == town)
            num_posts = posts_df.count()
            if num_posts > 0:
                score = analyze(posts_df)
            else:
                continue
            
            with open(output_file, "a", newline='') as t:
                writer = csv.writer(t)
                writer.writerow([town,score,num_posts])
            if index%1000 == 0:
                print("[" + datetime.now().strftime("%H:%M:%S") + "] Completed: " + str(index+1) + " out of " + str(towns.count()["town"]))
        except Exception as e:
            with open(output_dir+"/log.txt", "a") as log:
                log.write("[" + datetime.now().strftime("%H:%M:%S") + "] Error analyzing town: " + town + "\n" + str(e))
                print("[" + datetime.now().strftime("%H:%M:%S") + "] " + str(e))
    return output_file

def star_fills(score):
    stars = [0]*5
    for i in range(5):
        if score >= (i+1):
            stars[i] = 100
        else:
            stars[i] = (score-i) * 100
            break
            
    return stars

def resident_satisfaction(town_score_file, output_dir):
    rows = []
    total_posts = 0
    scores_dict = {}
    with open(town_score_file, "r") as t:
        reader = csv.reader(t)
        next(reader)
        for row in reader:
            if row[1] == 'n/a':
                scores_dict[row[0]] = 0.0
                total_posts += float(row[2])
                row.append(0)
                rows.append(row)
            else:
                scores_dict[row[0]] = float(row[1])
                total_posts += float(row[2])
                row.append(1)
                rows.append(row)
    normalized_scores = normalize(scores_dict, 5.0)

    with open(output_dir+"/town_resident_satisfaction_scores.csv", "w", newline='') as s:
        writer = csv.writer(s)
        writer.writerow(["town", "state","sentiment_score","number_of_posts", "satisfaction_score", "star_fill","x", "y", "score_valid"])
        for i, row in enumerate(rows):
            town_split = row[0].split(",")
            norm_score = round(normalized_scores[row[0]],1)
            if norm_score > 5: norm_score = 5
            elif norm_score < 0 or row[1] == 'n/a': norm_score = 0
            stars = star_fills(norm_score)
            writer.writerow([town_split[0], town_split[1], row[1], row[2], norm_score, stars[0], 1, 1, row[-1]])
            writer.writerow([town_split[0], town_split[1], row[1], row[2], norm_score, stars[1], 2, 1, row[-1]])
            writer.writerow([town_split[0], town_split[1], row[1], row[2], norm_score, stars[2], 3, 1, row[-1]])
            writer.writerow([town_split[0], town_split[1], row[1], row[2], norm_score, stars[3], 4, 1, row[-1]])
            writer.writerow([town_split[0], town_split[1], row[1], row[2], norm_score, stars[4], 5, 1, row[-1]])

neighborhood_file = sys.argv[1]
posts_file = sys.argv[2]
output_dir = sys.argv[3]

scores_file = analyze_posts(neighborhood_file, posts_file, output_dir)
resident_satisfaction(scores_file, output_dir)

