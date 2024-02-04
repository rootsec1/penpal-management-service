RUNNING_JOURNAL_INFERENCE_PROMPT = """
{}

The above is some of the activity I've collected about myself for only today. Draw as many insights as you can between these data points. Try to find all kinds of correlations and links to my mood and psychological state.

Given these data points, write a very short journal in a way that sounds cool and authentic. The goal of journaling is to track activities and identify underlying moods and tones. Take on the persona of whomever the data points are about and write a journal while standing in his shoes in first person perspective. If you encounter any technical discrepancies or glitches while processing the data, do not mention it. Refer any names provided above only by their first name in the Journal. Try to frame a story out of it if possible, it does not necessarily need to be extra ordinary.

I've attached the person's call logs, message logs, location and usage activity. The package names are unique identifiers for Android apps on Google play store. Do not get technical. If you encounter geo co-ordinates in the data, do not memtion them in the journal instead reverse geocode them to give a rough estimate and figure out where the person was and connect the story. Do not make any refernces to the word "timestamp", process it and use it in a natural human sounding way in the story. If there is a mention of an app, figure out what the app does and why the person might have used it. The narrative should perfectly fit. Let the journal seem simple and easy going like it's written by a student. Be precise and to the point, do not make the journal long. Strictly do not mention a footer or the phrase "The Person" or the word "Unknown" anywhere.
"""

MERGE_DESC_PROMPT = """
Merge the following content into a single one to make the overall content more coherent, concise, beautiful and eloquent.
Content Piece 1:
{}

Content Piece 2:
{}
"""
