#!/bin/sh

predicted=$1
gold=$2
predictedEncoding=$3
goldEncoding=$4

jarpath="target/score_paper_segmentation-1.0-SNAPSHOT-jar-with-dependencies.jar"

java -Xmx4G -cp $jarpath edu.umass.cs.iesl.score_paper_segmentation.Scorer $predicted $gold $predictedEncoding $goldEncoding