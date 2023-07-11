"""
vid_converter.py

This module has the code to convert input video files into a specified audio file.

NOTE: This module only does flac conversion at the moment, and needs to be
      updated to handle other conversion types

Created: 07/11/2023
"""

import ffmpeg
import os


# TODO this does not allow for any other type of audio conversion other than .flac.
#      Further implementation is required

class VideoConverter:
    """ Converts video inputs into specified audio format"""

    def __init__(self, input_dir):
        """ Constructor

            Args:
                input_dir   (string): input file path for video that we want to convert
        """
        self.cwd = os.getcwd()

        if not os.path.isfile(input_dir):
            raise Exception("Error: Cannot validate existence of {}".format(input_dir))
        self.input_dir = input_dir


    def generateAudio(self, output_dir, codec="flac", quiet=True):
        """
            Converts our video into specified audio format

        Args:
            output_dir  (string): output file path to save audio file to
            codec       (string): type of encoding for the audio file
            quiet       (bool): controls ffmpeg's console output
                                    True: silence output
                                    False: allow output to print

        Return:
            None

        """

        {
            ffmpeg.input(self.input_dir)
            .output(output_dir, acodec=codec)
            .run(quiet=quiet)
        }
