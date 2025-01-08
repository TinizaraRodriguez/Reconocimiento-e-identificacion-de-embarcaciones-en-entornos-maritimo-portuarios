from argparse import ArgumentParser
import time
from mix_clip import mixnet_clip4str
#from call_api import call_function

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def buildingArguments():
    parser = ArgumentParser()
    parser.add_argument('inputdirectory', help='Directory with the image(s) you want to use for testing')
    parser.add_argument('inputImgsDir', help='Directory with the originals image(s)')
    parser.add_argument('outputdirectory', help='Directory where you want to save the testing result image(s)')
    parser.add_argument('labelFile', help='File ground truth')
    parser.add_argument('coordinatesTextDirectory', help='Directory with all the files with the coordinates of the text')
    parser.add_argument('--starttime', default='0' , help='Start time for ocr process')
    parser.add_argument('--outputprefix', default='output-', help='Prefix that will be aded to the original image(s) name on the final result')
    parser.add_argument('--device', default='cuda:1', help='Device used for inference')
    parser.add_argument('--configDetModel', default='/OCR/MixNet/MixNet_FSNet_M_622.pth', help='Weight file for MixNet model')
    parser.add_argument('--configRecModel', default='/OCR/CLIP4STR/clip4str_base16x16_d70bde1f2d.ckpt',help='Weight file for Clip4str model')
    

    # basic opts
    parser.add_argument('--exp_name', default="TD500HUST", type=str, choices=['Synthtext', 'Totaltext', 'Ctw1500','Icdar2015', 'Totaltext_mid', 'Ctw1500_mid','TD500HUST_mid','ArT_mid', "MLT2017", 'TD500HUST', "MLT2019", "ArT", "ALL","preSynthMLT","preALL"], help='Experiment name')
    parser.add_argument('--resume', default=None, type=str, help='Path to target resume checkpoint')
    parser.add_argument('--num_workers', default=0, type=int, help='Number of workers used in dataloading')
    parser.add_argument('--cuda', default=True, type=str2bool, help='Use cuda to train model')
    parser.add_argument('--mgpu', action='store_true', help='Use multi-gpu to train model')
    parser.add_argument('--save_dir', default='./model/', help='Path to save checkpoint models')
    parser.add_argument('--vis_dir', default='./vis/', help='Path to save visualization images')
    parser.add_argument('--log_dir', default='./logs/', help='Path to tensorboard log')
    parser.add_argument('--loss', default='CrossEntropyLoss', type=str, help='Training Loss')
    parser.add_argument('--pretrain', default=False, type=str2bool, help='Pretrained AutoEncoder model')
    parser.add_argument('--verbose', '-v', default=True, type=str2bool, help='Whether to output debug info')
    parser.add_argument('--viz', action='store_true', help='Whether to output debug info')

    # train opts
    parser.add_argument('--max_epoch', default=250, type=int, help='Max epochs')
    parser.add_argument('--lr', '--learning-rate', default=1e-3, type=float, help='initial learning rate')
    parser.add_argument('--lr_adjust', default='fix', choices=['fix', 'poly'], type=str, help='Learning Rate Adjust Strategy')
    parser.add_argument('--stepvalues', default=[], nargs='+', type=int, help='# of iter to change lr')
    parser.add_argument('--weight_decay', '--wd', default=0., type=float, help='Weight decay for SGD')
    parser.add_argument('--gamma', default=0.1, type=float, help='Gamma update for SGD lr')
    parser.add_argument('--momentum', default=0.9, type=float, help='momentum')
    parser.add_argument('--batch_size', default=6, type=int, help='Batch size for training')
    parser.add_argument('--optim', default='Adam', type=str, choices=['SGD', 'Adam'], help='Optimizer')
    parser.add_argument('--save_freq', default=5, type=int, help='save weights every # epoch')
    parser.add_argument('--display_freq', default=10, type=int, help='display training metrics every # iter')
    parser.add_argument('--viz_freq', default=50, type=int, help='visualize training process every # iter')
    parser.add_argument('--log_freq', default=10000, type=int, help='log to tensorboard every # iterations')
    parser.add_argument('--val_freq', default=1000, type=int, help='do validation every # iterations')

    # backbone
    parser.add_argument('--scale', default=1, type=int, help='prediction on 1/scale feature map')
    parser.add_argument('--net', default='FSNet_M', type=str, choices=["FSNet_M", "FSNet_S","FSNet_hor"], help='Network architecture')
    parser.add_argument('--mid', default=False, type=str2bool, help='midline predict to Transformer')
    parser.add_argument('--embed', default=False, type=str2bool, help='predict embeding value for training')
    parser.add_argument('--know', default=False, type=str2bool, help='Knowledge Distillation')
    parser.add_argument('--onlybackbone', default=False, type=str2bool, help='skip the Transformer block, only train the FSNet. ')
        
    # data args
    parser.add_argument('--load_memory', default=False, type=str2bool, help='Load data into memory')
    parser.add_argument('--rescale', type=float, default=255.0, help='rescale factor')
    parser.add_argument('--input_size', default=960, type=int, help='model input size')
    parser.add_argument('--test_size', default=[960, 960], type=int, nargs='+', help='test size')

    # eval args00
    parser.add_argument('--checkepoch', default=1070, type=int, help='Load checkpoint number')
    parser.add_argument('--start_epoch', default=0, type=int, help='start epoch number')
    parser.add_argument('--cls_threshold', default=0.875, type=float, help='threshold of pse')
    parser.add_argument('--dis_threshold', default=0.35, type=float, help='filter the socre < score_i')

    # demo args
    parser.add_argument('--img_root', default=None,   type=str, help='Path to deploy images')
    
    return parser.parse_args()
    

def main():
    args = buildingArguments()
    start_time = time.time()
    mixnet_clip4str(args, start_time)

    print("Finalizada la ejecucion de Mixnet en conjunto con Clip4str")

if __name__ == '__main__':
    main()
