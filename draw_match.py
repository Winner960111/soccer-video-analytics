import cv2
import pandas as pd

from inference import Converter, HSVClassifier, NNClassifier, YoloV5, hsv_classifier
from inference.filters import filters
from run_utils import classify_city_gk, get_player_detections
from soccer import Ball, Match, Player, Team

classifier = NNClassifier(
    model_path="models/model_classification.pt",
    classes=["Chelsea", "Man City", "Referee"],
)

hsv_classifier = HSVClassifier(filters=filters)
person_detector = YoloV5()
ball_detector = YoloV5(model_path="models/best.pt")

man_city = Team(name="Man City", abbreviation="MNC", color=(255, 165, 0))
chelsea = Team(name="Chelsea", abbreviation="CHE", color=(255, 0, 0))
teams = [man_city, chelsea]

match = Match(home=chelsea, away=man_city)
match.team_possession = man_city

frame = cv2.imread("images/city_gk_vs_referee.png")

# Players
player_detections = get_player_detections(person_detector, hsv_classifier, frame)
player_detections = hsv_classifier.predict_from_detections(
    detections=player_detections, img=frame
)
classify_city_gk(player_detections)
players = Player.from_detections(detections=player_detections, teams=teams)

# Ball
ball_df = ball_detector.predict(frame)
ball_detections = Converter.DataFrame_to_Detections(ball_df)
ball = Ball(ball_detections[0]) if ball_detections else None
if ball:
    ball.set_color(match)

# Match
match.update(players, ball)

# Draw
frame = Player.draw_players(players=players, frame=frame, confidence=False)
frame = ball.draw(frame)
frame = match.draw(frame, debug=False)

# Write img
cv2.imwrite("match.png", frame)
