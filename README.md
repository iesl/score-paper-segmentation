# Score Paper Segmentation #

This project is used to measure the accuracy of PDF text extraction methods. Specifically, it is used to measure how well the extractors can determine the header, body and references of scientific papers. 

The extractions which are evaluated are plain text with the following format:

```
#Header
<title, authors, abstract>

#Body
<text>

#References
<citations>

```

The evaluation between a predicted labeling of the sections and the gold labeling of the sections is done by first computing the set of bigrams in each section. The Jaccard Similarity is computed between the predicted and gold bigrams for each section. The Jaccard Similarity between two sets A and B is defined as :

```
J(A,B) = | A intersect B | / | A union B |
```

The evaluation over a group of documents is done by measuring the average Jaccard for each section (header, body, references).


## Building the code ##

The scorer is written in Scala. We use Maven to compile the package:

```
mvn clean package
```

## Usage ##

The following shell script is used to score groups of files. The usage of the shell script is:

```
./bin/score.sh <predicted-directory> <gold-directory> <predicted-file-encoding> <gold-file-encoding> 
```

The two directories must have the following format. The two directories must have files with the same base names (extensions are ignored) for the code to work properly. E.g:

```
<Pred>
abc.svg.txt
efg.svg.txt
```

```
<Gold>
abc.xml.txt
efg.xml.txt
```
