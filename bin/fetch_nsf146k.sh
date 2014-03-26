#!/bin/bash

if [ $# -ge 1 ]
then
	DEMO_PATH=$1
else
	DEMO_PATH=data/demo/nsf146k
fi
DOWNLOAD_PATH=$DEMO_PATH/download
CORPUS_PATH=$DEMO_PATH/corpus

echo "# Setting up the NSF dataset..."

if [ ! -d "$CORPUS_PATH" ]
then
	echo "    Creating folder '$DEMO_PATH'..."
	mkdir -p data
	mkdir -p data/demo
	mkdir -p $DEMO_PATH

	if [ ! -e "$DEMO_PATH/questionable-to-delete.txt" ]
	then
		echo "After a model is imported into a Termite Data Server, you can technically delete all content in this folder without affecting the server. However you may wish to retain these files to track provenance and for other analysis purposes." > $DEMO_PATH/questionable-to-delete.txt
	fi

	if [ ! -d "$DOWNLOAD_PATH" ]
	then
		echo "    Creating folder '$DOWNLOAD_PATH'..."
		mkdir -p $DOWNLOAD_PATH
		echo "    Downloading..."
		curl --insecure --location http://homes.cs.washington.edu/~jcchuang/misc/files/nsf146k.zip > $DOWNLOAD_PATH/nsf146k.zip
		echo "    Corpus has been downloaded to '$DOWNLOAD_PATH'."
	else
		echo "    Already downloaded: $DOWNLOAD_PATH"
	fi

	echo "    Creating folder '$CORPUS_PATH'..."
	mkdir -p $CORPUS_PATH
	echo "    Uncompressing..."
	unzip -q $DOWNLOAD_PATH/nsf146k.zip -d $CORPUS_PATH
	echo "    Corpus is now available at '$CORPUS_PATH'."
else
	echo "    Already available: $CORPUS_PATH"
fi

echo
