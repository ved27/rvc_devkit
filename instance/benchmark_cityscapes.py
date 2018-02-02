import math
import os.path as op
import png
import shutil

from benchmark import *
from dataset_format_kitti2015 import *
from util import *
from util_stereo import *

import numpy as np
import scipy.misc as sp


class Cityscapes(Benchmark):

    def Name(self):
        return 'Cityscapes Instance-Level Semantic Labeling Task'
    
    
    def Prefix(self):
        return 'Cityscapes_'
    
    
    def Website(self):
        return 'https://cityscapes-dataset.com/'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return True
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        input_file_path = op.join(archive_dir_path, 'leftImg8bit_trainvaltest.zip')
        gt_file_path = op.join(archive_dir_path, 'gtFine_trainvaltest.zip')
        expected_archives = [input_file_path, gt_file_path]

        # Try to unpack input and ground truth files
        self.ExtractManualDownloadArchives(expected_archives, op.join(unpack_dir_path, self.Prefix() + 'dirs'))


    def ExtractManualDownloadArchives(self, expected_archives, unpack_dir_path):
        missing_archives = []
        for archive_path in expected_archives:
            if not op.isfile(archive_path):
                missing_archives.append(archive_path)

        # Extract archives
        if not missing_archives:
            for archive_path in expected_archives:
                UnzipFile(archive_path, unpack_dir_path)
        # Report missing files
        else:
            for missing_archive in missing_archives:
                print('ERROR: Could not find: ' + missing_archive)
            print('%s must be downloaded manually. Please register at %s\nto download the data and place it '
                  'according to the path(s) above.' % (self.Prefix()[:-1], self.Website()))
            sys.exit(1)


    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)


    def CityscapesToKitti(self, cs_instance, cs_semantic):
        instance = np.zeros(cs_instance.shape, dtype='int32')
        instance[np.where(cs_instance > 1000)] = 1 + cs_instance[np.where(cs_instance > 1000)] % 1000
        kitti_instance = cs_semantic*256 + instance 
        return kitti_instance

        
    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        img_dir_path = op.join(unpack_dir_path, self.Prefix() + 'dirs', 'leftImg8bit')
        gt_dir_path = op.join(unpack_dir_path, self.Prefix() + 'dirs', 'gtFine')

        # Retrieve the dataset splits (train, test, val)
        splits = [d for d in os.listdir(img_dir_path) if op.isdir(op.join(img_dir_path, d))]

        # Move the training data
        for split in splits:

            # Extract all cities
            city_names = [c for c in os.listdir(op.join(img_dir_path, split)) if op.isdir(op.join(img_dir_path, split, c))]

            for city in city_names:
                city_img_dir_path = op.join(img_dir_path, split, city)
                city_gt_dir_path = op.join(gt_dir_path, split, city)

                # Read the image file names without the prefix
                img_names = ['_'.join(f.split('_')[:3]) for f in os.listdir(city_img_dir_path) if op.isfile(op.join(city_img_dir_path, f))]

                for img_name in img_names:
                    if split == 'test':
                        # Move the test image data
                        shutil.move(op.join(city_img_dir_path, img_name + '_leftImg8bit.png'),
                                    op.join(test_dir_path, 'image_2', self.Prefix() + img_name + '.png'))
                    else:
                        # Move the training image data
                        shutil.move(op.join(city_img_dir_path, img_name + '_leftImg8bit.png'),
                                    op.join(training_dir_path, 'image_2', self.Prefix() + img_name + '.png'))

                        # Convert the instance files to the Kitti2015 format
                        cs_instance = sp.imread(op.join(city_gt_dir_path, img_name + '_gtFine_instanceIds.png'))
                        cs_semantic = sp.imread(op.join(city_gt_dir_path, img_name + '_gtFine_labelIds.png'))
                        kitti_instance = self.CityscapesToKitti(cs_instance, cs_semantic)

                        tgt_file_name = op.join(training_dir_path, 'instance', self.Prefix() + img_name + '.png')
                        sp.toimage(kitti_instance, high=np.max(kitti_instance), low=np.min(kitti_instance), mode='I').save(tgt_file_name)

        shutil.rmtree(op.join(unpack_dir_path, self.Prefix() + 'dirs'))


    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)
    
    
    def CreateSubmission(self, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):
        # FILE STRUCTURE:
        # your_algo_name/pred_list/FILENAME.txt
        # your_algo_name/pred_img/FILENAME_MASKID.png
        
        # Create the archive and clean up.
        archive_filename = ZipDirectory(archive_base_path, pack_dir_path)
        DeleteFolderContents(pack_dir_path)
        
        return archive_filename