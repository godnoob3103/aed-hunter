import os
import csv
from google_images_search import GoogleImagesSearch
import requests
from ultralytics import YOLO

# Set up your Google API credentials
api_key = 'AIzaSyBLfqC0pbLFIqKvnHo18ii-306TZ_9bfFE'
cx = '0302ca633d0644527'
gis = GoogleImagesSearch(api_key, cx)

# List of search queries
search_queries = ['AED ประเทศไทย', 'AED สนามบิน']  # Replace 'Your_second_query' with your actual second query

# Common folder for all images and CSV file
common_folder_path = 'D:/AED hunter/download picture and link/pic and link/common'
if not os.path.exists(common_folder_path):
    os.makedirs(common_folder_path)

# Define the CSV file name
csv_file_path = os.path.join(common_folder_path, 'image_urls_with_detections.csv')

# Initialize CSV file
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['Search Query', 'Image Number', 'Image URL', 'Detections']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()

# Process each search query
for search_query in search_queries:
    query_folder_path = os.path.join(common_folder_path, search_query.replace(" ", "_"))
    folder_with_detections = os.path.join(query_folder_path, 'with_detections')
    folder_without_detections = os.path.join(query_folder_path, 'without_detections')

    # Create directories for the search query
    for folder in [query_folder_path, folder_with_detections, folder_without_detections]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    try:
        # Search for images
        gis.search(search_params={'q': search_query, 'num': 10})
        results = gis.results()

        for i, image in enumerate(results):
            try:
                # Download the image
                response = requests.get(image.url)
                image_filename = f'image_{i+1}.jpg'
                image_path = os.path.join(query_folder_path, image_filename)
                with open(image_path, 'wb') as img_file:
                    img_file.write(response.content)

                # Use YOLO to detect objects
                model = YOLO("/content/best.pt")  # Update the model path if necessary
                results_yolo = model(source=image_path, conf=0.7)

                # Check for detections and move the file to the appropriate folder
                if results_yolo[0]:  # If detections are present
                    detection_status = 1
                    os.rename(image_path, os.path.join(folder_with_detections, image_filename))
                else:
                    detection_status = 0
                    os.rename(image_path, os.path.join(folder_without_detections, image_filename))

                # Write the image information to the CSV file
                with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    csv_writer.writerow({'Search Query': search_query, 'Image Number': i + 1, 'Image URL': image.url, 'Detections': detection_status})

            except Exception as e:
                print(f"Error processing {search_query} - image {i+1}: {e}")

    except Exception as e:
        print(f"Error with {search_query}: {e}")

print(f"All image URLs and detection statuses have been saved to {csv_file_path}")
