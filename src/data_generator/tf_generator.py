"""
 Copyright (C) 2020  Argonne, Hariharan Devarajan <hdevarajan@anl.gov>
 This file is part of DLProfile
 DLIO is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as
 published by the Free Software Foundation, either version 3 of the published by the Free Software Foundation, either
 version 3 of the License, or (at your option) any later version.
 This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
 warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.
 You should have received a copy of the GNU General Public License along with this program.
 If not, see <http://www.gnu.org/licenses/>.
"""

from src.data_generator.data_generator import DataGenerator
from numpy import random

from src.utils.utility import progress
from shutil import copyfile

"""
Generator for creating data in TFRecord format.
"""
class TFRecordGenerator(DataGenerator):
    def __init__(self):
        super().__init__()

    def generate(self):
        import tensorflow as tf
        """
        Generator for creating data in TFRecord format of 3d dataset.
        """
        super().generate()
        record = random.random((self._dimension, self._dimension))
        record_label = 0
        prev_out_spec =""
        count = 0
        for i in range(0, int(self.num_files)):
            if i % self.comm_size == self.my_rank:
                progress(i+1, self.num_files, "Generating TFRecord Data")
                out_path_spec = "{}_{}_of_{}.tfrecords".format(self._file_prefix, i, self.num_files)
                # Open a TFRecordWriter for the output-file.
                if count == 0:
                    prev_out_spec = out_path_spec
                    with tf.io.TFRecordWriter(out_path_spec) as writer:
                        for i in range(0, self.num_samples):
                            img_bytes = record.tostring()
                            data = {
                                'image': tf.train.Feature(bytes_list=tf.train.BytesList(value=[img_bytes])),
                                'label': tf.train.Feature(int64_list=tf.train.Int64List(value=[record_label]))
                            }
                            # Wrap the data as TensorFlow Features.
                            feature = tf.train.Features(feature=data)
                            # Wrap again as a TensorFlow Example.
                            example = tf.train.Example(features=feature)
                            # Serialize the data.
                            serialized = example.SerializeToString()
                            # Write the serialized data to the TFRecords file.
                            writer.write(serialized)
                    count += 1
                else:
                    copyfile(prev_out_spec, out_path_spec)
