import facerec
import sys
mrfaces = facerec.FaceRecognizer('fisher', 100)
mrfaces.add(sys.argv[1], 300)
