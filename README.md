# Score Paper Segmentation #

Building the code:

```
mvn clean package
```

Usage:

```
./bin/score.sh <predicted-directory> <gold-directory> <predicted-file-encoding> <gold-file-encoding> 
```

The two directories must have files with the same base names (extensions are ignored) for the code to work properly. E.g:

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
