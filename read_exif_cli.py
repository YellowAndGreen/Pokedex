#!/usr/bin/env python3
import exifread
import sys
import argparse


def print_exif_data(image_path: str):
    """
    Opens an image file, extracts EXIF data using exifread, and prints all tags.

    Args:
        image_path (str): The path to the image file.
    """
    try:
        with open(image_path, "rb") as f:
            tags = exifread.process_file(f)

        if not tags:
            print(f"No EXIF metadata found in {image_path}")
            return

        print(f"EXIF data for: {image_path}\n----------------------------")
        for tag_name, value in tags.items():
            # MakerNote tags can be very verbose and often not human-readable directly
            if tag_name == "EXIF MakerNote":
                print(
                    f"{tag_name}: [MakerNote data, often binary, not fully displayed]"
                )
            elif tag_name in ["JPEGThumbnail", "TIFFThumbnail"]:
                print(f"{tag_name}: [Thumbnail data not displayed]")
            else:
                try:
                    # Attempt to get a printable representation
                    printable_value = value.printable
                    # If the value has a list of components, show them
                    if (
                        hasattr(value, "values")
                        and isinstance(value.values, list)
                        and len(value.values) > 1
                    ):
                        print(
                            f"{tag_name} ({value.field_type}): {value.values} (Printable: '{printable_value}')"
                        )
                    else:
                        print(f"{tag_name} ({value.field_type}): {printable_value}")
                except AttributeError:
                    print(f"{tag_name}: {str(value)}")
        print("----------------------------")

    except FileNotFoundError:
        print(f"Error: File not found at {image_path}", file=sys.stderr)
    except IsADirectoryError:
        print(
            f"Error: Expected a file, but {image_path} is a directory.", file=sys.stderr
        )
    except Exception as e:
        print(f"An error occurred while processing {image_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read and print EXIF data from an image file."
    )
    parser.add_argument("image_path", type=str, help="Path to the image file.")

    args = parser.parse_args()

    print_exif_data(args.image_path)

"""
How to use:
1. Save this script as read_exif_cli.py in your project root (e.g., illustrated-photo-library/read_exif_cli.py).
2. Make sure you have the exifread library installed in your Python environment:
   pip install exifread
3. Run from the terminal:
   python read_exif_cli.py path/to/your/image.jpg
   python read_exif_cli.py path/to/your/image.png

Example:
   python read_exif_cli.py pokedex_backend/tests/assets/test_image.png
   python read_exif_cli.py some_other_image_with_exif.jpg
"""
