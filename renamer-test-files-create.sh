#!/bin/bash

# Directory setup
TARGET_DIR="renamer_test_files"

# Create or clean the target directory
if [ -d "$TARGET_DIR" ]; then
    echo "INFO: Cleaning existing directory $TARGET_DIR"
    rm -rf "$TARGET_DIR"
fi

# Create directory
mkdir -p "$TARGET_DIR"
echo "INFO: Directory $TARGET_DIR created."

# File creation
declare -a FILES=(
    # Original test files
    "periods.in.between.words.(2007).txt"
    "underscores_in_between_words_[1995].txt"
    "hyphens-in-between-words-500MB.txt"
    "periods.in.between.words..jpg"
    "underscores_in_between_words_.jpg"
    "hyphens-in-between-words-.jpg"

    # Files with technical information
    "sample_movie_1080p_bluray_x264_AC3.mkv"
    "music_album_FLAC_320kbps.zip"
    "my_video_clip_4K_HDR_HEVC.mp4"
    "series_episode_01_1080p_WEBRip_x265_AAC.mp4"
    "sample_audio_track_AAC_128kbps.mp3"
    "movie_2001_Directors_Cut_REMUX.mp4"
    "documentary_4K_HDR10_60fps.mkv"
    "old_recording_LQ_256kbps.wav"
    "video_file_HD_Rip_MPEG2.mp4"
    "concert_video_720p_DTS_HD_Audio.m2ts"
)

# Create files in the target directory
for FILE in "${FILES[@]}"; do
    touch "$TARGET_DIR/$FILE"
    echo "INFO: Created file $TARGET_DIR/$FILE"
done

echo "INFO: File creation completed."