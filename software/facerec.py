import cv2
import os
import imgutils
import numpy

class FaceRecognizer(object):

    def __init__(self, algorithm, confidence_threshold):
        
        self.cascade_face = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_alt.xml")
        
        if algorithm == 'eigen' or algorithm == 'fisher' or algorithm == 'lbph':
            self.algorithm = algorithm;
        else:
            self.algorithm = 'fisher'
        
        self.threshold = confidence_threshold;
        
        if self.algorithm == 'eigen':
            self.recognizer = cv2.createEigenFaceRecognizer(threshold=self.threshold);
        elif self.algorithm == 'fisher':
            self.recognizer = cv2.createFisherFaceRecognizer(threshold=self.threshold);
        elif self.algorithm == 'lbph':
            self.recognizer = cv2.createLBPHFaceRecognizer(threshold=self.threshold);
        
        self.names = []

    
    def add(self, name, number_of_captures):
    
        if os.path.exists('faces/'):
            current = len([x for x in os.listdir('faces/') if os.path.isdir(os.path.join('faces/', x))])
        else:
            os.mkdir('faces/')
            current = 0
            
        os.mkdir('faces/s'+str(current))
        
        video_capture = cv2.VideoCapture(0)
        images = []
        while len(images) < number_of_captures:
            ret, frame = video_capture.read()
            (faces, frame) = imgutils.detect_pattern(frame, self.cascade_face, (75,75))
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cropped_frame = frame[y:h, x:w]
                    cropped_frame = imgutils.resize(cropped_frame, 128, 128)
                    images.append(cropped_frame)
                cv2.imshow('Capturing...', cropped_frame)
                cv2.waitKey(10)
        video_capture.release()
        cv2.destroyAllWindows()
        for i in range(len(images)):
            cv2.imwrite('faces/s'+str(current)+'/'+str(i)+'.jpg', images[i])
        
        namefile = open('faces/names', 'a+')
        namefile.write(name+'\n')
        namefile.close()
    
    
    def update(self, name, number_of_captures, new_name=None):
        
        if os.path.exists('faces/'):
        
            if new_name == None: new_name = name
        
            with open('faces/names') as namefile:
               names = namefile.read().splitlines()
            try: face_id = names.index(name)
            except ValueError:
                print "ERROR: Cannot update a face for a name not in database"
                return -1
            names[face_id] = new_name
            with open('faces/names', 'w') as namefile:
               namefile.write("\n".join(names))
        
            count = len([name for name in os.listdir('faces/') if os.path.isdir(os.path.join('faces/', name))])
            if face_id < count:
                current = face_id
                video_capture = cv2.VideoCapture(0)
                images = []
                while len(images) < number_of_captures:
                    ret, frame = video_capture.read()
                    (faces, frame) = imgutils.detect_pattern(frame, self.cascade_face, (75,75))
                    if len(faces) > 0:
                        for (x, y, w, h) in faces:
                            cropped_frame = frame[y:h, x:w]
                            cropped_frame = imgutils.resize(cropped_frame, 128, 128)
                            images.append(cropped_frame)
                        cv2.imshow('Capturing...', cropped_frame)
                        cv2.waitKey(10)
                video_capture.release()
                cv2.destroyAllWindows()
                for i in range(len(images)):
                    cv2.imwrite('faces/s'+str(current)+'/'+str(i)+'.jpg', images[i])
            else: print "ERROR: The face id does not exist in database"
        else:
            print "ERROR: There are no faces in database"
    
    
    def get_database(self, path):
    
        if not path.endswith('/'): path = path + '/'
    
        ids = os.listdir(path)
        images = []
        labels = []
        
        namefile = open(path+'names', 'r')
        names = namefile.read().splitlines()
        namefile.close()
        
        for id in ids:
            if os.path.isdir(path+id):
                pics = os.listdir(path+id)
                for pic in pics:
                    if pic.endswith('jpg'):
                        image = cv2.imread(path+id+'/'+pic)
                        (face, image) = imgutils.detect_pattern(image, self.cascade_face, (50,50))
                        for (x,y,w,h) in face:
                            image_crop = image[y:h, x:w]
                            image_crop = imgutils.resize(image_crop, 64, 64)
                            image_crop = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
                            images.append(image_crop)
                            labels.append(int(id[1:]))
        return images, labels, names


    def train_model(self, databasepath, modelpath):
    
        if not modelpath.endswith('/'): modelpath = modelpath + '/'
    
        if os.path.exists(databasepath):

            print "Training", self.algorithm, "model..."
            
            images, labels, names = self.get_database(databasepath)
    
            if self.algorithm == 'eigen':
        
                self.recognizer.train(images, numpy.array(labels))
                self.recognizer.save(modelpath+'model-eigen')
            
            elif self.algorithm == 'fisher':
            
                self.recognizer.train(images, numpy.array(labels))
                self.recognizer.save(modelpath+'model-fisher')
            
            elif self.algorithm == 'lbph':
            
                self.recognizer.train(images, numpy.array(labels))
                self.recognizer.save(modelpath+'model-lbph')
            
            namefile = open(modelpath+'names-'+self.algorithm, 'w')
            namefile.write('\n'.join(names))
            namefile.close()
            self.names = names;

            print "Finished training", self.algorithm, "model."
            
        else:
            
            print "ERROR: Specified path does not exist"
        
    
    def load_model(self, modelpath):
    
        if not modelpath.endswith('/'): modelpath = modelpath + '/'
    
        namefile = open(modelpath+'names-'+self.algorithm, 'r')
        names = namefile.read().splitlines()
        namefile.close()
    
        if self.algorithm == 'eigen':
        
            if os.path.exists(modelpath+'model-eigen'):
                self.recognizer.load(modelpath+'model-eigen')
            else: print "ERROR: No model found"
        
        elif self.algorithm == 'fisher':
        
            if os.path.exists(modelpath+'model-fisher'):
                self.recognizer.load(modelpath+'model-fisher')
            else: print "ERROR: No model found"
        
        elif self.algorithm == 'lbph':
        
            if os.path.exists(modelpath+'model-lbph'):
                self.recognizer.load(modelpath+'model-lbph')
            else: print "ERROR: No model found"
        
        self.names = names;
    
    
    def update_model(self):
    
        pass
        
    
    def recognize(self, image, search_for_faces=True, write_names_on_image=True):
        
        faces = []
        found = []
        confs = []
        
        if search_for_faces:
            (faces, image) = imgutils.detect_pattern(image, self.cascade_face, (64,64))
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    name = ""
                    image_crop = image[y:h, x:w]
                    image_crop = imgutils.resize(image_crop, 64, 64)
                    image_crop = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
                    id_predicted, conf = self.recognizer.predict(image_crop)
                    confs.append(conf)
                    cv2.putText(image, str(conf)[:5], (w-25, h+12), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255))
                    if id_predicted > -1 and write_names_on_image:
                        cv2.putText(image, self.names[id_predicted], (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255))
                        found.append(self.names[id_predicted])
                    else: 
                        cv2.putText(image, 'Unknown', (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255))
                        found.append('Unknown')
            image = imgutils.box(faces, image)
            
            if len(faces) > 0: decision = True
            else: decision = False
            
            return image, faces, found, confs, decision
        
