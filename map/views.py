from django.shortcuts import render
from django.conf import settings
import pandas as pd
import json
import os

def get_theaters_data():
    # CSV 파일 경로 수정
    csv_path = os.path.join(settings.BASE_DIR, 'static', 'data/facility_details_20241110_180514.csv')
    
    print(f"Looking for CSV file at: {csv_path}")  # 파일 경로 확인
    
    try:
        if not os.path.exists(csv_path):
            print(f"CSV file not found at: {csv_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
        df = pd.read_csv(csv_path)
        print(f"Successfully read CSV file. Found {len(df)} rows")  # 데이터 확인
        
        theater_list = []
        for _, row in df.iterrows():
            try:
                theater = {
                    'mt10id': str(row['mt10id']),
                    'fcltynm': str(row['fcltynm']),
                    'adres': str(row['adres'])
                }
                theater_list.append(theater)
            except KeyError as e:
                print(f"Missing column in CSV: {e}")
                continue
            except Exception as e:
                print(f"Error processing row: {e}")
                continue

        print(f"Processed {len(theater_list)} theaters")  # 처리된 데이터 확인
        
        return {
            'kakao_map_api_key': settings.KAKAO_MAP_API_KEY,
            'theaters': json.dumps(theater_list, ensure_ascii=False)
        }

    except Exception as e:
        print(f"Error in get_theaters_data: {e}")
        return {
            'kakao_map_api_key': settings.KAKAO_MAP_API_KEY,
            'theaters': '[]'
        }

def theater_map_view(request):
    context = get_theaters_data()
    return render(request, 'map/theater_map.html', context)