from vid_converter import VideoConverter
import os


def test_split_and_convert():
    input_dir = "data/fullvids/wetlab1.mp4"
    vc = VideoConverter(f"{os.getcwd()}/{input_dir}")
    output_dir = "test_storage"
    vc.split_and_convert(output_dir)


if __name__ == "__main__":
    test_split_and_convert()
