from flask_restful import Resource
from flask import request
from datetime import datetime

from config import Config

# AWS 의 여러 서비스들을 이용할 수 있는 파이썬 라이브러리
import boto3


class PhotoReviewResource(Resource) :

    def post(self) :

        # 사진이랑 내용은 필수다!!
        
        print(request.files)
        print(request.form)

        # if 'photo' not in request.files :
        #     return {'result':'fail', 'error':'사진은 필수'}
        
        # if 'content' not in request.form :
        #     return {'result':'fail', 'error':'내용은 필수'}

        if 'photo' not in request.files or 'content' not in request.form :
            return {'result':'fail', 'error':'필수항목 확인'}, 400
        
        file = request.files['photo']
        content = request.form['content']
        
        rating = request.form['rating']
        rating = int(rating)

        
        #### S3 저장코드는 동일 ####

        ### content 와 image_url 은 DB에 저장한다.

        # rating 은 0 부터 5까지인데, 
        # 이값을 0~100 사이의 값으로 변경하여,
        # 클라이언트에게 보내시오.

        rating = rating * 20

        return {'rating' : rating}


class PhotoResource(Resource) :

    def post(self) :

        print( request.files )

        # 사진이 필수인 경우의 코드 
        if 'photo' not in request.files : 
            return {'result':'fail', 'error':'파일없음'},400
        
        # 유저가 올린 파일을 변수로 만든다.
        file = request.files['photo']

        # 파일명을 유니크하게 만들어준다.

        current_time = datetime.now()
        print(current_time.isoformat().replace(':','_').replace('.','_')+'.jpg')

        new_filename = current_time.isoformat().replace(':','_').replace('.','_')+'.jpg'

        # 새로운 파일명으로, S3에 파일 업로드 
        try :

            s3 = boto3.client('s3' , 
                     aws_access_key_id = Config.AWS_ACCESS_KEY_ID ,
                     aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
        
            s3.upload_fileobj(file,
                              Config.S3_BUCKET,
                              new_filename,
                              ExtraArgs = {'ACL':'public-read' , 'ContentType':'image/jpeg' } )
            
        except Exception as e:
            print(str(e))
            return {'result':'fail', 'error':str(e)}, 500
        
        # 위에서 저장한 사진의 URL 주소를 
        # DB에 저장해야 한다!

        # URL 주소는 = 버킷명.S3주소/우리가만든파일명 
        file_url = Config.S3_BASE_URL + new_filename


        ### Object Detection 한다.
        ### Rekognition 서비스 이용.
        # 
        #  첫번째 파라미터는 파일명, 두번째 파라미터는 버킷명

        label_list = self.detect_labels( new_filename, Config.S3_BUCKET)
        
                
        # 잘 되었으면, 클라이언트에 데이터를 응답한다. 
        return {'result' : 'success', 'file_url':file_url, 
                'count' : len(label_list), 
                'items' : label_list}


    def detect_labels(self, photo, bucket):

        client=boto3.client('rekognition', 
                            'us-east-1',
                            aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)

        response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
            MaxLabels=10)

        print('Detected labels for ' + photo) 
        print()   

        label_list = []

        for label in response['Labels']:

            label_list.append(label['Name'])

            print ("Label: " + label['Name'])
            print ("Confidence: " + str(label['Confidence']))
            print ("Instances:")
            for instance in label['Instances']:
                print ("  Bounding box")
                print ("    Top: " + str(instance['BoundingBox']['Top']))
                print ("    Left: " + str(instance['BoundingBox']['Left']))
                print ("    Width: " +  str(instance['BoundingBox']['Width']))
                print ("    Height: " +  str(instance['BoundingBox']['Height']))
                print ("  Confidence: " + str(instance['Confidence']))
                print()

            print ("Parents:")
            for parent in label['Parents']:
                print ("   " + parent['Name'])
            print ("----------")
            print ()
        return label_list
