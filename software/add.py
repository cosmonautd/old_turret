import facerec
import sys
mrfaces = facerec.FaceRecognizer('fisher')
mrfaces.add(sys.argv[1], 300)
