from argparse import ArgumentParser
import time
from kerasOCR import kerasOCR
#from call_api import call_function

def buildingArguments():
    parser = ArgumentParser()
    #parser.add_argument('configRecModel', help='Config file for recognition kerasOCR model')
    #parser.add_argument('configDetModel', help='Config file for detection kerasOCR model')
    parser.add_argument('inputdirectory', help='Directory with the image(s) you want to use for testing')
    parser.add_argument('inputImgsDir', help='Directory with the originals image(s)')
    parser.add_argument('outputdirectory', help='Directory where you want to save the testing result image(s)')
    parser.add_argument('labelFile', help='File ground truth')
    parser.add_argument('coordinatesTextDirectory', help='Directory with all the files with the coordinates of the text')
    parser.add_argument('--starttime', default='0' , help='Start time for ocr process')
    parser.add_argument('--outputprefix', default='output-', help='Prefix that will be aded to the original image(s) name on the final result (kerasOCR)')
    parser.add_argument('--device', default='cuda:1', help='Device used for inference')
    return parser.parse_args()

def main():
    args = buildingArguments()
    start_time = time.time()
    kerasOCR(args, start_time)

    print("Finalizada la ejecucion de kerasOCR")

if __name__ == '__main__':
    main()
