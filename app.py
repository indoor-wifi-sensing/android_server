import json
import math
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/api', methods=['POST'])
def handle_request():
    # 모델 불러오기
    model = joblib.load('model.pkl')
    data = request.get_json()  # JSON 데이터를 파싱합니다.

    wifi_data = json.loads(data['data'])  # JSON 형식의 문자열을 Python 리스트로 변환
    wifi_data = [item for item in wifi_data if all(item)]  # 모든 부분이 None이 아닌 엔트리만 선택
    for wifi in wifi_data[0:7]:
        output_str = f"{wifi[0]},"
        output_str += ",".join(wifi[1:8]) if len(wifi) >= 8 else ",".join(wifi[1:])
        print(output_str)


    pred = 0
    count_num = 0
    while (count_num < 5):
        i = 0
        if pred == 1:
            break
        for wifi in wifi_data:
            wifi_data[i][1] = int(wifi[1]) - 1
            i += 1

        df = pd.read_csv('data/data.csv')

        pos = df.iloc[0]['pos']
        disList = []
        disPos = []
        dis_detail_list = [[]]  # dis_detail_list 초기화
        count = 0
        num = 0
        disPos.append(pos)  # disPos 리스트를 초기화하고 첫 번째 값을 추가

        for _, wifi in df.iterrows():
            if wifi['pos'] is None:
                break
            if wifi['pos'] != pos:
                if disList:  # disList가 비어있지 않으면 제곱근 계산 및 값 추가
                    disList[count] = disList[count] / num
                    num = 0
                    count += 1
                pos = wifi['pos']
                disPos.append(pos)  # 새로운 위치 정보를 추가
                disList.append(0)  # disList에 새로운 위치의 초기값 0 추가
                dis_detail_list.append([])  # 새로운 위치에 대한 dis_detail_list 초기화
            num += 1
            check_pos = 0
            for chose_wifi in wifi_data:
                mac = chose_wifi[0]
                if mac == wifi['mac']:
                    a = int(wifi['rss']) - int(chose_wifi[1])
                    a = a * a
                    a = math.sqrt(a)
                    if disList:  # disList가 비어있지 않으면 값 추가
                        disList[count] += a
                        dis_detail_list[count].append(a)
                    else:  # disList가 비어있으면 초기값 설정
                        disList.append(a)
                        dis_detail_list[count].append(a)
                    check_pos = 1
                    break
            
            if check_pos == 0:
                a = int(wifi['rss'])
                a = a * a
                a = math.sqrt(a)
                if disList:  # disList가 비어있지 않으면 값 추가
                    disList[count] += a
                    dis_detail_list[count].append(a)
                else:  # disList가 비어있으면 초기값 설정
                    disList.append(a)
                    dis_detail_list[count].append(a)
        
        if disList:  # 마지막 위치의 제곱근 계산
            disList[count] = disList[count] / num
        
        min_distance = disList[0]
        min_index = 0
        for i in range(len(disList)):
            if disList[i] == 0:
                break
            if disList[i] < min_distance:
                min_distance = disList[i]
                min_index = i
        
        values = dis_detail_list[min_index]

        sample_df = pd.DataFrame({
            'tar': [disPos[min_index]],
            'dif1': [0],
            'dif2': [0],
            'dif3': [0],
            'dif4': [0],
            'dif5': [0],
            'dif6': [0],
            'dif7': [0],
            'dist': [min_distance]
        })

        if len(values) >= 7:
            sample_df['dif1'] = values[0]
            sample_df['dif2'] = values[1]
            sample_df['dif3'] = values[2]
            sample_df['dif4'] = values[3]
            sample_df['dif5'] = values[4]
            sample_df['dif6'] = values[5]
            sample_df['dif7'] = values[6]
        elif len(values) == 6:
            sample_df['dif1'] = values[0]
            sample_df['dif2'] = values[1]
            sample_df['dif3'] = values[2]
            sample_df['dif4'] = values[3]
            sample_df['dif5'] = values[4]
            sample_df['dif6'] = values[5]
        elif len(values) == 5:
            sample_df['dif1'] = values[0]
            sample_df['dif2'] = values[1]
            sample_df['dif3'] = values[2]
            sample_df['dif4'] = values[3]
            sample_df['dif5'] = values[4]

        sample_df_values = sample_df.values[0]
        output_str = f"{sample_df_values[0]},"
        output_str += ",".join(str(int(x)) for x in sample_df_values[1:8])
        output_str += f",{round(sample_df_values[8], 2)}"
        print("tar  dif1  dif2  dif3  dif4  dif5  dif6  dif7      dist")
        print(output_str)

        X_new = sample_df[['tar', 'dif1', 'dif2', 'dif3', 'dif4', 'dif5', 'dif6', 'dif7', 'dist']]

        # 학습 데이터로부터 더미 변수 컬럼 생성
        train_data = pd.read_csv('data/iot_data.csv')
        train_X = train_data[['tar', 'dif1', 'dif2', 'dif3', 'dif4', 'dif5', 'dif6', 'dif7', 'dist']]
        train_X = pd.get_dummies(train_X)
        dummy_columns = train_X.columns.tolist()

        # 새로운 데이터에 더미 변수 컬럼 추가
        X_new = pd.get_dummies(X_new)
        X_new = X_new.reindex(columns=dummy_columns, fill_value=0)

        # 예측
        y_pred_new = model.predict(X_new)

        # 예측 결과 확인
        print("Prediction:", y_pred_new)
        pred = y_pred_new
        count_num += 1

    # if (pred == [0]):
    #     disPos[min_index] = 'cannot find your position'

    # 요청 데이터 처리 및 응답 생성
    response = {'message': 'Hello, Android!', 'received_data': disPos[min_index]}

    print(disPos[min_index])
    print(response)

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
